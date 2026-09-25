// Package verdict is the Go port of parse-verdict.sh: it extracts a blind verifier leaf's
// structured verdict (PASS | REJECT + reason) from the leaf's raw output.
//
// The port mirrors the bash script line for line rather than re-deriving the contract, so
// every quirk the integration suite (tests/parse-verdict.test.sh) pins — the LAST VERDICT:
// line wins, an inline reason after the verdict word, a REASON: label stripped from the
// first following line, a trailing code fence dropped — is reproduced byte for byte.
// Character classes are the C-locale [[:space:]] the suites run under (LC_ALL=C), so a
// non-ASCII whitespace byte is not whitespace here, exactly as it is not for bash then.
package verdict

import (
	"io"
	"strings"
)

// Result is what the script would have answered: Reason goes to stdout followed by a
// newline unless Code is 2, in which case Diag goes to stderr and stdout stays empty.
type Result struct {
	Code   int    // 0 PASS · 1 REJECT · 2 malformed
	Reason string // trimmed reason text, empty when Code is 2
	Diag   string // the stderr diagnostic when Code is 2, without a trailing newline
}

// isSpace is bash's [[:space:]] under LC_ALL=C: space, \t, \n, \v, \f, \r.
func isSpace(b byte) bool {
	return b == ' ' || b == '\t' || b == '\n' || b == '\v' || b == '\f' || b == '\r'
}

func ltrim(s string) string {
	return strings.TrimLeftFunc(s, func(r rune) bool { return r < 0x80 && isSpace(byte(r)) })
}
func rtrim(s string) string {
	return strings.TrimRightFunc(s, func(r rune) bool { return r < 0x80 && isSpace(byte(r)) })
}

// labelTail matches bash's `^[[:space:]]*<LABEL>:[[:space:]]*(.*)$` with a case-insensitive
// label, returning the captured tail (everything after the colon and its whitespace, trailing
// whitespace included) and whether the line matched.
func labelTail(line, label string) (string, bool) {
	s := ltrim(line)
	if len(s) < len(label)+1 || !strings.EqualFold(s[:len(label)], label) || s[len(label)] != ':' {
		return "", false
	}
	return ltrim(s[len(label)+1:]), true
}

// splitLines is the script's `while IFS= read -r line || [[ -n "$line" ]]` loop: lines split
// on \n, a final unterminated line kept, a trailing newline adding no empty line.
func splitLines(input string) []string {
	if input == "" {
		return nil
	}
	lines := strings.Split(input, "\n")
	if lines[len(lines)-1] == "" {
		lines = lines[:len(lines)-1]
	}
	return lines
}

// asciiUpper is `tr '[:lower:]' '[:upper:]'` under LC_ALL=C.
func asciiUpper(s string) string {
	b := []byte(s)
	for i, c := range b {
		if c >= 'a' && c <= 'z' {
			b[i] = c - 'a' + 'A'
		}
	}
	return string(b)
}

// firstToken splits s at its first whitespace byte: `${s%%[[:space:]]*}` and the rest.
func firstToken(s string) (word, rest string) {
	for i := 0; i < len(s); i++ {
		if isSpace(s[i]) {
			return s[:i], s[i:]
		}
	}
	return s, ""
}

// Parse resolves a leaf's raw output to a verdict, reason and exit code.
func Parse(input string) Result {
	lines := splitLines(input)

	vidx := -1
	var tail string
	for i, line := range lines {
		if t, ok := labelTail(line, "VERDICT"); ok {
			vidx, tail = i, t
		}
	}
	if vidx < 0 {
		return Result{Code: 2, Diag: "parse-verdict: no VERDICT: line found"}
	}

	word, inline := firstToken(tail)
	var code int
	switch asciiUpper(word) {
	case "PASS":
		code = 0
	case "REJECT":
		code = 1
	default:
		return Result{Code: 2, Diag: "parse-verdict: unrecognised verdict word '" + asciiUpper(word) + "'"}
	}

	// Inline reason: the verdict line after the word, one leading separator of each kind
	// stripped in this order (the script's `for sep in '—' '–' '-' ':'`).
	inline = ltrim(inline)
	for _, sep := range []string{"—", "–", "-", ":"} {
		inline = strings.TrimPrefix(inline, sep)
	}
	inline = ltrim(inline)

	// Following reason: the lines after the verdict line, a REASON: label stripped from the
	// first, each terminated by \n (the script's `printf -v following '%s\n' "${rest[@]}"`).
	following := ""
	if vidx+1 < len(lines) {
		rest := append([]string(nil), lines[vidx+1:]...)
		if t, ok := labelTail(rest[0], "REASON"); ok {
			rest[0] = t
		}
		following = strings.Join(rest, "\n") + "\n"
	}

	reason := rtrim(following)
	if reason == "" {
		reason = inline
	}
	reason = rtrim(ltrim(reason))

	// A trailing fence-only line (``` or ~~~) is dropped.
	last := reason
	if i := strings.LastIndexByte(reason, '\n'); i >= 0 {
		last = reason[i+1:]
	}
	if isFence(last) {
		if i := strings.LastIndexByte(reason, '\n'); i >= 0 {
			reason = reason[:i]
		} else {
			reason = ""
		}
		reason = rtrim(reason)
	}
	return Result{Code: code, Reason: reason}
}

// isFence is the script's `^[[:space:]]*(```|~~~)[[:space:]]*$`.
func isFence(line string) bool {
	s := rtrim(ltrim(line))
	return s == "```" || s == "~~~"
}

// Main is the CLI: stdin in, reason or diagnostic out, and the exit code returned.
func Main(stdin io.Reader, stdout, stderr io.Writer) int {
	b, err := io.ReadAll(stdin)
	if err != nil {
		io.WriteString(stderr, "parse-verdict: "+err.Error()+"\n")
		return 2
	}
	r := Parse(string(b))
	if r.Code == 2 {
		io.WriteString(stderr, r.Diag+"\n")
		return 2
	}
	io.WriteString(stdout, r.Reason+"\n")
	return r.Code
}
