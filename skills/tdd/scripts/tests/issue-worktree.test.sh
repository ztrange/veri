#!/usr/bin/env bash
# Unit tests for scripts/issue-worktree.sh — the linked git worktree an issue branch lives
# in, so a conductor never drags the checkout it was invoked from off the default branch.
#
# Contract under test:
#   issue-worktree.sh <n> <slug>   creates/reuses <repo-root>/.tdd/wt/<n> on branch
#                                  tdd/<n>-<slug>, prints its absolute path, exit 0
#
# Run: scripts/tests/issue-worktree.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
source "$HERE/lib/harness.sh"
work="$(scratch_dir)"
mkdir -p "$work/skill/scripts"
cp -R "$HERE/../issue-worktree.sh" "$HERE/../veri" "$work/skill/scripts/"
WT="$work/skill/scripts/issue-worktree.sh"

git_q() { local repo="$1"; shift; git -C "$repo" -c user.name=veri -c user.email=veri@example.test "$@"; }

make_repo() {
  mkdir -p "$1"
  new_repo -b main "$1" >/dev/null 2>&1
  git_q "$1" commit -q --allow-empty -m "initial" >/dev/null 2>&1
}

stub_git() {
  local dir="$1" real
  real="$(command -v git)"
  mkdir -p "$dir"
  cat > "$dir/git" <<STUB
#!/bin/sh
case "\$1" in
  remote) [ -n "\${STUB_ORIGIN_URL:-}" ] && [ "\$2" = get-url ] && { echo "\$STUB_ORIGIN_URL"; exit 0; } ;;
  ls-remote) [ -n "\${STUB_LS_EMPTY:-}" ] && exit 0; [ -n "\${STUB_LS_FAIL:-}" ] && { echo "fatal: unable to access remote" >&2; exit 128; } ;;
  fetch) [ -n "\${STUB_FETCH_FAIL:-}" ] && { echo "fatal: unable to access remote" >&2; exit 128; } ;;
esac
exec "$real" "\$@"
STUB
  chmod +x "$dir/git"
}
stub_git "$work/stubbin"

wt_path() { printf '%s\n' "$(cd "$1" && pwd -P)/.tdd/wt/$2"; }

registry() {
  git -C "$1" worktree list --porcelain 2>/dev/null
  git -C "$1" for-each-ref --format='%(refname) %(objectname)' refs/heads 2>/dev/null
}

ahead_pair() {
  upstream="$work/$1-upstream"
  clone="$work/$1-clone"
  make_repo "$upstream"
  git clone -q "$upstream" "$clone" >/dev/null 2>&1
  git_q "$upstream" commit -q --allow-empty -m "landed while the clone was busy" >/dev/null 2>&1
  remote_tip="$(git_q "$upstream" rev-parse main)"
  stale_tip="$(git_q "$clone" rev-parse main)"
}

upstream="$work/ls-remote-silent-upstream"
make_repo "$upstream"
clone="$work/ls-remote-silent-clone"
git clone -q "$upstream" "$clone" >/dev/null 2>&1
want="$(wt_path "$clone" 1672)"
before="$(registry "$clone")"

errfile="$work/ls-remote-silent.err"
out="$(cd "$clone" && PATH="$work/stubbin:$PATH" STUB_LS_FAIL=1 "$WT" 1672 ls-remote-silent 2>"$errfile")" && code=0 || code=$?
after="$(registry "$clone")"

{ [[ "$code" == 2 ]] && [[ -z "$out" ]] && grep -F 'ls-remote' "$errfile" >/dev/null \
  && [[ ! -e "$want" ]] && [[ "$after" == "$before" ]]; } \
  && ok || no "#1672: a fresh cut whose origin ls-remote gets no answer (the fetch would answer): exits 2 naming the ls-remote lookup and creates no worktree (exit=$code want 2, stdout='$out' want empty, stderr='$(cat "$errfile")' want it to name ls-remote, $want $( [[ -e "$want" ]] && echo "exists" || echo "absent, good" ), registry $( [[ "$after" == "$before" ]] && echo unchanged || echo changed ))"

SKILL="$HERE/../../SCRIPTS.md"

entry="$(awk '
  !in_e && index($0, "- `$S/issue-worktree.sh <n> <slug>") == 1 { in_e = 1; print; next }
  in_e && /^([-#]|[0-9]+\.)/ { exit }
  in_e { print }' "$SKILL" | tr -d '*`' | tr '[:upper:]' '[:lower:]' | tr '\n' ' ')"

synopsis="$(grep -m1 -F -- '- `$S/issue-worktree.sh <n> <slug>' "$SKILL" || true)"
[[ -n "${entry// /}" ]] \
  && ok || no "#1432: the issue-worktree.sh entry is read out of SKILL.md whatever alternatives its synopsis names after '<n> <slug>' (synopsis line in SKILL.md: '$synopsis', entry read: '$entry')"

says() {
  local complaint="$1" re="$2"
  [[ "$entry" =~ $re ]] || problems="$problems; $complaint"
}

repo="$work/pinned-scratch"
make_repo "$repo"
decoy="$work/decoy"
make_repo "$decoy"
mutant="$decoy/skills/tdd/scripts"
mkdir -p "$mutant"
cp -R "$HERE/../veri" "$mutant/veri"
awk '/^exec python3/ { print "cd \"$(dirname \"$0\")\"" } { print }' "$WT" > "$mutant/issue-worktree.sh"
chmod +x "$mutant/issue-worktree.sh"
before="$(registry "$decoy")"
errfile="$work/pinned-scratch.err"

out="$(cd "$repo" && "$mutant/issue-worktree.sh" 41 escaped 2>"$errfile")" && code=0 || code=$?
after="$(registry "$decoy")"

problems=""
[[ "$after" == "$before" ]] || problems+="; the decoy repository's worktree+branch registry changed:
--- before
$before
--- after
$after"
[[ ! -e "$decoy/.tdd/wt/41" ]] || problems+="; $decoy/.tdd/wt/41 was created"
[[ "$code" != 0 || "$out" != *"$decoy"* ]] || problems+="; exit=0 naming '$out', want the case to fail on a subject that resolved the decoy repository"
{ [[ -z "$problems" ]]; } \
  && ok || no "#1158: an issue-worktree.sh that resolves its main tree from its own directory, not the suite's scratch repository, creates no worktree, branch or .tdd/wt entry outside that repository (${problems#; })"

repo="$work/scratch-copy"
make_repo "$repo"
scratch="$(cd "$work" && pwd -P)"
subject_dir="$(cd "$(dirname "$WT")" && pwd -P)"
errfile="$work/scratch-copy.err"
problems=""
if [[ "$subject_dir/" != "$scratch/"* ]]; then
  problems+="; want the suite to run a copy of issue-worktree.sh under its scratch directory $scratch, it runs $subject_dir/issue-worktree.sh"
else
  landing="$(cd "$subject_dir/../.." && pwd -P)"
  if [[ "$landing/" != "$scratch/"* || "$landing/" == "$(cd "$repo" && pwd -P)/"* ]]; then
    problems+="; want the copy's ../.. inside $scratch and outside the scratch repository, it is $landing"
  else
    mkdir -p "$landing/.tdd/wt/5/.tdd"
    printf '%s\n' "$$" > "$landing/.tdd/wt/5/.tdd/conductor.pid"
    cp "$WT" "$WT.orig"
    awk '/^exec python3/ { print "cd \"$(dirname \"$0\")/../..\"" } { print }' "$WT.orig" > "$WT"
    chmod +x "$WT"
    out="$(cd "$repo" && "$WT" 42 planted 2>"$errfile")" && code=0 || code=$?
    mv "$WT.orig" "$WT"
    [[ ! -e "$landing/.tdd/wt/42" ]] || problems+="; $landing/.tdd/wt/42 was created"
    landing_branches="$(git -C "$landing" for-each-ref --format='%(refname)' refs/heads/tdd 2>/dev/null)"
    [[ -z "$landing_branches" ]] || problems+="; branches created beside the scratch repository: $landing_branches"
    [[ "$code" != 0 || "$out" == "$(wt_path "$repo" 42)" ]] || problems+="; exit=0 naming '$out', want the scratch repository's .tdd/wt/42 or a failure"
  fi
fi
{ [[ -z "$problems" ]]; } \
  && ok || no "#1158: the suite runs a scratch copy of issue-worktree.sh, and a cd \"\$(dirname \"\$0\")/../..\" planted into it creates no worktree, branch or .tdd/wt entry outside the scratch repository (${problems#; })"

ahead_pair remote-claimed
git_q "$upstream" branch -q tdd/61-someone-else main >/dev/null 2>&1
mine="$(wt_path "$clone" 61)"
before="$(registry "$clone")"
heads_before="$(git_q "$clone" rev-list --all 2>/dev/null)"

err="$(cd "$clone" && "$WT" 61 fresh-start 2>&1 >/dev/null)" && code=0 || code=$?
after="$(registry "$clone")"
heads_after="$(git_q "$clone" rev-list --all 2>/dev/null)"

{ [[ "$code" == 2 ]] && [[ "$err" == *"tdd/61-someone-else"* ]] && [[ ! -e "$mine" ]] \
  && [[ "$after" == "$before" ]] && [[ "$heads_after" == "$heads_before" ]]; } \
  && ok || no "#1656: an issue branch already on the remote: a fresh call exits 2 naming that remote branch and leaves no worktree, branch or commit behind (exit=$code want 2, stderr='$err' want it to name 'tdd/61-someone-else', '$mine' $( [[ -e "$mine" ]] && echo "was created" || echo "absent, good" ), git's worktree+branch registry $( [[ "$after" == "$before" ]] && echo unchanged || echo changed ), commits $( [[ "$heads_after" == "$heads_before" ]] && echo unchanged || echo changed ))"

ahead_pair pr-claimed
mine="$(wt_path "$clone" 62)"
mkdir -p "$work/pr-claimed-gh"
printf '[{"body": "Closes #62", "state": "OPEN", "isDraft": true, "url": "https://example.test/pull/620"}]\n' > "$work/pr-claimed-gh/prs.json"
before="$(registry "$clone")"
heads_before="$(git_q "$clone" rev-list --all 2>/dev/null)"

err="$(cd "$clone" && VERI_GH_JSON="$work/pr-claimed-gh" "$WT" 62 fresh-start 2>&1 >/dev/null)" && code=0 || code=$?
after="$(registry "$clone")"
heads_after="$(git_q "$clone" rev-list --all 2>/dev/null)"

{ [[ "$code" == 2 ]] && [[ "$err" == *"pull/620"* ]] && [[ ! -e "$mine" ]] \
  && [[ "$after" == "$before" ]] && [[ "$heads_after" == "$heads_before" ]]; } \
  && ok || no "#1656: an open PR saying Closes #62: a fresh call exits 2 naming that PR and leaves no worktree, branch or commit behind (exit=$code want 2, stderr='$err' want it to name 'pull/620', '$mine' $( [[ -e "$mine" ]] && echo "was created" || echo "absent, good" ), git's worktree+branch registry $( [[ "$after" == "$before" ]] && echo unchanged || echo changed ), commits $( [[ "$heads_after" == "$heads_before" ]] && echo unchanged || echo changed ))"

ahead_pair pr-silent
mine="$(wt_path "$clone" 64)"
mkdir -p "$work/pr-silent-gh"
before="$(registry "$clone")"

errfile="$work/pr-silent.err"
out="$(cd "$clone" && VERI_GH_JSON="$work/pr-silent-gh" "$WT" 64 fresh-start 2>"$errfile")" && code=0 || code=$?
after="$(registry "$clone")"

{ [[ "$code" == 2 ]] && [[ -z "$out" ]] && grep -Ei 'open[- ]PR' "$errfile" >/dev/null \
  && [[ ! -e "$mine" ]] && [[ "$after" == "$before" ]]; } \
  && ok || no "#1672: a fresh cut whose open-PR lookup gets no answer: exits 2 naming the open-PR lookup and creates no worktree (exit=$code want 2, stdout='$out' want empty, stderr='$(cat "$errfile")' want it to name the open-PR lookup, '$mine' $( [[ -e "$mine" ]] && echo "was created" || echo "absent, good" ), registry $( [[ "$after" == "$before" ]] && echo unchanged || echo changed ))"

ahead_pair resume-claimed
git_q "$upstream" branch -q tdd/63-mine main >/dev/null 2>&1
mine="$(wt_path "$clone" 63)"
git_q "$clone" worktree add -q -b tdd/63-mine "$mine" main >/dev/null 2>&1
mkdir -p "$mine/.tdd"
printf '%s\n' '- [ ] step' > "$mine/.tdd/issue-63.md"
mkdir -p "$work/resume-claimed-gh"
printf '[{"body": "Closes #63", "state": "OPEN", "isDraft": true, "url": "https://example.test/pull/630"}]\n' > "$work/resume-claimed-gh/prs.json"

out="$(cd "$clone" && VERI_GH_JSON="$work/resume-claimed-gh" "$WT" 63 mine 2>/dev/null)" && code=0 || code=$?

{ [[ "$code" == 0 ]] && [[ "$out" == "$mine" ]]; } \
  && ok || no "#1656: a resume (worktree and ledger exist) still starts though its branch is on the remote and an open PR claims the issue (exit=$code want 0, stdout='$out' want '$mine')"

ahead_pair resume-silent
mine="$(wt_path "$clone" 65)"
git_q "$clone" worktree add -q -b tdd/65-mine "$mine" main >/dev/null 2>&1
mkdir -p "$mine/.tdd" "$work/resume-silent-gh"
printf '%s\n' '- [ ] step' > "$mine/.tdd/issue-65.md"

out="$(cd "$clone" && PATH="$work/stubbin:$PATH" STUB_LS_FAIL=1 VERI_GH_JSON="$work/resume-silent-gh" "$WT" 65 mine 2>/dev/null)" && code=0 || code=$?

{ [[ "$code" == 0 ]] && [[ "$out" == "$mine" ]]; } \
  && ok || no "#1672: a resume of the run's own issue branch still hands back its worktree when the ls-remote and open-PR lookups get no answer (exit=$code want 0, stdout='$out' want '$mine')"

ahead_pair ghe-claimed
mine="$(wt_path "$clone" 66)"
mkdir -p "$work/ghe-bin"
cat > "$work/ghe-bin/gh" <<'STUB'
#!/bin/sh
case "$*" in
  *[?\&]page=1) echo '[{"body": "Closes #66", "state": "OPEN", "url": "https://ghe.example.test/acme/veri/pull/660"}]' ;;
  *) echo '[]' ;;
esac
STUB
chmod +x "$work/ghe-bin/gh"
before="$(registry "$clone")"

errfile="$work/ghe-claimed.err"
out="$(cd "$clone" && PATH="$work/ghe-bin:$work/stubbin:$PATH" STUB_ORIGIN_URL="https://ghe.example.test/acme/veri.git" "$WT" 66 fresh-start 2>"$errfile")" && code=0 || code=$?
after="$(registry "$clone")"

{ [[ "$code" == 2 ]] && [[ -z "$out" ]] && grep -F 'pull/660' "$errfile" >/dev/null \
  && [[ ! -e "$mine" ]] && [[ "$after" == "$before" ]]; } \
  && ok || no "#1672: a fresh cut from a GitHub Enterprise origin (not github.com) runs the open-PR check: an open PR saying Closes #66 exits 2 naming that PR and creates no worktree (exit=$code want 2, stdout='$out' want empty, stderr='$(cat "$errfile")' want it to name 'pull/660', '$mine' $( [[ -e "$mine" ]] && echo "was created" || echo "absent, good" ), registry $( [[ "$after" == "$before" ]] && echo unchanged || echo changed ))"

ahead_pair fetched-claimed
git_q "$upstream" branch -q tdd/64-taken-over main >/dev/null 2>&1
git_q "$clone" fetch -q origin >/dev/null 2>&1
mine="$(wt_path "$clone" 64)"
fetched_ref="$(git_q "$clone" rev-parse --verify --quiet refs/remotes/origin/tdd/64-taken-over 2>/dev/null)"
before="$(registry "$clone")"

err="$(cd "$clone" && "$WT" 64 taken-over 2>&1 >/dev/null)" && code=0 || code=$?
after="$(registry "$clone")"

{ [[ -n "$fetched_ref" ]] && [[ "$code" == 2 ]] && [[ "$err" == *"tdd/64-taken-over"* ]] \
  && [[ "$err" == *"git branch tdd/64-taken-over origin/tdd/64-taken-over"* ]] && [[ ! -e "$mine" ]] \
  && [[ "$after" == "$before" ]]; } \
  && ok || no "#1734: a fresh call over a fetched remote-tracking ref of a branch origin holds exits 2 naming the branch and the git branch command that takes the run over, creating no worktree or branch (exit=$code want 2, fetched ref='$fetched_ref' want set, stderr='$err', '$mine' $( [[ -e "$mine" ]] && echo "was created" || echo "absent, good" ), git's worktree+branch registry $( [[ "$after" == "$before" ]] && echo unchanged || echo changed ))"

ahead_pair taken-over-resume
git_q "$upstream" branch -q tdd/65-took-over main >/dev/null 2>&1
git_q "$clone" fetch -q origin >/dev/null 2>&1
git_q "$clone" branch -q tdd/65-took-over origin/tdd/65-took-over >/dev/null 2>&1
git_q "$clone" switch -q -c scratch-65 tdd/65-took-over >/dev/null 2>&1
git_q "$clone" commit -q --allow-empty -m "local work" >/dev/null 2>&1
git_q "$clone" branch -q -f tdd/65-took-over scratch-65 >/dev/null 2>&1
git_q "$clone" switch -q main >/dev/null 2>&1
git_q "$clone" branch -q -D scratch-65 >/dev/null 2>&1
local_tip="$(git_q "$clone" rev-parse tdd/65-took-over)"
remote_tip="$(git_q "$clone" rev-parse refs/remotes/origin/tdd/65-took-over)"
mine="$(wt_path "$clone" 65)"

out="$(cd "$clone" && "$WT" 65 took-over 2>/dev/null)" && code=0 || code=$?
branch="$(git -C "$mine" branch --show-current 2>/dev/null)"
tip="$(git -C "$mine" rev-parse HEAD 2>/dev/null)"

{ [[ "$local_tip" != "$remote_tip" ]] && [[ "$code" == 0 ]] && [[ "$out" == "$mine" ]] \
  && [[ "$branch" == "tdd/65-took-over" ]] && [[ "$tip" == "$local_tip" ]]; } \
  && ok || no "#1734: a clone holding the local branch while origin holds it too and the remote-tracking ref is fetched still starts as a resume on the local tip (exit=$code want 0, stdout='$out' want '$mine', branch='$branch' want 'tdd/65-took-over', tip='$tip' want local $local_tip not remote $remote_tip)"

ahead_pair registered-resume
git_q "$upstream" branch -q tdd/66-registered main >/dev/null 2>&1
git_q "$clone" fetch -q origin >/dev/null 2>&1
mine="$(wt_path "$clone" 66)"
git_q "$clone" worktree add -q -b tdd/66-registered "$mine" origin/tdd/66-registered >/dev/null 2>&1
git_q "$mine" commit -q --allow-empty -m "local work" >/dev/null 2>&1
local_tip="$(git_q "$mine" rev-parse HEAD)"
remote_tip="$(git_q "$clone" rev-parse refs/remotes/origin/tdd/66-registered)"

out="$(cd "$clone" && "$WT" 66 registered 2>/dev/null)" && code=0 || code=$?
branch="$(git -C "$mine" branch --show-current 2>/dev/null)"
tip="$(git -C "$mine" rev-parse HEAD 2>/dev/null)"

{ [[ "$local_tip" != "$remote_tip" ]] && [[ "$code" == 0 ]] && [[ "$out" == "$mine" ]] \
  && [[ "$branch" == "tdd/66-registered" ]] && [[ "$tip" == "$local_tip" ]]; } \
  && ok || no "#1734: a clone with the issue's worktree registered while origin holds the branch and the remote-tracking ref is fetched still starts as a resume on the branch's own tip (exit=$code want 0, stdout='$out' want '$mine', branch='$branch' want 'tdd/66-registered', tip='$tip' want local $local_tip not remote $remote_tip)"

finish
