package verdict

import (
	"bytes"
	"strings"
	"testing"
)

// The cases tests/parse-verdict.test.sh pins, run in-process: no shell, no pipe, no fork.
func TestParse(t *testing.T) {
	cases := []struct {
		name string
		code int
		in   string
		out  string
		diag string
	}{
		{"pass with reason", 0,
			"I ran the test and it failed as expected.\nVERDICT: PASS\nREASON: The test fails because slugify is undefined, which is the missing behavior.",
			"The test fails because slugify is undefined, which is the missing behavior.", ""},
		{"reject with reason", 1,
			"VERDICT: REJECT\nREASON: The test asserts on an internal helper, not observable behavior.",
			"The test asserts on an internal helper, not observable behavior.", ""},
		{"malformed no verdict", 2, "I could not make up my mind about this test.", "", "parse-verdict: no VERDICT: line found"},
		{"last verdict wins", 1,
			"My first instinct was VERDICT: PASS but on reflection:\nVERDICT: REJECT\nREASON: The failure is an ImportError from a typo, not the missing behavior.",
			"The failure is an ImportError from a typo, not the missing behavior.", ""},
		{"case insensitive", 0,
			"verdict: pass\nreason: Genuine pass — target test and full suite are green.",
			"Genuine pass — target test and full suite are green.", ""},
		{"indented verdict line", 0, "   VERDICT: PASS\n   REASON: All good.", "All good.", ""},
		{"multiline reason", 1,
			"VERDICT: REJECT\nREASON: Two problems:\n- the test is over-coupled to the implementation\n- it is also far too complex for one criterion",
			"Two problems:\n- the test is over-coupled to the implementation\n- it is also far too complex for one criterion", ""},
		{"reason inline after verdict", 1,
			"VERDICT: REJECT — the test never actually runs the code under test",
			"the test never actually runs the code under test", ""},
		{"unknown verdict word", 2, "VERDICT: MAYBE\nREASON: unsure", "", "parse-verdict: unrecognised verdict word 'MAYBE'"},
		{"fenced verdict block", 1,
			"I ran the test myself.\n```\nVERDICT: REJECT\nREASON: The test asserts a constant and never calls slugify().\n```",
			"The test asserts a constant and never calls slugify().", ""},
		{"multiline reason then fence", 1,
			"VERDICT: REJECT\nREASON: Two problems:\n- vacuous assertion\n- no call to the function\n```",
			"Two problems:\n- vacuous assertion\n- no call to the function", ""},
		{"tilde fence", 1, "VERDICT: REJECT\nREASON: nope\n~~~", "nope", ""},
		{"trailing newline adds no line", 0, "VERDICT: PASS\nREASON: ok\n", "ok", ""},
		{"empty input", 2, "", "", "parse-verdict: no VERDICT: line found"},
		{"empty verdict word", 2, "VERDICT:   ", "", "parse-verdict: unrecognised verdict word ''"},
		{"inline reason beaten by following block", 0, "VERDICT: PASS — inline\nREASON: following", "following", ""},
		{"blank following lines fall back to inline", 0, "VERDICT: PASS — inline\n\n   \n", "inline", ""},
	}
	for _, c := range cases {
		t.Run(c.name, func(t *testing.T) {
			got := Parse(c.in)
			if got.Code != c.code || got.Reason != c.out || got.Diag != c.diag {
				t.Errorf("want code %d reason %q diag %q, got code %d reason %q diag %q", c.code, c.out, c.diag, got.Code, got.Reason, got.Diag)
			}
		})
	}
}

// NEW_STEP: lines before the verdict pair change nothing (#362).
func TestParseNewStepLinesChangeNothing(t *testing.T) {
	plain := "I read the diff against the base sha.\nVERDICT: PASS\nREASON: The transform is behaviour-preserving and the suite is green."
	proposing := "I read the diff against the base sha.\nNEW_STEP: slugify returns an empty string for input that is all separators\nVERDICT: PASS\nREASON: The transform is behaviour-preserving and the suite is green."
	if a, b := Parse(plain), Parse(proposing); a != b {
		t.Errorf("want identical results, got %+v and %+v", a, b)
	}
}

// Main is the CLI shape: reason + newline on stdout for 0/1, diagnostic + newline on stderr
// and an empty stdout for 2.
func TestMain(t *testing.T) {
	var out, errb bytes.Buffer
	if code := Main(strings.NewReader("VERDICT: REJECT\nREASON: r"), &out, &errb); code != 1 || out.String() != "r\n" || errb.Len() != 0 {
		t.Errorf("reject: want (1, %q, %q), got (%d, %q, %q)", "r\n", "", code, out.String(), errb.String())
	}
	out.Reset()
	errb.Reset()
	if code := Main(strings.NewReader("no verdict"), &out, &errb); code != 2 || out.Len() != 0 || errb.String() != "parse-verdict: no VERDICT: line found\n" {
		t.Errorf("malformed: want (2, %q, diag), got (%d, %q, %q)", "", code, out.String(), errb.String())
	}
}
