# lib/json-escape.sh — sourced, not run: `json_escape_string`, the one place a string
# becomes the escaped JSON-string content `event.sh` writes (issue #290).
#
# Perf: event.sh used to hand its whole line to `python3 -c '... json.dumps(line) ...'`
# purely for this — escaping is the one thing plain string concatenation cannot do safely,
# since a payload holds a verifier's reason with quotes and backslashes in it, or a
# newline. Forking an interpreter for that, three to five times per supervision
# (supervise.sh's launch/retry/exit marks plus harvest-usage.sh's usage mark, all through
# event.sh), was ~45 ms of interpreter start paid before any work, several hundred times in
# a multi-step run. This is the same escaping done in bash instead — the interpreter start
# is not amortised, it is removed.
#
# `json_escape_string <out-var> <string>` writes the JSON-escaped CONTENT of <string> — no
# surrounding quotes — into the caller's variable named by <out-var>, e.g.
# `json_escape_string esc "$s"; line="\"$esc\""`  is the full JSON string literal for `$s`.
# A nameref output rather than a printed one a caller captures with `$(...)`: event.sh calls
# this eight-plus times per line (once per fixed key, once per `key=value` payload
# argument), and a command substitution forks a subshell per call — cheap next to python3,
# but not free, and not this issue's to reintroduce for a different reason than the one it
# started with.
#
# It matches `json.dumps(s)` (python's default: `ensure_ascii=True`, no caller here ever
# passes otherwise) byte for byte, proven in json-escape.test.sh against a live python3
# rather than by inspection:
#   - `"` and `\` escape to `\"` and `\\`.
#   - `\b` `\f` `\n` `\r` `\t` escape to those two-character forms.
#   - every other byte below 0x20, and 0x7f (DEL — outside python's `' '..'~'` printable
#     range, the boundary `py_encode_basestring_ascii`'s own regex draws), escapes to
#     `\u00XX` (lowercase hex, matching python's `'{:04x}'.format`).
#   - a byte 0x80 or above is read as the LEAD byte of a UTF-8 sequence, decoded to its
#     Unicode code point, and escaped as `\uXXXX` — or, for a code point above 0xFFFF (an
#     emoji, past the Basic Multilingual Plane), as the UTF-16 surrogate PAIR python's own
#     `ensure_ascii` emits for one, since JSON strings carry UTF-16 code units and there is
#     no other way to name an astral character while staying ASCII-only.
#   - well-formed UTF-8 in is assumed: argv and env values reaching event.sh are text a
#     model or a caller wrote, never raw invalid bytes, and this does not attempt to
#     replicate python's `surrogateescape` handling of the malformed case.
#
# Operates on RAW BYTES, not locale-aware characters: `LC_ALL=C` is forced for the
# function's own duration (restored on return, `local` unwinds it), so bash's substring
# indexing below (`${s:i:1}`) reads one BYTE per step regardless of the caller's locale —
# under a UTF-8 locale the same indexing would instead walk one multi-byte CHARACTER per
# step, which is the wrong unit for a UTF-8 decoder to drive itself with. `make test`
# already forces `LC_ALL=C` for every suite for an unrelated reason (BSD text tools in a
# UTF-8 locale, CLAUDE.md's "make test on the development Mac"); this does not rely on that
# — a real conductor run invoked from whatever locale the operator's shell carries must
# decode the same way.
json_escape_string() {
  local -n _json_escape_out="$1"
  local LC_ALL=C
  local s="$2" out="" i=0 len byte c esc

  len=${#s}
  while (( i < len )); do
    c="${s:i:1}"
    # The `'` prefix is bash/ksh's own numeric-conversion syntax: `printf '%d' "'$c"` is the
    # ordinal of the FIRST byte of `$c`, which under the forced C locale above is `$c`
    # itself (one byte, since C is a single-byte locale) — not the character's Unicode code
    # point, which is what the same expression would give under a UTF-8 locale instead.
    byte=$(( $(printf '%d' "'$c") & 0xFF ))

    case "$byte" in
      34) out+='\"' ;;                 # "
      92) out+='\\' ;;                 # \
      8)  out+='\b' ;;
      12) out+='\f' ;;
      10) out+='\n' ;;
      13) out+='\r' ;;
      9)  out+='\t' ;;
      *)
        if (( byte < 0x20 || byte == 0x7f )); then
          printf -v esc '\\u%04x' "$byte"
          out+="$esc"
        elif (( byte < 0x80 )); then
          out+="$c"
        else
          # A UTF-8 lead byte: 110xxxxx (2 bytes), 1110xxxx (3), 11110xxx (4). The mask
          # picks off the leading count bits and what is left of the byte is the code
          # point's own top bits; each continuation byte (10xxxxxx) contributes six more.
          local nbytes cp k cont cbyte
          if   (( (byte & 0xE0) == 0xC0 )); then nbytes=2; cp=$(( byte & 0x1F ))
          elif (( (byte & 0xF0) == 0xE0 )); then nbytes=3; cp=$(( byte & 0x0F ))
          elif (( (byte & 0xF8) == 0xF0 )); then nbytes=4; cp=$(( byte & 0x07 ))
          else                                   nbytes=1; cp=$byte
          fi
          for (( k=1; k<nbytes; k++ )); do
            cont="${s:$((i+k)):1}"
            cbyte=$(( $(printf '%d' "'$cont") & 0xFF ))
            cp=$(( (cp << 6) | (cbyte & 0x3F) ))
          done
          if (( cp <= 0xFFFF )); then
            printf -v esc '\\u%04x' "$cp"
            out+="$esc"
          else
            # Astral (beyond the Basic Multilingual Plane): the UTF-16 surrogate pair
            # `ensure_ascii` itself emits for one — there is no single `\uXXXX` for a code
            # point past 0xFFFF, since a JSON string is a sequence of UTF-16 code units.
            local n2 hi lo
            n2=$(( cp - 0x10000 ))
            hi=$(( 0xD800 | (n2 >> 10) ))
            lo=$(( 0xDC00 | (n2 & 0x3FF) ))
            printf -v esc '\\u%04x\\u%04x' "$hi" "$lo"
            out+="$esc"
          fi
          # `i=$(( ... ))` rather than the arithmetic COMMAND `(( i += nbytes - 1 ))`: run
          # as its own statement, the latter's exit status is 1 whenever the RESULT is 0
          # (bash's rule for `((...))` as a command, not an expression) — `nbytes - 1`
          # landing on 0 would make `set -e` read a function that did not fail as one that
          # did. The same trap as the plain `i++` below, and the reason both are assignments.
          i=$(( i + nbytes - 1 ))
        fi
        ;;
    esac
    i=$(( i + 1 ))
  done

  _json_escape_out="$out"
}
