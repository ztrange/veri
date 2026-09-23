#!/usr/bin/env bash
# Tests for scripts/preserve-attempt.sh — the side-ref snapshot a troubled step leaves behind,
# so the tree a rejected or stuck leaf produced is still readable after the run (issue #409).
#
# Contract under test:
#   preserve-attempt.sh <issue> <step> <phase> <attempt>   # run from the issue's worktree
#       commits the worktree as it stands to refs/veri/attempts/<issue>/<step>/<phase>-<attempt>
#
# The subject is git's own storage, so this suite is not in the fast tier: the behaviour under
# test IS a real repository's refs, and a fake git could not answer `git show`. Every case runs
# against a throwaway `git init` repo with one commit, and asks git rather than the filesystem —
# a file written under .git by hand would pass a filesystem check and be no commit at all.
#
# Run: scripts/tests/preserve-attempt.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
PRESERVE="$HERE/../preserve-attempt.sh"
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
pass=0 fail=0
ok() { pass=$((pass + 1)); }
no() { fail=$((fail + 1)); echo "FAIL - $1"; }

# The identity every commit this suite causes is made under, stated once: the suite must not
# depend on whatever user.name/user.email the machine running it carries (CI carries none).
# In the environment rather than as `git -c` flags because half the commits are git's own,
# made inside the script under test, which takes no flags from here.
ident=(GIT_AUTHOR_NAME=veri GIT_AUTHOR_EMAIL=veri@example.test
       GIT_COMMITTER_NAME=veri GIT_COMMITTER_EMAIL=veri@example.test)

# git_q <repo> <args…> — git run against <repo> under that identity.
git_q() { local repo="$1"; shift; env "${ident[@]}" git -C "$repo" "$@"; }

# Every case calls the script with the same coordinates — issue 409, step 3, develop-green,
# attempt 1 — so the one ref they all expect is spelled out once rather than per case.
REF="refs/veri/attempts/409/3/develop-green-1"

# ref_resolves <repo> [<ref>] — 0 when <ref>, $REF by default, names a commit in <repo>. Asked
# of git rather than of the filesystem, for the reason in the header: a file written under .git
# by hand would pass a filesystem check and be no commit at all. The ref is a parameter because
# the case that pins the ledger-index name expects a different one, and the reading is the same.
ref_resolves() { git_q "$1" rev-parse --verify --quiet "${2:-$REF}^{commit}" >/dev/null 2>&1; }

# attempts_dir <repo> — the directory preservation puts its copies in. A case asks whether it
# exists at all as well as what is in it, and copy_path builds names under it, so the path is
# named here once and nowhere else.
attempts_dir() { printf '%s/.tdd/attempts' "$1"; }

# copies_in <repo> — every name left in that directory, space-joined, and empty when the
# directory is not there. The listing rather than a count, so a case that expected nothing
# names what it found instead.
copies_in() { ls "$(attempts_dir "$1")" 2>/dev/null | tr '\n' ' '; }

# copy_path <repo> <step> <mark> <ext> — where preservation puts the leaf's <ext> file in
# <repo> for step <step> under <mark>. The name is the criterion itself — step, phase, attempt
# and the mark that triggered the preservation — so it is built in one place, not per case. The
# step is a parameter for the same reason ref_resolves takes its ref: the case that pins the
# ledger-index naming expects a different number, and the name is built the same way.
copy_path() { printf '%s/%s-develop-green-1-%s.%s' "$(attempts_dir "$1")" "$2" "$3" "$4"; }

# copy_text <path> — the preserved file's contents, or the literal <missing> when it was never
# written. A failure message that says <missing> distinguishes "preserved the wrong bytes" from
# "preserved nothing", which an empty string would not.
copy_text() { if [[ -f "$1" ]]; then cat "$1"; else echo "<missing>"; fi; }

# new_repo <path> — a throwaway repo at <path>, on `main`, carrying one commit that tracks
# stop-run.sh. -b main names the default branch rather than inheriting init.defaultBranch.
new_repo() {
  mkdir -p "$1"
  git init -q -b main "$1" >/dev/null 2>&1
  printf 'committed\n' > "$1/stop-run.sh"
  git_q "$1" add stop-run.sh >/dev/null 2>&1
  git_q "$1" commit -q -m "initial" >/dev/null 2>&1
}

# The worktree edit preservation exists to capture: stop-run.sh differing from the commit that
# tracks it. Two cases read this text back out of the preserved tree and seven write it, so it is
# one name rather than a string repeated either side of the script under test.
REJECTED="rejected work"

# dirty_repo <path> — new_repo carrying that edit, which is the fixture nearly every case starts
# from; the ones that do not are the ones about the leaf's own output, not its tree.
dirty_repo() {
  new_repo "$1"
  printf '%s\n' "$REJECTED" > "$1/stop-run.sh"
}

# write_ledger <repo> <step…> — issue 409's committed plan ledger in <repo>, one checkbox line
# per <step> in the order given, the first already ticked and the rest unchecked. A ticked line
# first because the index the script derives counts every checkbox, done or not; committed
# rather than merely written because that is the shape a run's ledger is in by the time an
# attempt is preserved. Two cases need one, of different lengths, so the shape of a ledger is
# written here rather than in each of them.
write_ledger() {
  local repo="$1"; shift
  local box='x' step
  mkdir -p "$repo/.tdd"
  { printf '# Plan for #409\n\n'
    for step in "$@"; do printf -- '- [%s] %s\n' "$box" "$step"; box=' '; done
  } > "$repo/.tdd/issue-409.md"
  git_q "$repo" add .tdd/issue-409.md >/dev/null 2>&1
  git_q "$repo" commit -q -m "plan: scope #409" >/dev/null 2>&1
}

# leaf_output <repo> <log-text> [<out-text>] — the files run-leaf.sh leaves behind in <repo>
# for the develop-green phase: the progress log always, and the final-output file only when
# <out-text> is given, because a leaf killed before it wrote one is a case of its own. Their
# names are what preservation reads, so they are spelled here rather than in each case.
leaf_output() {
  local repo="$1" log_text="$2" out_text="${3:-}"
  mkdir -p "$repo/.tdd"
  printf '%s\n' "$log_text" > "$repo/.tdd/develop-green.log"
  if [[ -n "$out_text" ]]; then printf '%s\n' "$out_text" > "$repo/.tdd/develop-green.out"; fi
}

# preserve <repo> <args…> — call the script from <repo>, under the same identity: the commit
# it makes is git's, and a machine with no configured user (CI) must not decide whether this
# case can run at all.
preserve() {
  local repo="$1"; shift
  ( cd "$repo" && env "${ident[@]}" "$PRESERVE" "$@" )
}

# 1. the worktree as it stands lands on a ref named by issue, step, phase and attempt, and
#    `git show` reads that commit's tree back — the rejected file, which no commit on the
#    branch ever carried
repo="$work/repo"
dirty_repo "$repo"
preserve "$repo" 409 3 develop-green 1 >/dev/null 2>&1; code=$?
ref_resolves "$repo"; resolved=$?
shown="$(git_q "$repo" show "$REF:stop-run.sh" 2>&1)"
{ [[ "$code" == 0 ]] && [[ "$resolved" == 0 ]] && [[ "$shown" == "$REJECTED" ]]; } \
  && ok || no "commits the worktree to $REF and git show reads it back (code=$code resolved=$resolved shown='$shown')"

# 2. preserving leaves the work branch untouched — HEAD, the index and `git log` read the same
#    after as before, so a rebase-merge of the branch carries none of the preserved commit. The
#    index is made to differ from HEAD first (a staged file), so "unchanged" is a real claim
#    rather than one an empty index would satisfy by accident.
repo="$work/untouched"
dirty_repo "$repo"
printf 'staged\n' > "$repo/staged.txt"
git_q "$repo" add staged.txt >/dev/null 2>&1
head_before="$(git_q "$repo" rev-parse HEAD 2>&1)"
index_before="$(git_q "$repo" ls-files -s 2>&1)"
log_before="$(git_q "$repo" log --oneline 2>&1)"
preserve "$repo" 409 3 develop-green 1 >/dev/null 2>&1; code=$?
head_after="$(git_q "$repo" rev-parse HEAD 2>&1)"
index_after="$(git_q "$repo" ls-files -s 2>&1)"
log_after="$(git_q "$repo" log --oneline 2>&1)"
{ [[ "$code" == 0 ]] && [[ "$head_after" == "$head_before" ]] \
    && [[ "$index_after" == "$index_before" ]] && [[ "$log_after" == "$log_before" ]]; } \
  && ok || no "leaves HEAD, the index and git log untouched (code=$code head=$head_before/$head_after index_changed=$([[ "$index_after" == "$index_before" ]] && echo no || echo yes) log_changed=$([[ "$log_after" == "$log_before" ]] && echo no || echo yes))"

# 3. the leaf's own output is preserved beside the tree: the progress log and the final-output
#    file are copied to names carrying the step, phase, attempt and the mark that triggered the
#    preservation, so a reader can pair them with the event that made the step interesting. The
#    originals stay where run-leaf.sh left them — this is a copy, not a move, because the leaf
#    that wrote them may still be the one a retry reads back.
repo="$work/leafoutput"
new_repo "$repo"
leaf_output "$repo" 'streamed progress' 'final result text'
preserve "$repo" 409 3 develop-green 1 reject >/dev/null 2>&1; code=$?
log_copy="$(copy_path "$repo" 3 reject log)"
out_copy="$(copy_path "$repo" 3 reject out)"
log_text="$(copy_text "$log_copy")"
out_text="$(copy_text "$out_copy")"
{ [[ "$code" == 0 ]] && [[ "$log_text" == "streamed progress" ]] \
    && [[ "$out_text" == "final result text" ]] \
    && [[ -f "$repo/.tdd/develop-green.log" ]] && [[ -f "$repo/.tdd/develop-green.out" ]]; } \
  && ok || no "copies the leaf's log and final output to names carrying step, phase, attempt and mark (code=$code log='$log_text' out='$out_text')"

# 4. a leaf killed before it wrote its final-output file still gets its log preserved, and the
#    preservation reports success: a missing .out is the normal shape of a stuck or killed leaf,
#    not a failure of preserving what there was. No .out copy is written, because there was
#    nothing to copy.
repo="$work/nooutput"
new_repo "$repo"
leaf_output "$repo" 'streamed progress'
preserve "$repo" 409 3 develop-green 1 stuck >/dev/null 2>&1; code=$?
log_copy="$(copy_path "$repo" 3 stuck log)"
out_copy="$(copy_path "$repo" 3 stuck out)"
log_text="$(copy_text "$log_copy")"
out_there="$([[ -e "$out_copy" ]] && echo yes || echo no)"
{ [[ "$code" == 0 ]] && [[ "$log_text" == "streamed progress" ]] && [[ "$out_there" == no ]]; } \
  && ok || no "preserves the log of a leaf that wrote no final output, with exit 0 (code=$code log='$log_text' out_copy=$out_there)"

# 5. and a leaf that wrote neither file is preserved too: the tree is still on its ref and the
#    preservation still reports success. Nothing is copied, so a reader is never handed an
#    empty file that reads as "the leaf said nothing" when the truth is it never wrote one.
repo="$work/nooutputatall"
dirty_repo "$repo"
preserve "$repo" 409 3 develop-green 1 bail >/dev/null 2>&1; code=$?
ref_resolves "$repo"; resolved=$?
copies="$(copies_in "$repo")"
{ [[ "$code" == 0 ]] && [[ "$resolved" == 0 ]] && [[ -z "$copies" ]]; } \
  && ok || no "preserves the tree and exits 0 when the leaf wrote neither log nor output (code=$code resolved=$resolved copies='$copies')"

# 6. and the mark is what turns copying on: the same call without it — four arguments, with a
#    progress log sitting right there in .tdd — preserves the tree and copies nothing. An
#    untroubled step is the common case, and it must cost what it costs today: no .tdd/attempts
#    directory, no copies in it.
repo="$work/nomark"
dirty_repo "$repo"
leaf_output "$repo" 'streamed progress' 'final result text'
preserve "$repo" 409 3 develop-green 1 >/dev/null 2>&1; code=$?
ref_resolves "$repo"; resolved=$?
attempts_there="$([[ -e "$(attempts_dir "$repo")" ]] && echo yes || echo no)"
copies="$(copies_in "$repo")"
{ [[ "$code" == 0 ]] && [[ "$resolved" == 0 ]] && [[ "$attempts_there" == no ]] && [[ -z "$copies" ]]; } \
  && ok || no "copies nothing when no mark is given, log present (code=$code resolved=$resolved attempts_dir=$attempts_there copies='$copies')"

# 7. preservation puts the developer's rationale nowhere a verifier leaf reads: the preserved
#    commit is unreachable from HEAD — `git log` on the branch never walks into it, and a blind
#    verifier reading `git diff <base-sha>..HEAD` never sees it either — and the commit's own
#    message carries the coordinates and nothing else. The leaf's log and final output are made
#    to carry an unmistakable rationale sentence first, so "no rationale in the message" is a
#    claim about a string that was sitting right there to be copied into it.
repo="$work/blind"
dirty_repo "$repo"
rationale="I used a helper because the verifier rejected the inline version"
leaf_output "$repo" "$rationale" "$rationale"
preserve "$repo" 409 3 develop-green 1 reject >/dev/null 2>&1; code=$?
git_q "$repo" merge-base --is-ancestor "$REF" HEAD >/dev/null 2>&1; reachable=$?
message="$(git_q "$repo" log -1 --format=%B "$REF" 2>&1)"
{ [[ "$code" == 0 ]] && [[ "$reachable" != 0 ]] \
    && [[ "$message" == "attempt: issue 409 step 3 develop-green attempt 1" ]]; } \
  && ok || no "leaves the preserved commit unreachable from HEAD, with a message carrying no rationale (code=$code reachable=$([[ "$reachable" == 0 ]] && echo yes || echo no) message='$message')"

# 8. the ref name carries the step's INDEX in the committed ledger, not the step's own prose:
#    a plan step is a sentence with spaces, and often an apostrophe or a slash, none of which
#    `git check-ref-format` accepts — so a ref built out of the title is no ref at all and the
#    snapshot is silently never written (issue #427). The ledger already numbers its steps by
#    position, which is short, stable and legal, so the second unchecked-or-checked step of
#    issue 409's ledger is preserved under `.../409/2/...` however it is worded.
repo="$work/ledgerindex"
dirty_repo "$repo"
prose="A leaf's output is kept under refs/veri, not the branch"
write_ledger "$repo" "The first step, already done" "$prose" "A third step nobody is on"
preserve "$repo" 409 "$prose" develop-green 1 >/dev/null 2>&1; code=$?
indexed="refs/veri/attempts/409/2/develop-green-1"
ref_resolves "$repo" "$indexed"; resolved=$?
refs="$(git_q "$repo" for-each-ref --format='%(refname)' refs/veri/attempts 2>&1 | tr '\n' ' ')"
{ [[ "$code" == 0 ]] && [[ "$resolved" == 0 ]]; } \
  && ok || no "names the ref by the step's ledger index, not its prose (code=$code resolved=$([[ "$resolved" == 0 ]] && echo yes || echo no) refs='$refs')"

# 9. and a step the ledger cannot name is preserved all the same, under a ref name git accepts:
#    the fallback has only the title to go on, and a title is a sentence — spaces, an
#    apostrophe, a slash — none of which `git check-ref-format` allows, so the fallback wrote no
#    ref at all and the snapshot was silently lost (issue #427). The repo carries no ledger, so
#    the title is all there is; what the ref is called is the green leaf's to choose, and what
#    this case asks is only that git accepts it and reads the attempt's tree back through it.
repo="$work/prosetitle"
dirty_repo "$repo"
prose="A leaf's tree is kept under refs/veri, not the branch"
preserve "$repo" 409 "$prose" develop-green 1 >/dev/null 2>&1; code=$?
found="$(git_q "$repo" for-each-ref --count=1 --format='%(refname)' refs/veri/attempts/409 2>/dev/null)"
git_q "$repo" check-ref-format "$found" >/dev/null 2>&1; legal=$?
shown="$(git_q "$repo" show "$found:stop-run.sh" 2>&1)"
{ [[ "$code" == 0 ]] && [[ -n "$found" ]] && [[ "$legal" == 0 ]] \
    && [[ "$shown" == "$REJECTED" ]]; } \
  && ok || no "preserves the attempt under a ref git accepts when the step title carries spaces, an apostrophe and a slash (code=$code ref='$found' legal=$([[ "$legal" == 0 ]] && echo yes || echo no) shown='$shown')"

# 10. and the leaf's own copies are named from that same index too: the ref is not the only
#     place the step's prose is spelled into a path. `.tdd/attempts/<step>-<phase>-<attempt>-
#     <mark>.log` built out of a title carrying a slash names a directory that does not exist,
#     so the copy fails and the preservation reports a failure for a leaf whose log was sitting
#     right there (issue #427). The ledger names this step 2, so both copies are `2-...` and
#     nothing nested is written beside them.
repo="$work/ledgercopies"
new_repo "$repo"
prose="A leaf's output is kept under refs/veri, not the branch"
write_ledger "$repo" "The first step, already done" "$prose"
leaf_output "$repo" 'streamed progress' 'final result text'
preserve "$repo" 409 "$prose" develop-green 1 reject >/dev/null 2>&1; code=$?
log_text="$(copy_text "$(copy_path "$repo" 2 reject log)")"
out_text="$(copy_text "$(copy_path "$repo" 2 reject out)")"
entries="$(copies_in "$repo")"
{ [[ "$code" == 0 ]] && [[ "$log_text" == "streamed progress" ]] \
    && [[ "$out_text" == "final result text" ]] \
    && [[ "$entries" == "2-develop-green-1-reject.log 2-develop-green-1-reject.out " ]]; } \
  && ok || no "names the leaf's copies by the step's ledger index, so a title carrying a slash writes no nested path (code=$code log='$log_text' out='$out_text' entries='$entries')"


# 11. a preserve that fails for a reason deriving a legal name cannot fix — here a ref already
#     sitting where the attempt's own ref needs a directory — says so on stderr and exits
#     non-zero, rather than passing silently (issue #427). That silence is the whole reason the
#     prose-ref bug survived: preservation is best-effort to every caller, so a reader of the
#     run's .err has only what this script says to go on, and git's own plumbing fatal names a
#     ref rather than the attempt it belonged to.
repo="$work/otherfailure"
dirty_repo "$repo"
git_q "$repo" update-ref "refs/veri/attempts/409/3" HEAD >/dev/null 2>&1
err="$(preserve "$repo" 409 3 develop-green 1 2>&1 >/dev/null)"; code=$?
said=no
if [[ "$err" == *preserve-attempt.sh* && "$err" == *409* && "$err" == *develop-green* ]]; then said=yes; fi
{ [[ "$code" != 0 ]] && [[ "$said" == yes ]]; } \
  && ok || no "says on stderr that it could not preserve the attempt when the ref write fails for another reason (code=$code said=$said err='$err')"


echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
