package pushbranch

import (
	"bytes"
	"errors"
	"strings"
	"testing"
)

// fake is the in-process stand-in for git, sleep and event.sh: it records every call as one
// line, the way the bash unit suite's mocked functions appended to a calls file, and answers
// pushes from a script of outcomes.
type fake struct {
	calls     []string
	pushes    []pushOutcome
	branch    string
	lsRemote  string
	recordErr error
	env       map[string]string
	stderr    bytes.Buffer
}

type pushOutcome struct {
	out string
	ok  bool
}

func (f *fake) deps() Deps {
	return Deps{
		Git: func(combined bool, args ...string) (string, bool) {
			f.calls = append(f.calls, "git "+strings.Join(args, " "))
			switch args[0] {
			case "push":
				if len(f.pushes) == 0 {
					return "fatal: unable to access origin", false
				}
				p := f.pushes[0]
				f.pushes = f.pushes[1:]
				return p.out, p.ok
			case "rev-parse":
				return f.branch, true
			case "ls-remote":
				return f.lsRemote, true
			}
			return "", false
		},
		Sleep: func(s string) { f.calls = append(f.calls, "sleep "+s) },
		Record: func(event string, kv ...string) error {
			f.calls = append(f.calls, "record "+event+" "+strings.Join(kv, " "))
			return f.recordErr
		},
		Getenv: func(k string) (string, bool) { v, ok := f.env[k]; return v, ok },
		Stderr: &f.stderr,
	}
}

func assertCalls(t *testing.T, got []string, want ...string) {
	t.Helper()
	if strings.Join(got, "\n") != strings.Join(want, "\n") {
		t.Errorf("calls:\nwant:\n  %s\ngot:\n  %s", strings.Join(want, "\n  "), strings.Join(got, "\n  "))
	}
}

// bash unit case 2: a bad tunable is caught before any push — empty stdout, one exact
// stderr line, exit 2, and no git, sleep or record call.
func TestBadTunableExits2BeforeAnyPush(t *testing.T) {
	for _, bad := range []struct{ key, val string }{{"VERI_PUSH_RETRIES", "x"}, {"VERI_PUSH_BACKOFF", "1.5"}, {"VERI_PUSH_RETRIES", ""}} {
		f := &fake{env: map[string]string{"VERI_PUSH_RETRIES": "0", "VERI_PUSH_BACKOFF": "0"}}
		f.env[bad.key] = bad.val
		code := Run(f.deps())
		want := "push-branch.sh: " + bad.key + " must be a non-negative integer, got '" + bad.val + "'\n"
		if code != 2 || f.stderr.String() != want {
			t.Errorf("%s=%q: want exit 2 and stderr %q, got %d and %q", bad.key, bad.val, want, code, f.stderr.String())
		}
		assertCalls(t, f.calls)
	}
}

// bash unit case 3: with VERI_PUSH_RETRIES=1 and the backoff at its default, a failed push
// is attempted twice with one 2 s wait between, records one push-failed event carrying git's
// output and the attempt count, prints one stderr line, and exits 0.
func TestFailedPushRetriesThenRecordsPushFailed(t *testing.T) {
	f := &fake{env: map[string]string{"VERI_PUSH_RETRIES": "1"}}
	code := Run(f.deps())
	if code != 0 {
		t.Errorf("want exit 0, got %d", code)
	}
	assertCalls(t, f.calls,
		"git push --set-upstream origin HEAD",
		"sleep 2",
		"git push --set-upstream origin HEAD",
		"record push-failed error=fatal: unable to access origin attempts=2")
	if want := "push-branch.sh: push failed after 2 attempts; the branch is not on the remote\n"; f.stderr.String() != want {
		t.Errorf("want stderr %q, got %q", want, f.stderr.String())
	}
}

// integration case 4: VERI_PUSH_RETRIES unset means 3 retries — 4 attempts.
func TestDefaultRetriesIsThree(t *testing.T) {
	f := &fake{env: map[string]string{"VERI_PUSH_BACKOFF": "0"}}
	Run(f.deps())
	n := 0
	for _, c := range f.calls {
		if strings.HasPrefix(c, "git push") {
			n++
		}
	}
	if n != 4 {
		t.Errorf("want 4 push attempts, got %d in %v", n, f.calls)
	}
}

// integration case 6: the wait is VERI_PUSH_BACKOFF seconds doubled per retry — 1, 2, 4 for
// three retries — and none follows the last attempt.
func TestBackoffDoublesPerRetry(t *testing.T) {
	f := &fake{env: map[string]string{"VERI_PUSH_RETRIES": "3", "VERI_PUSH_BACKOFF": "1"}}
	Run(f.deps())
	var sleeps []string
	for _, c := range f.calls {
		if strings.HasPrefix(c, "sleep ") {
			sleeps = append(sleeps, strings.TrimPrefix(c, "sleep "))
		}
	}
	if got := strings.Join(sleeps, " "); got != "1 2 4" {
		t.Errorf("want sleeps '1 2 4', got %q", got)
	}
	if last := f.calls[len(f.calls)-1]; !strings.HasPrefix(last, "record push-failed") {
		t.Errorf("want the last call to be the record, not a sleep after the last attempt; got %q", last)
	}
}

// integration case 5: a blip that clears on the second attempt exits 0 and records nothing.
func TestSecondAttemptLandsQuietly(t *testing.T) {
	f := &fake{env: map[string]string{"VERI_PUSH_BACKOFF": "0"},
		pushes: []pushOutcome{{"fatal: simulated blip", false}, {"", true}}}
	code := Run(f.deps())
	if code != 0 || f.stderr.Len() != 0 {
		t.Errorf("want exit 0 and empty stderr, got %d and %q", code, f.stderr.String())
	}
	assertCalls(t, f.calls, "git push --set-upstream origin HEAD", "sleep 0", "git push --set-upstream origin HEAD")
}

// integration case 9: a push that lands first time exits 0, says nothing, records nothing.
func TestLandedPushIsSilent(t *testing.T) {
	f := &fake{env: map[string]string{}, pushes: []pushOutcome{{"branch set up to track", true}}}
	if code := Run(f.deps()); code != 0 || f.stderr.Len() != 0 {
		t.Errorf("want exit 0 and empty stderr, got %d and %q", code, f.stderr.String())
	}
	assertCalls(t, f.calls, "git push --set-upstream origin HEAD")
}

// integration case 8: a non-fast-forward rejection is attempted once even with retries
// available, exits 1, names the remote sha on stderr, and records push-rejected with it.
func TestNonFastForwardRejectionExits1AfterOneAttempt(t *testing.T) {
	rejected := " ! [rejected]        HEAD -> tdd/232 (non-fast-forward)\nerror: failed to push some refs"
	f := &fake{env: map[string]string{"VERI_PUSH_BACKOFF": "0"},
		pushes:   []pushOutcome{{rejected, false}},
		branch:   "tdd/232",
		lsRemote: "abc123\trefs/heads/tdd/232"}
	code := Run(f.deps())
	if code != 1 {
		t.Errorf("want exit 1, got %d", code)
	}
	assertCalls(t, f.calls,
		"git push --set-upstream origin HEAD",
		"git rev-parse --abbrev-ref HEAD",
		"git ls-remote origin refs/heads/tdd/232",
		"record push-rejected remote_sha=abc123 error="+rejected)
	if want := "push rejected (non-fast-forward): origin/tdd/232 is at abc123\n"; f.stderr.String() != want {
		t.Errorf("want stderr %q, got %q", want, f.stderr.String())
	}
}

// integration case 10: an event that cannot be written is exit 2 on both failing paths.
func TestUnwritableEventExits2(t *testing.T) {
	f := &fake{env: map[string]string{"VERI_PUSH_RETRIES": "0", "VERI_PUSH_BACKOFF": "0"}, recordErr: errors.New("unwritable")}
	if code := Run(f.deps()); code != 2 {
		t.Errorf("unreachable origin: want exit 2, got %d", code)
	}
	f = &fake{env: map[string]string{"VERI_PUSH_RETRIES": "0", "VERI_PUSH_BACKOFF": "0"}, recordErr: errors.New("unwritable"),
		pushes: []pushOutcome{{"! [rejected] x (fetch first)", false}}}
	if code := Run(f.deps()); code != 2 {
		t.Errorf("rejection: want exit 2, got %d", code)
	}
}

func TestCutFirstField(t *testing.T) {
	for in, want := range map[string]string{"": "", "sha\trefs/heads/x": "sha", "sha\trefs/heads/x\n": "sha", "no-tab": "no-tab", "a\tb\nc\td": "a\nc"} {
		if got := cutFirstField(in); got != want {
			t.Errorf("%q: want %q, got %q", in, want, got)
		}
	}
}
