#!/usr/bin/env bash
# lib/json-escape.sh — sourced, not run: defines `json_escape_string`.
#
# json_escape_string <out-var> <string> — write the JSON-escaped content of <string>, without
# surrounding quotes, into the caller's variable named <out-var>, byte for byte what python's
# `json.dumps` emits. Well-formed UTF-8 input is assumed.
#
# hazard: LC_ALL=C is forced for the call, since under a UTF-8 locale `${s:i:1}` steps by character, not byte.
# hazard: `(( … ))` as a command returns 1 on a zero result, so counters are advanced by assignment.
json_escape_string() {
  local -n _json_escape_out="$1"
  local LC_ALL=C
  local s="$2" out="" i=0 len byte c esc

  len=${#s}
  while (( i < len )); do
    c="${s:i:1}"
    printf -v byte '%d' "'$c"
    byte=$(( byte & 0xFF ))

    case "$byte" in
      34) out+='\"' ;;
      92) out+='\\' ;;
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
          local nbytes cp k cont cbyte
          if   (( (byte & 0xE0) == 0xC0 )); then nbytes=2; cp=$(( byte & 0x1F ))
          elif (( (byte & 0xF0) == 0xE0 )); then nbytes=3; cp=$(( byte & 0x0F ))
          elif (( (byte & 0xF8) == 0xF0 )); then nbytes=4; cp=$(( byte & 0x07 ))
          else                                   nbytes=1; cp=$byte
          fi
          for (( k=1; k<nbytes; k++ )); do
            cont="${s:$((i+k)):1}"
            printf -v cbyte '%d' "'$cont"
            cbyte=$(( cbyte & 0xFF ))
            cp=$(( (cp << 6) | (cbyte & 0x3F) ))
          done
          if (( cp <= 0xFFFF )); then
            printf -v esc '\\u%04x' "$cp"
            out+="$esc"
          else
            local n2 hi lo
            n2=$(( cp - 0x10000 ))
            hi=$(( 0xD800 | (n2 >> 10) ))
            lo=$(( 0xDC00 | (n2 & 0x3FF) ))
            printf -v esc '\\u%04x\\u%04x' "$hi" "$lo"
            out+="$esc"
          fi
          i=$(( i + nbytes - 1 ))
        fi
        ;;
    esac
    i=$(( i + 1 ))
  done

  _json_escape_out="$out"
}
