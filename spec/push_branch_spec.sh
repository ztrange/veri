#shellcheck shell=bash
#
# Port of skills/tdd/scripts/tests/unit/push-branch.test.sh to ShellSpec, for the
# hand-rolled-suites-vs-ShellSpec spike. All 4 cases from the original file, same inputs,
# same expected stdout/stderr/exit code. Not wired into `make test`/`make spec` — this file
# is evidence for the spike's verdict, not an adoption.
#
# Paths are relative to the project root, matching how the task's own invocation
# (`vendor/shellspec/shellspec --shell bash spec/push_branch_spec.sh`) is run: ShellSpec's
# CWD is the project root for the whole run, and nothing here changes it.
PUSH="skills/tdd/scripts/push-branch.sh"
ORIGINAL_SUITE="skills/tdd/scripts/tests/unit/push-branch.test.sh"

# ShellSpec's `Mock` writes a real executable into $SHELLSPEC_MOCK_BINDIR and prepends that
# to PATH (vendor/shellspec/libexec/shellspec-translate.sh:227-229) — a mocked `git` is a
# forked process. The original suite's whole point for cases 1 and 3 is the opposite: a
# same-named shell FUNCTION, which bash resolves before it ever looks at PATH, so nothing is
# forked (push-branch.test.sh:27-29 and :70-82 say so explicitly). `Mock` would silently
# defeat the exact thing being asserted, so both cases keep plain function overrides instead,
# defined inside the function passed to `When call` — ordinary bash, which ShellSpec is happy
# to run verbatim inside an example.

Describe 'push-branch.sh'
  scratch=""
  setup() { scratch="$(mktemp -d)"; }
  cleanup() { rm -rf "$scratch"; }
  Before 'setup'
  After 'cleanup'

  # Case 1 (push-branch.test.sh:27-47): sourcing the script runs nothing — no git call, no
  # exit out of the sourcing shell — and leaves `main` defined for a caller to run.
  It 'sourcing push-branch.sh runs nothing and defines main'
    trace() {
      git() { echo "git $*" >> "$scratch/calls"; return 0; }
      sleep() { echo "sleep $*" >> "$scratch/calls"; return 0; }
      source "$PUSH"
      echo "source returned"
      declare -F main >/dev/null && echo "main defined"
    }
    : > "$scratch/calls"
    When call trace
    The output should equal "$(printf 'source returned\nmain defined')"
    The value "$(cat "$scratch/calls")" should equal ""
  End

  # Case 2 (push-branch.test.sh:49-64): executed directly (a real process — this is the CLI
  # contract, not the in-process path), a bad tunable is caught before any push: nothing on
  # stdout, one exact stderr line, exit 2. No git/gh/sleep runs on this path, so no mock is
  # needed at all here, same as the original.
  It "executed directly, push-branch.sh keeps its CLI contract: VERI_PUSH_RETRIES=x prints nothing on stdout, one exact stderr line, and exits 2"
    run_push() { VERI_PUSH_RETRIES=x VERI_PUSH_BACKOFF=0 "$PUSH"; }
    When call run_push
    The status should equal 2
    The stdout should equal ""
    The stderr should equal "push-branch.sh: VERI_PUSH_RETRIES must be a non-negative integer, got 'x'"
  End

  # Case 3 (push-branch.test.sh:66-96): sourced, with git/sleep/record mocked as functions and
  # PATH pointed at an empty directory, `main` runs the whole failed-push path in-process:
  # every attempt pushes, one wait between the two, one push-failed event, one stderr line,
  # exit 0 — and no real process starts, since PATH holds nothing one could start from.
  #
  # A whole ShellSpec example (Before hook, When, every The, After hook) runs inside ONE
  # subshell (dsl.sh's `shellspec_example` wraps `shellspec_invoke_example` in `( set -e;
  # ... )`), not a fresh one per statement. That is coarser than the original's own `( ... )`,
  # which scoped PATH="$nobin" to only the case-3 body: a PATH assigned directly in
  # `run_case3` leaked into every later statement in the same example — including `cat` in
  # the closing `The value` check and `rm` in the `After` hook, both now unresolvable — and
  # failed the example for a reason that has nothing to do with push-branch.sh. Nesting the
  # original's own `( ... )` inside `run_case3` restores the narrower scope the hand-rolled
  # suite got for free from a literal subshell.
  It 'sourced with git, sleep and record mocked as functions and PATH empty, main runs a failed push to its push-failed event, starting no real process'
    run_case3() (
      source "$PUSH"
      git() { echo "git $*" >> "$scratch/calls"; echo "fatal: unable to access origin"; return 128; }
      sleep() { echo "sleep $*" >> "$scratch/calls"; return 0; }
      record() { echo "record $*" >> "$scratch/calls"; return 0; }
      PATH="$scratch/nobin"
      VERI_PUSH_RETRIES=1
      unset VERI_PUSH_BACKOFF
      main
    )
    mkdir -p "$scratch/nobin"
    : > "$scratch/calls"
    When call run_case3
    The status should equal 0
    The stdout should equal ""
    The stderr should equal "push-branch.sh: push failed after 2 attempts; the branch is not on the remote"
    The value "$(cat "$scratch/calls")" should equal "$(printf 'git push --set-upstream origin HEAD\nsleep 2\ngit push --set-upstream origin HEAD\nrecord push-failed error=fatal: unable to access origin attempts=2')"
  End

  # Case 4 (push-branch.test.sh:98-116) is meta: it asserts on the ORIGINAL bash suite's own
  # header comment (not on push-branch.sh, and not on this spec file), so the port keeps
  # reading the same file the original read. It stays meaningful regardless of this spike's
  # verdict: it is what pins that push-branch.test.sh's rationale for being script #1 (#339)
  # doesn't quietly drift out of its header.
  #
  # The original records three separate "missing" reasons when the header lacks a phrase, for
  # a human reading a failing run. ShellSpec's `The status`/`The output` have no natural slot
  # for a list of independent reasons without inventing output just to diff it, and the pass/
  # fail condition is identical either way (all three phrases must be present), so this port
  # collapses the three checks into one boolean and drops the itemised diagnostic — a loss of
  # failure detail, not of what is asserted.
  It "the unit suite's header comment records push-branch.sh as the chosen script, by a process-count proxy and not measured seconds"
    check_header() {
      local header="" line _shebang
      {
        read -r _shebang
        while IFS= read -r line && [[ "$line" == \#* ]]; do header+="$line"$'\n'; done
      } < "$ORIGINAL_SUITE"
      header="${header//$'\n'# / }"
      [[ "$header" =~ push-branch\.sh[^.]*chosen|chosen[^.]*push-branch\.sh ]] || return 1
      [[ "$header" == *"process-count proxy"* ]] || return 1
      [[ "$header" =~ not[[:space:]]+(by[[:space:]]+)?(a[[:space:]]+)?measured([[:space:]]+wall-clock)?[[:space:]]+second ]] || return 1
    }
    When call check_header
    The status should be success
  End
End
