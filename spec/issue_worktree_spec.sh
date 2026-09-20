#shellcheck shell=bash
# ShellSpec port of scripts/tests/issue-worktree.test.sh, for the spike that asks whether
# veri's hand-rolled suites should move to ShellSpec. Nothing here is meant to be merged.
#
# The port is faithful by design: every case keeps the original's seed, the original's inputs
# and the original's assertions, in the original's order. The *reasons* those assertions exist
# are argued at length in the original beside each case, and are not copied here — a second
# copy of an argument is one that drifts. What is commented here is only where the port had to
# diverge from the original, and why.
#
# Divergences that recur, stated once:
#
#  * **One `When` per example.** ShellSpec evaluates exactly one subject per `It`, so a case
#    that invokes the script twice (2, 4, 10, 11, 25) runs the first invocation as ordinary
#    shell in the example body and gives `When run` to the one whose streams and status the
#    case is actually about. The original captured both calls' exit codes the same way, so
#    nothing is lost — but which call ShellSpec is watching is now a choice the port made, and
#    each such case says which it picked.
#  * **Post-call state is read after `When run`.** The original reads git's verdict on the
#    created worktree after the call and folds it into one conjunction; here those reads sit
#    between the `When` and the `The value` lines. ShellSpec runs the evaluation in a subshell,
#    so on-disk state survives it and variables set inside it would not — every read here is of
#    the disk, which is what the original read too.
#  * **Failure detail is gone.** Each original case carries a hand-written failure line naming
#    every probe and the value it got (`exit=$code want 2, stdout='$out' want …`). ShellSpec
#    prints its own diff per failed expectation instead, so those lines are dropped rather than
#    ported. That is a real change in what a red run tells a human: the original named the whole
#    criterion in one sentence, ShellSpec names the one comparison that missed.
#  * **The fixture is per-example.** The original makes one `mktemp -d` for the whole file and
#    gives each case its own subdirectory of it; ShellSpec's Before/After hooks make and drop
#    one per example. Same isolation, 25 mktemps instead of 1.
#  * **Two cases cannot be green and faithful at once.** Cases 6 and 20 deliberately assert
#    nothing about stdout — what they are about is the commit the worktree lands on. ShellSpec
#    treats "the subject wrote to stdout and no expectation read it" as a WARNING, and
#    `--warning-as-failure` is on by default and is a global CLI flag with no per-example or
#    per-group override (`SHELLSPEC_WARNING_AS_FAILURE` is read in lib/core/outputs.sh and set
#    only from the command line). So the choice is: add an `The output should equal` those two
#    cases do not make, or leave the run red. This port leaves it red, because the point of the
#    spike is what a faithful port costs. Both show up in the count line as failures.

WT="$PWD/skills/tdd/scripts/issue-worktree.sh"
SKILL="$PWD/skills/tdd/SKILL.md"

Describe 'issue-worktree.sh'
  # The helpers are the original's, verbatim in behaviour. Their arguments and their answers are
  # unchanged, so the cases below read against the original line for line.
  git_q() { local repo="$1"; shift; git -C "$repo" -c user.name=veri -c user.email=veri@example.test "$@"; }

  new_repo() {
    mkdir -p "$1"
    git init -q -b main "$1" >/dev/null 2>&1
    git_q "$1" commit -q --allow-empty -m "initial" >/dev/null 2>&1
  }

  wt_path() { printf '%s\n' "$(cd "$1" && pwd -P)/.tdd/wt/$2"; }

  registry() {
    git -C "$1" worktree list --porcelain 2>/dev/null
    git -C "$1" for-each-ref --format='%(refname) %(objectname)' refs/heads 2>/dev/null
  }

  linked_worktree() {
    local path="$(cd "$work" && pwd -P)/$2"
    git_q "$1" worktree add -q -b "$3" "$path" main >/dev/null 2>&1
    printf '%s\n' "$path"
  }

  ahead_pair() {
    upstream="$work/$1-upstream"
    clone="$work/$1-clone"
    new_repo "$upstream"
    git clone -q "$upstream" "$clone" >/dev/null 2>&1
    git_q "$upstream" commit -q --allow-empty -m "landed while the clone was busy" >/dev/null 2>&1
    remote_tip="$(git_q "$upstream" rev-parse main)"
    stale_tip="$(git_q "$clone" rev-parse main)"
  }

  # The original's `work` plus its EXIT trap, per example rather than per file. `git worktree
  # add` registers absolute paths inside the fixture, so dropping the whole tree is the whole
  # cleanup — the same thing the original's `trap 'rm -rf "$work"' EXIT` does once at the end.
  make_work() { work="$(mktemp -d)"; }
  drop_work() { [ -n "${work:-}" ] && rm -rf "$work"; return 0; }
  Before 'make_work'
  After 'drop_work'

  # 1
  It 'creates the worktree on a new branch cut from the default branch and prints its path'
    repo="$work/fresh"
    new_repo "$repo"
    main_tip="$(git_q "$repo" rev-parse main)"
    git_q "$repo" switch -q -c side >/dev/null 2>&1
    git_q "$repo" commit -q --allow-empty -m "work on side" >/dev/null 2>&1
    side_tip="$(git_q "$repo" rev-parse side)"
    want="$(wt_path "$repo" 7)"
    cd "$repo"

    When run script "$WT" 7 add-worktree

    top="$(git -C "$want" rev-parse --show-toplevel 2>/dev/null)"
    branch="$(git -C "$want" branch --show-current 2>/dev/null)"
    tip="$(git -C "$want" rev-parse HEAD 2>/dev/null)"

    The status should equal 0
    The output should equal "$want"
    The value "$top" should equal "$want"
    The value "$branch" should equal 'tdd/7-add-worktree'
    # main's tip, not side's — the original spells out both in its failure line; here the
    # second only survives as this comment, since ShellSpec has nowhere to put it.
    The value "$tip" should equal "$main_tip"
    The value "$side_tip" should not equal "$main_tip"
  End

  # 2. `When run` is given the SECOND call: its path, its status and "nothing new created" are
  # what the case is about, and the first call is seed.
  It 'answers a second call for the same issue with the same path and creates nothing new'
    repo="$work/again"
    new_repo "$repo"
    want="$(wt_path "$repo" 9)"
    cd "$repo"

    first="$("$WT" 9 resume-me 2>/dev/null)" && first_code=0 || first_code=$?
    before="$(registry "$repo")"

    When run script "$WT" 9 resume-me

    after="$(registry "$repo")"

    The value "$first_code" should equal 0
    The status should equal 0
    The output should equal "$want"
    The output should equal "$first"
    The value "$after" should equal "$before"
  End

  # 3
  It 'refuses with exit 2 when the branch is checked out elsewhere, and touches nothing'
    repo="$work/taken"
    new_repo "$repo"
    other="$(linked_worktree "$repo" taken-elsewhere tdd/11-collide)"
    mine="$(wt_path "$repo" 11)"
    before="$(registry "$repo")"
    cd "$repo"

    When run script "$WT" 11 collide

    after="$(registry "$repo")"

    The status should equal 2
    The stderr should include "$other"
    The path "$mine" should not be exist
    The value "$after" should equal "$before"
  End

  # 4. The original asserts both halves of --remove in one case, deliberately: "a removal that
  # cannot tell the two apart is either useless or destructive" is one criterion. Both halves
  # are kept here in one example, which costs the port the thing ShellSpec is best at — the
  # dirty half runs as ordinary shell in the body and only the clean half gets `When run`. The
  # clean half is the one given to ShellSpec because its criterion includes the exit status of a
  # removal that must succeed; the dirty half's evidence (exit code, the file, the registry) is
  # all readable from the body.
  It 'removes a clean worktree and refuses one with uncommitted changes with exit 2'
    repo="$work/remove-dirty"
    new_repo "$repo"
    dirty="$(wt_path "$repo" 14)"
    (cd "$repo" && "$WT" 14 still-working >/dev/null 2>&1)
    printf 'work in progress\n' > "$dirty/notes.txt"
    git_q "$dirty" add notes.txt >/dev/null 2>&1
    dirty_before="$(registry "$repo")"
    (cd "$repo" && "$WT" --remove 14 >/dev/null 2>&1) && dirty_code=0 || dirty_code=$?
    dirty_after="$(registry "$repo")"

    clean_repo="$work/remove-clean"
    new_repo "$clean_repo"
    want="$(wt_path "$clean_repo" 13)"
    (cd "$clean_repo" && "$WT" 13 done-with-this >/dev/null 2>&1)
    cd "$clean_repo"

    When run script "$WT" --remove 13

    clean_after="$(registry "$clean_repo")"

    The status should equal 0
    The value "$clean_after" should not include "worktree $want"
    The path "$want" should not be exist
    The value "$dirty_code" should equal 2
    The path "$dirty/notes.txt" should be exist
    The value "$dirty_after" should equal "$dirty_before"
  End

  # 5
  It 'checks out an existing branch that no worktree holds instead of failing on -b'
    repo="$work/existing-branch"
    new_repo "$repo"
    main_tip="$(git_q "$repo" rev-parse main)"
    git_q "$repo" switch -q -c tdd/17-resume >/dev/null 2>&1
    git_q "$repo" commit -q --allow-empty -m "work from the previous run" >/dev/null 2>&1
    branch_tip="$(git_q "$repo" rev-parse tdd/17-resume)"
    git_q "$repo" switch -q main >/dev/null 2>&1
    want="$(wt_path "$repo" 17)"
    cd "$repo"

    When run script "$WT" 17 resume

    branch="$(git -C "$want" branch --show-current 2>/dev/null)"
    tip="$(git -C "$want" rev-parse HEAD 2>/dev/null)"

    The status should equal 0
    The output should equal "$want"
    The value "$branch" should equal 'tdd/17-resume'
    The value "$tip" should equal "$branch_tip"
    The value "$branch_tip" should not equal "$main_tip"
  End

  # 6. Asserts nothing about stdout, as the original does not — so this example WARNS and the
  # run is red. See the header.
  It 'cuts from origin/HEAD when it names a default branch that is neither main nor master'
    upstream="$work/upstream-trunk"
    new_repo "$upstream"
    git_q "$upstream" branch -m main trunk >/dev/null 2>&1
    clone="$work/clone-trunk"
    git clone -q "$upstream" "$clone" >/dev/null 2>&1
    git_q "$clone" symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/trunk >/dev/null 2>&1
    trunk_tip="$(git_q "$clone" rev-parse refs/remotes/origin/trunk)"
    want="$(wt_path "$clone" 21)"
    cd "$clone"

    When run script "$WT" 21 remote-default

    tip="$(git -C "$want" rev-parse HEAD 2>/dev/null)"

    The status should equal 0
    The value "$tip" should equal "$trunk_tip"
  End

  # 7
  It 'cuts from a local master when there is no remote and master is the only branch'
    repo="$work/local-master"
    new_repo "$repo"
    git_q "$repo" branch -m main master >/dev/null 2>&1
    master_tip="$(git_q "$repo" rev-parse master)"
    git_q "$repo" switch -q -c side >/dev/null 2>&1
    git_q "$repo" commit -q --allow-empty -m "work on side" >/dev/null 2>&1
    side_tip="$(git_q "$repo" rev-parse side)"
    want="$(wt_path "$repo" 23)"
    cd "$repo"

    When run script "$WT" 23 local-master

    branch="$(git -C "$want" branch --show-current 2>/dev/null)"
    tip="$(git -C "$want" rev-parse HEAD 2>/dev/null)"

    The status should equal 0
    The output should equal "$want"
    The value "$branch" should equal 'tdd/23-local-master'
    The value "$tip" should equal "$master_tip"
    The value "$side_tip" should not equal "$master_tip"
  End

  # 8
  It 'exits 2 with a diagnostic and creates nothing when there is no remote and no main or master'
    repo="$work/no-default"
    new_repo "$repo"
    git_q "$repo" branch -m main trunk >/dev/null 2>&1
    before="$(registry "$repo")"
    cd "$repo"

    When run script "$WT" 25 no-default

    after="$(registry "$repo")"

    The status should equal 2
    The output should equal ''
    The stderr should include 'default branch'
    The value "$after" should equal "$before"
  End

  # 9
  It 'creates the main working tree worktree when called from a linked worktree'
    repo="$work/from-linked"
    new_repo "$repo"
    linked="$(linked_worktree "$repo" from-linked-session session)"
    want="$(wt_path "$repo" 27)"
    nested="$(wt_path "$linked" 27)"
    cd "$linked"

    When run script "$WT" 27 from-linked

    top="$(git -C "$want" rev-parse --show-toplevel 2>/dev/null)"

    The status should equal 0
    The output should equal "$want"
    The value "$top" should equal "$want"
    The path "$nested" should not be exist
  End

  # 10. `When run` is given the call from the MAIN working tree — the resume, which is the half
  # that used to disagree with the create. The create from the linked worktree is seed.
  It 'finds a run created from a linked worktree again from the main working tree'
    repo="$work/cross-caller"
    new_repo "$repo"
    linked="$(linked_worktree "$repo" cross-caller-session cross-session)"
    want="$(wt_path "$repo" 29)"

    first="$(cd "$linked" && "$WT" 29 cross-caller 2>/dev/null)" && first_code=0 || first_code=$?
    before="$(registry "$repo")"
    cd "$repo"

    When run script "$WT" 29 cross-caller

    after="$(registry "$repo")"

    The value "$first_code" should equal 0
    The status should equal 0
    The output should equal "$want"
    The output should equal "$first"
    The value "$after" should equal "$before"
  End

  # 11. `When run` is given the --remove; the create is seed.
  It 'removes the main working tree worktree when --remove runs from a linked worktree'
    repo="$work/remove-from-linked"
    new_repo "$repo"
    want="$(wt_path "$repo" 31)"
    (cd "$repo" && "$WT" 31 remove-from-linked >/dev/null 2>&1)
    linked="$(linked_worktree "$repo" remove-from-linked-session remove-session)"
    cd "$linked"

    When run script "$WT" --remove 31

    after="$(registry "$repo")"

    The status should equal 0
    The value "$after" should not include "worktree $want"
    The path "$want" should not be exist
  End

  # 12. The original's last probe is `grep -qxF "worktree $out" <<<"$listing"` — the same
  # question the script asks of the registry, whole line and literal. ShellSpec's `include` is a
  # substring test and its `match` is a glob, so neither is that question: a `.` in the path
  # would be a wildcard in one and the line would not have to be whole in the other. The grep is
  # kept and its verdict is what the expectation reads.
  It 'prints the resolved path git itself lists when the repository is reached through a symlink'
    repo="$work/symlinked"
    new_repo "$repo"
    via="$work/reached-by-symlink"
    ln -s "$(cd "$repo" && pwd -P)" "$via"
    want="$(wt_path "$repo" 33)"
    cd "$via"

    When run script "$WT" 33 through-symlink

    listing="$(registry "$repo")"
    listed="$(grep -qxF "worktree $want" <<<"$listing" && echo yes || echo no)"

    The status should equal 0
    The output should equal "$want"
    The value "$listed" should equal 'yes'
  End

  # 13
  It "cuts from origin's tip when the remote's default branch is ahead of the local one"
    ahead_pair ahead
    want="$(wt_path "$clone" 35)"
    cd "$clone"

    When run script "$WT" 35 from-remote-tip

    tip="$(git -C "$want" rev-parse HEAD 2>/dev/null)"

    The status should equal 0
    The output should equal "$want"
    The value "$tip" should equal "$remote_tip"
    The value "$tip" should not equal "$stale_tip"
  End

  # 14
  It "leaves the local default branch ref and the caller's working tree untouched"
    upstream="$work/untouched-upstream"
    new_repo "$upstream"
    clone="$work/untouched-clone"
    git clone -q "$upstream" "$clone" >/dev/null 2>&1
    printf 'landed while the clone was busy\n' > "$upstream/landed.txt"
    git_q "$upstream" add landed.txt >/dev/null 2>&1
    git_q "$upstream" commit -q -m "landed while the clone was busy" >/dev/null 2>&1
    remote_tip="$(git_q "$upstream" rev-parse main)"

    main_before="$(git_q "$clone" rev-parse refs/heads/main)"
    head_before="$(git_q "$clone" rev-parse HEAD)"
    branch_before="$(git_q "$clone" branch --show-current)"
    want="$(wt_path "$clone" 37)"
    cd "$clone"

    When run script "$WT" 37 leave-the-clone-alone

    main_after="$(git_q "$clone" rev-parse refs/heads/main)"
    head_after="$(git_q "$clone" rev-parse HEAD)"
    branch_after="$(git_q "$clone" branch --show-current)"
    dirty_after="$(git_q "$clone" status --porcelain --untracked-files=no)"

    The status should equal 0
    The output should equal "$want"
    The value "$main_after" should equal "$main_before"
    The value "$main_after" should not equal "$remote_tip"
    The value "$head_after" should equal "$head_before"
    The value "$branch_after" should equal "$branch_before"
    The value "$dirty_after" should equal ''
    The path "$clone/landed.txt" should not be exist
  End

  # 15
  It 'gives the new issue branch no upstream'
    upstream="$work/no-tracking-upstream"
    new_repo "$upstream"
    clone="$work/no-tracking-clone"
    git clone -q "$upstream" "$clone" >/dev/null 2>&1
    want="$(wt_path "$clone" 39)"
    cd "$clone"

    When run script "$WT" 39 no-upstream

    tracks="$(git_q "$clone" for-each-ref --format='%(upstream:short)' refs/heads/tdd/39-no-upstream)"

    The status should equal 0
    The output should equal "$want"
    The value "$tracks" should equal ''
  End

  # 16
  It 'refuses with exit 2 when the fetch fails rather than falling back to the stale local branch'
    upstream="$work/unreachable-upstream"
    new_repo "$upstream"
    clone="$work/unreachable-clone"
    git clone -q "$upstream" "$clone" >/dev/null 2>&1
    rm -rf "$upstream"
    want="$(wt_path "$clone" 41)"
    before="$(registry "$clone")"
    cd "$clone"

    When run script "$WT" 41 fetch-fails

    after="$(registry "$clone")"

    The status should equal 2
    The output should equal ''
    The stderr should include 'fetch'
    The path "$want" should not be exist
    The value "$after" should equal "$before"
  End

  # 17
  It 'cuts from the local main without going to a remote when there is no remote at all'
    repo="$work/no-remote"
    new_repo "$repo"
    main_tip="$(git_q "$repo" rev-parse main)"
    git_q "$repo" switch -q -c side >/dev/null 2>&1
    git_q "$repo" commit -q --allow-empty -m "work on side" >/dev/null 2>&1
    side_tip="$(git_q "$repo" rev-parse side)"
    want="$(wt_path "$repo" 43)"
    cd "$repo"

    When run script "$WT" 43 no-remote

    branch="$(git -C "$want" branch --show-current 2>/dev/null)"
    tip="$(git -C "$want" rev-parse HEAD 2>/dev/null)"

    The status should equal 0
    The output should equal "$want"
    The value "$branch" should equal 'tdd/43-no-remote'
    The value "$tip" should equal "$main_tip"
    The value "$side_tip" should not equal "$main_tip"
    The stderr should equal ''
  End

  # 18
  It 'checks out an existing issue branch as it is without going to an unreachable remote'
    upstream="$work/resume-no-fetch-upstream"
    new_repo "$upstream"
    clone="$work/resume-no-fetch-clone"
    git clone -q "$upstream" "$clone" >/dev/null 2>&1
    git_q "$clone" switch -q -c tdd/45-resume-no-fetch >/dev/null 2>&1
    git_q "$clone" commit -q --allow-empty -m "work from the previous run" >/dev/null 2>&1
    branch_tip="$(git_q "$clone" rev-parse tdd/45-resume-no-fetch)"
    git_q "$clone" switch -q main >/dev/null 2>&1
    main_tip="$(git_q "$clone" rev-parse main)"
    rm -rf "$upstream"
    want="$(wt_path "$clone" 45)"
    cd "$clone"

    When run script "$WT" 45 resume-no-fetch

    branch="$(git -C "$want" branch --show-current 2>/dev/null)"
    tip="$(git -C "$want" rev-parse HEAD 2>/dev/null)"

    The status should equal 0
    The output should equal "$want"
    The value "$branch" should equal 'tdd/45-resume-no-fetch'
    The value "$tip" should equal "$branch_tip"
    The value "$tip" should not equal "$main_tip"
    The stderr should equal ''
  End

  # 19. The only case whose subject is not a process: SKILL.md's bullet, read as text. ShellSpec
  # wants an evaluation before an expectation, and there is no command here to evaluate — so the
  # original's `problems` accumulator becomes a function that PRINTS the complaints and the
  # expectation is that it printed none. The three probes and their wording are the original's;
  # what is lost is that the failure line no longer quotes the text that was read, because
  # ShellSpec's diff shows the complaint and not the input it was made about.
  It "says in SKILL.md that the branch is cut from the freshly fetched remote default branch and why the local one is not used"
    skill_entry_problems() {
      local entry problems=""
      entry="$(awk '
        !in_e && index($0, "- `$S/issue-worktree.sh <n> <slug>`") == 1 { in_e = 1; print; next }
        in_e && /^([-#]|[0-9]+\.)/ { exit }
        in_e { print }' "$SKILL" | tr -d '*`' | tr '[:upper:]' '[:lower:]' | tr '\n' ' ')"

      says() {
        local complaint="$1" re="$2"
        [[ "$entry" =~ $re ]] || problems="$problems; $complaint"
      }

      if [[ -z "${entry// /}" ]]; then
        problems="; no bullet for '\$S/issue-worktree.sh <n> <slug>' found in $SKILL — what the conductor is told about the base could not be established"
      else
        says "nothing names a fetch — a conductor reading it cannot tell the base is refreshed at all" \
          'fetch'
        says "the base is still described as the default branch, which reads as the local one" \
          'origin/<[a-z-]+>|origin/(main|master|the default)|remote.s (tip|default)|remote default branch|tip of (the )?(remote|origin)'
        says "nothing says the local default branch is stale, so the fetch reads as belt and braces" \
          'stale|behind|lags?|out of date'
      fi
      printf '%s' "${problems#; }"
    }

    When call skill_entry_problems

    The output should equal ''
  End

  # 20. Asserts nothing about stdout, as the original does not — WARNS, as case 6 does.
  It "cuts from origin's freshly fetched tip when the clone has an origin but no origin/HEAD"
    ahead_pair no-origin-head
    git_q "$clone" symbolic-ref --delete refs/remotes/origin/HEAD >/dev/null 2>&1
    want="$(wt_path "$clone" 47)"
    # `|| true` is the port's, not the original's. The original suite runs under `set -uo
    # pipefail` and NOT `-e`, so an assignment from a command substitution that fails — which
    # this one does by construction, the symref having just been deleted — leaves the name empty
    # and the case carries on. ShellSpec turns errexit on inside an example, so the same line
    # aborts it before the `When` is ever reached, with "Example aborted (exit status: 1)" and no
    # hint which line did it. Every seed line in this suite that reads a ref that may be absent
    # has that shape.
    origin_head="$(git_q "$clone" symbolic-ref --quiet refs/remotes/origin/HEAD 2>/dev/null)" || true
    cd "$clone"

    When run script "$WT" 47 no-origin-head

    tip="$(git -C "$want" rev-parse HEAD 2>/dev/null)"

    The status should equal 0
    The value "$origin_head" should equal ''
    The value "$tip" should equal "$remote_tip"
    The value "$tip" should not equal "$stale_tip"
  End

  # 21
  It 'checks out a branch that exists only on the remote at its own tip with its ledger present'
    upstream="$work/remote-only-upstream"
    new_repo "$upstream"
    git_q "$upstream" switch -q -c tdd/49-remote-only >/dev/null 2>&1
    mkdir -p "$upstream/.tdd"
    printf -- '- [x] 1. the step the previous run finished\n' > "$upstream/.tdd/issue-49.md"
    git_q "$upstream" add .tdd/issue-49.md >/dev/null 2>&1
    git_q "$upstream" commit -q -m "plan: the previous run's ledger" >/dev/null 2>&1
    ledger_want="$(cat "$upstream/.tdd/issue-49.md")"
    remote_branch_tip="$(git_q "$upstream" rev-parse tdd/49-remote-only)"
    git_q "$upstream" switch -q main >/dev/null 2>&1
    clone="$work/remote-only-clone"
    git clone -q "$upstream" "$clone" >/dev/null 2>&1
    main_tip="$(git_q "$clone" rev-parse main)"
    want="$(wt_path "$clone" 49)"

    local_ref="$(git_q "$clone" show-ref --verify --quiet refs/heads/tdd/49-remote-only && echo present || echo absent)"
    remote_ref="$(git_q "$clone" rev-parse --verify --quiet refs/remotes/origin/tdd/49-remote-only 2>/dev/null)"
    cd "$clone"

    When run script "$WT" 49 remote-only

    branch="$(git -C "$want" branch --show-current 2>/dev/null)"
    tip="$(git -C "$want" rev-parse HEAD 2>/dev/null)"
    ledger_got="$(cat "$want/.tdd/issue-49.md" 2>/dev/null)"

    The status should equal 0
    The value "$local_ref" should equal 'absent'
    The value "$remote_ref" should equal "$remote_branch_tip"
    The output should equal "$want"
    The value "$branch" should equal 'tdd/49-remote-only'
    The value "$tip" should equal "$remote_branch_tip"
    The value "$tip" should not equal "$main_tip"
    The value "$ledger_got" should equal "$ledger_want"
  End

  # 22
  It 'makes the worktree for a remote-only branch track that remote branch'
    upstream="$work/tracks-upstream"
    new_repo "$upstream"
    git_q "$upstream" switch -q -c tdd/51-tracks >/dev/null 2>&1
    git_q "$upstream" commit -q --allow-empty -m "the previous run's work" >/dev/null 2>&1
    git_q "$upstream" switch -q main >/dev/null 2>&1
    clone="$work/tracks-clone"
    git clone -q "$upstream" "$clone" >/dev/null 2>&1
    want="$(wt_path "$clone" 51)"

    local_ref="$(git_q "$clone" show-ref --verify --quiet refs/heads/tdd/51-tracks && echo present || echo absent)"
    cd "$clone"

    When run script "$WT" 51 tracks

    tracks="$(git_q "$clone" for-each-ref --format='%(upstream:short)' refs/heads/tdd/51-tracks)"

    The status should equal 0
    The value "$local_ref" should equal 'absent'
    The output should equal "$want"
    The value "$tracks" should equal 'origin/tdd/51-tracks'
  End

  # 23
  It "checks out a local branch ahead of its remote where it stands, never rewound to the remote's tip"
    upstream="$work/local-ahead-upstream"
    new_repo "$upstream"
    git_q "$upstream" switch -q -c tdd/53-local-ahead >/dev/null 2>&1
    git_q "$upstream" commit -q --allow-empty -m "the tip the previous run pushed" >/dev/null 2>&1
    remote_branch_tip="$(git_q "$upstream" rev-parse tdd/53-local-ahead)"
    git_q "$upstream" switch -q main >/dev/null 2>&1
    clone="$work/local-ahead-clone"
    git clone -q "$upstream" "$clone" >/dev/null 2>&1
    git_q "$clone" switch -q -c tdd/53-local-ahead origin/tdd/53-local-ahead >/dev/null 2>&1
    git_q "$clone" commit -q --allow-empty -m "committed by the last run and never pushed" >/dev/null 2>&1
    local_branch_tip="$(git_q "$clone" rev-parse tdd/53-local-ahead)"
    git_q "$clone" switch -q main >/dev/null 2>&1
    want="$(wt_path "$clone" 53)"

    local_ref="$(git_q "$clone" rev-parse --verify --quiet refs/heads/tdd/53-local-ahead 2>/dev/null)"
    remote_ref="$(git_q "$clone" rev-parse --verify --quiet refs/remotes/origin/tdd/53-local-ahead 2>/dev/null)"
    cd "$clone"

    When run script "$WT" 53 local-ahead

    branch="$(git -C "$want" branch --show-current 2>/dev/null)"
    tip="$(git -C "$want" rev-parse HEAD 2>/dev/null)"

    The status should equal 0
    The value "$local_ref" should equal "$local_branch_tip"
    The value "$remote_ref" should equal "$remote_branch_tip"
    The value "$local_branch_tip" should not equal "$remote_branch_tip"
    The output should equal "$want"
    The value "$branch" should equal 'tdd/53-local-ahead'
    The value "$tip" should equal "$local_branch_tip"
  End

  # 24
  It 'still cuts from the default branch for a name that exists in neither namespace'
    upstream="$work/neither-upstream"
    new_repo "$upstream"
    git_q "$upstream" switch -q -c tdd/99-some-other-run >/dev/null 2>&1
    git_q "$upstream" commit -q --allow-empty -m "another issue's run, pushed" >/dev/null 2>&1
    other_tip="$(git_q "$upstream" rev-parse tdd/99-some-other-run)"
    git_q "$upstream" switch -q main >/dev/null 2>&1
    clone="$work/neither-clone"
    git clone -q "$upstream" "$clone" >/dev/null 2>&1
    main_tip="$(git_q "$clone" rev-parse main)"
    want="$(wt_path "$clone" 55)"

    local_ref="$(git_q "$clone" show-ref --verify --quiet refs/heads/tdd/55-neither && echo present || echo absent)"
    remote_ref="$(git_q "$clone" show-ref --verify --quiet refs/remotes/origin/tdd/55-neither && echo present || echo absent)"
    cd "$clone"

    When run script "$WT" 55 neither

    branch="$(git -C "$want" branch --show-current 2>/dev/null)"
    tip="$(git -C "$want" rev-parse HEAD 2>/dev/null)"

    The status should equal 0
    The value "$local_ref" should equal 'absent'
    The value "$remote_ref" should equal 'absent'
    The output should equal "$want"
    The value "$branch" should equal 'tdd/55-neither'
    The value "$tip" should equal "$main_tip"
    The value "$tip" should not equal "$other_tip"
  End

  # 25. `When run` is given the second call — the refusal. The first is the script's own seed,
  # as the original insists it must be.
  #
  # `$$` is the original's choice of "a pid certain to be alive for exactly as long as the case
  # runs". ShellSpec runs each example in a subshell and bash does not renumber `$$` there, so it
  # is still the runner's own pid — alive, and the same value the expectation reads back.
  It 'refuses with exit 2 and prints no path when the conductor that made the worktree is still alive'
    repo="$work/live-holder"
    new_repo "$repo"
    live="$(wt_path "$repo" 61)"

    first="$(cd "$repo" && "$WT" 61 live-run 2>/dev/null)" && first_code=0 || first_code=$?
    mkdir -p "$live/.tdd"
    printf '%s\n' "$$" > "$live/.tdd/conductor.pid"
    before="$(registry "$repo")"
    cd "$repo"

    When run script "$WT" 61 live-run

    after="$(registry "$repo")"

    The value "$first_code" should equal 0
    The value "$first" should equal "$live"
    The status should equal 2
    The output should equal ''
    The stderr should include "$$"
    The value "$after" should equal "$before"
  End
End
