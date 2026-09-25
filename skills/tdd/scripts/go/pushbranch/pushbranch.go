// Package pushbranch is the Go port of push-branch.sh: copy the run's branch to the remote
// from the worktree it runs in, retrying an unreachable origin with a doubling backoff,
// exiting 1 on a non-fast-forward rejection and recording either failure through event.sh.
//
// Everything that starts a process or waits on a clock goes through Deps, so a unit test
// runs Run in-process with function values in place of git, sleep and event.sh. The
// production Deps (ProcessDeps) keep the script's contract literally: `sleep` is a process
// found on PATH — not time.Sleep — because the integration suite observes the backoff by
// putting a `sleep` stub first on PATH, and git is whatever `git` PATH resolves to.
package pushbranch

import (
	"fmt"
	"io"
	"os"
	"os/exec"
	"path/filepath"
	"strconv"
	"strings"
)

// Deps are the seams a test replaces. Every string a git call returns has its trailing
// newlines stripped, the way bash's `$(...)` strips them.
type Deps struct {
	// Git runs `git args...`. With combined true, stderr is merged into the returned output
	// (the script's `2>&1`); otherwise stderr passes through to the process's own stderr.
	// ok is whether git exited 0.
	Git func(combined bool, args ...string) (out string, ok bool)
	// Sleep waits the given number of seconds (passed as the script passes it, verbatim).
	Sleep func(seconds string)
	// Record appends an event through event.sh; a non-nil error means it could not be written.
	Record func(event string, kv ...string) error
	// Getenv is os.LookupEnv or a test's map.
	Getenv func(key string) (string, bool)
	// Stderr is where the script's own lines go.
	Stderr io.Writer
}

func envDefault(getenv func(string) (string, bool), key, def string) string {
	if v, ok := getenv(key); ok {
		return v
	}
	return def
}

func isDigits(s string) bool {
	if s == "" {
		return false
	}
	for i := 0; i < len(s); i++ {
		if s[i] < '0' || s[i] > '9' {
			return false
		}
	}
	return true
}

// Run is the script's main. It returns the exit code.
func Run(d Deps) int {
	retries := envDefault(d.Getenv, "VERI_PUSH_RETRIES", "3")
	backoff := envDefault(d.Getenv, "VERI_PUSH_BACKOFF", "2")
	for _, t := range [][2]string{{"VERI_PUSH_RETRIES", retries}, {"VERI_PUSH_BACKOFF", backoff}} {
		if !isDigits(t[1]) {
			fmt.Fprintf(d.Stderr, "push-branch.sh: %s must be a non-negative integer, got '%s'\n", t[0], t[1])
			return 2
		}
	}
	nRetries, _ := strconv.ParseInt(retries, 10, 64)
	wait, _ := strconv.ParseInt(backoff, 10, 64)

	var attempt int64
	var out string
	for attempt <= nRetries {
		attempt++
		var ok bool
		out, ok = d.Git(true, "push", "--set-upstream", "origin", "HEAD")
		if ok {
			return 0
		}
		if strings.Contains(out, "[rejected]") &&
			(strings.Contains(out, "non-fast-forward") || strings.Contains(out, "fetch first") || strings.Contains(out, "stale info")) {
			branch, _ := d.Git(false, "rev-parse", "--abbrev-ref", "HEAD")
			lsRemote, _ := d.Git(false, "ls-remote", "origin", "refs/heads/"+branch)
			remoteSHA := cutFirstField(lsRemote)
			fmt.Fprintf(d.Stderr, "push rejected (non-fast-forward): origin/%s is at %s\n", branch, remoteSHA)
			if err := d.Record("push-rejected", "remote_sha="+remoteSHA, "error="+out); err != nil {
				return 2
			}
			return 1
		}
		if attempt <= nRetries {
			d.Sleep(strconv.FormatInt(wait, 10))
			wait *= 2
		}
	}
	fmt.Fprintf(d.Stderr, "push-branch.sh: push failed after %d attempts; the branch is not on the remote\n", attempt)
	if err := d.Record("push-failed", "error="+out, "attempts="+strconv.FormatInt(attempt, 10)); err != nil {
		return 2
	}
	return 0
}

// cutFirstField is `cut -f1` over the captured output, then `$(...)`'s trailing-newline strip.
func cutFirstField(s string) string {
	if s == "" {
		return ""
	}
	lines := strings.Split(s, "\n")
	for i, l := range lines {
		if j := strings.IndexByte(l, '\t'); j >= 0 {
			lines[i] = l[:j]
		}
	}
	return strings.TrimRight(strings.Join(lines, "\n"), "\n")
}

// ProcessDeps are the real thing: git and sleep from PATH, event.sh beside the scripts.
// scriptsDir is where event.sh lives — the directory of the .sh entry points.
func ProcessDeps(scriptsDir string) Deps {
	return Deps{
		Git: func(combined bool, args ...string) (string, bool) {
			cmd := exec.Command("git", args...)
			var b []byte
			var err error
			if combined {
				b, err = cmd.CombinedOutput()
			} else {
				cmd.Stderr = os.Stderr
				b, err = cmd.Output()
			}
			return strings.TrimRight(string(b), "\n"), err == nil
		},
		Sleep: func(seconds string) {
			cmd := exec.Command("sleep", seconds)
			cmd.Stdout, cmd.Stderr = os.Stdout, os.Stderr
			_ = cmd.Run()
		},
		Record: func(event string, kv ...string) error {
			cmd := exec.Command(filepath.Join(scriptsDir, "event.sh"), append([]string{event}, kv...)...)
			cmd.Stdout, cmd.Stderr = os.Stdout, os.Stderr
			return cmd.Run()
		},
		Getenv: os.LookupEnv,
		Stderr: os.Stderr,
	}
}
