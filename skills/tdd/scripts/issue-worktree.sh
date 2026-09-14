#!/usr/bin/env bash
# issue-worktree.sh — the linked git worktree an issue branch lives in.
#
# The conductor used to `git switch -c tdd/<n>-<slug>` in whatever checkout /tdd was
# invoked from, which drags that checkout off the default branch for the whole run: anything
# symlinked or served out of it (a user-level skill link, a dev server) silently starts seeing
# the issue branch. This creates a *linked worktree* instead — a second working directory that
# shares the one .git object store — and prints its absolute path, so the run can `cd` there
# and leave the caller's checkout exactly where it was.
#
# Usage:   issue-worktree.sh <n> <slug>
#          issue-worktree.sh --remove <n>
# Output:  the worktree's absolute path on stdout, exit 0.
set -euo pipefail

# git's own registry of worktrees — asked once here, questioned three times below. `worktree
# list --porcelain` prints one block per registered worktree, blank-line separated: a
# `worktree <absolute-path>` line first, then `HEAD <sha>`, then `branch <full-ref>` (absent
# when that worktree is detached).
#
# Captured into a variable rather than piped into each reader: `set -o pipefail` above would
# let git's exit code — including the SIGPIPE it takes when a reader stops early — decide the
# answer instead of the reader's. Each question below feeds it back in with <<<, a here-string,
# which hands one string to a command as its stdin without a pipeline.
registry="$(git worktree list --porcelain)"

# main_working_tree — the repository's main working tree, the one every other worktree is linked
# to. The **main working tree is always the first block** of the registry, so the answer is that
# block's `worktree <absolute-path>` line with the label taken off.
#
# ${registry%%$'\n'*} strips the longest match of "newline and everything after it" from the end,
# leaving that first line, and ${first_line#worktree } then takes the label off the front. The
# path git prints there is absolute and has its symlinks resolved (on macOS a /var/... path comes
# back as /private/var/...), which is the property this needs: git reports every worktree path
# that way, so the path we print matches what `git worktree list` will say about it.
#
# The two steps are a `local` and a print rather than two names in the script's own scope: what
# the first step yields is still `worktree /path/...`, label and all, and no name outside here
# should be able to hold that, because no name would be true of it. Behind the function there is
# one name for the one answer, and it says what the answer is.
main_working_tree() {
  local first_line="${registry%%$'\n'*}"
  printf '%s\n' "${first_line#worktree }"
}

# The issue worktree belongs to the repository's MAIN working tree, never to the checkout we
# happen to have been called from. `git rev-parse --show-toplevel`, which this used to ask,
# answers with the caller's own worktree — so a conductor started from a linked worktree (a
# Claude session checkout under .claude/worktrees/<name>, or any other second working directory)
# nested the run inside it: removing that session took the run's leaf logs with it, and a resume
# from the main clone computed the un-nested path, failed to find it registered, and then refused
# because the branch was checked out "somewhere else" (issue #166).
#
# Named `main_tree` and not `root`: every path below hangs off it, so the name is the one place
# a reader learns *whose* root it is. `root` is what this held back when it was --show-toplevel,
# and it reads equally true of the caller's checkout — which is exactly the reading that put the
# run inside a session worktree.
main_tree="$(main_working_tree)"

# wt_path <n> — where issue <n>'s worktree lives. The layout is stated once, here, because both
# halves of this script need it and a create that answered with a different path than the remove
# went looking for would be a silent no-op. `.tdd/` is already git-ignored, so nesting a worktree
# under it needs no new ignore rule.
wt_path() { printf '%s\n' "$main_tree/.tdd/wt/$1"; }

# --remove <n> takes the worktree back out again, once its branch is merged or a human says so.
# It is answered here, before the positional <n> <slug> parsing below, because that parsing
# would otherwise read the flag itself as the issue number.
if [[ "${1:-}" == "--remove" ]]; then
  n="${2:?usage: issue-worktree.sh --remove <n>}"
  path="$(wt_path "$n")"

  # Never destroy work. `git status --porcelain` prints one line per change — staged, unstaged
  # or untracked — and nothing at all when the tree is clean, so a non-empty answer is the
  # whole test. Asking before removing rather than letting `git worktree remove` refuse for us
  # is what makes this exit 2, "no answer could be obtained", instead of git's own 1: a
  # worktree with changes in it is not a removal that failed, it is one we must not attempt.
  if [[ -n "$(git -C "$path" status --porcelain)" ]]; then
    echo "issue-worktree: $path has uncommitted changes — refusing to remove it" >&2
    exit 2
  fi

  # No --force: with the tree clean git has nothing to object to, and leaving the safety net
  # in place means a change that lands between the check above and here still stops us.
  # >&2 keeps any chatter off stdout.
  git worktree remove "$path" >&2
  exit 0
fi

# ${1:?msg} — expand $1, but if it is unset or empty, die with msg on stderr instead of
# silently building a branch called `tdd/-`. The first argument carries the whole usage line
# and the rest just name themselves, which is how every other script here does it.
n="${1:?usage: issue-worktree.sh <n> <slug>}"
slug="${2:?missing <slug>}"

branch="tdd/$n-$slug"
path="$(wt_path "$n")"

# Idempotent: a second call for the same issue — a resume, or a conductor re-entering step 1 —
# answers with the path it already made instead of dying on `git worktree add`'s "already
# exists". grep -x -F asks the registry for that exact `worktree <path>` line, whole and
# literal (-F: no regex, so a `.` in the path is a dot). Asking git rather than `[[ -d $path ]]`
# matters — a leftover directory git no longer knows about is not a worktree we can hand back,
# and it must fall through to the add below.
if grep -qxF "worktree $path" <<<"$registry"; then
  printf '%s\n' "$path"
  exit 0
fi

# checkout_holder <branch> — the path of the worktree that has <branch> checked out, or nothing
# at all when no worktree does. Walks the registry line by line, remembering the path of the
# block it is inside, and answers with it when a branch line names the one asked about.
#
# `read -r key value` splits each line on whitespace into the first word and *all* the rest, so
# a path containing spaces still arrives whole in $value; -r stops backslashes being eaten.
# `local` keeps the walk's bookkeeping out of the rest of the script. The closing `return 0`
# pins the no-match answer to success: a while loop exits with the status of the last command
# its *body* ran (not the `read` that ended it), which here is an unmatched `if` and so happens
# to be 0 already — but it would be 1 if that line were ever reworked into a bare `[[ ]]`, and
# `set -e` would then kill the script on the ordinary "nobody holds this branch" case.
checkout_holder() {
  local key value seen=""
  while read -r key value; do
    case "$key" in
      worktree) seen="$value" ;;
      branch) if [[ "$value" == "refs/heads/$1" ]]; then printf '%s\n' "$seen"; return 0; fi ;;
    esac
  done <<<"$registry"
  return 0
}

# Never steal a checkout. If the branch is already checked out somewhere else, another
# conductor owns that run, so refuse with exit 2 — "no answer could be obtained" — and name the
# path, because it is the only thing that tells a human which run to go and look at.
holder="$(checkout_holder "$branch")"
if [[ -n "$holder" ]]; then
  echo "issue-worktree: branch $branch is already checked out in $holder — another conductor owns it" >&2
  exit 2
fi

# ref_exists <full-refname> — does this refname resolve in this repo? `show-ref --verify` wants
# the full refname and answers only through its exit code (--quiet suppresses the printed sha):
# 0 when the ref is there, non-zero when it is not.
#
# The two tests below are each half of one decision — is there already a branch for this issue,
# local or fetched — and they are asked of the same repository a line apart. Behind one name they
# cannot come to disagree about what "exists" means or about which exit code says so; written out
# twice, a `--quiet` dropped or a `2>/dev/null` added to one of them would change the answer on
# only one arm, and the arm that then ran would be the one nobody had looked at.
ref_exists() { git show-ref --verify --quiet "$1"; }

# branch_exists <name> — does this repo already carry a local branch called <name>? Asked twice
# below, of two different things: the issue branch (a resume), and each candidate default branch.
# Naming it keeps the refs/heads/ prefix — the part that makes --verify work at all — in one place.
branch_exists() { ref_exists "refs/heads/$1"; }

# remote_branch_ref <name> — the refname a branch called <name> fetched from origin lives under.
# The spelling is written once, here, for the reason wt_path's layout is written once: the test just
# below and the `git worktree add` that acts on its answer are two halves of one decision, and a test
# that asked about one ref while the add started from another would take that arm on evidence about a
# different branch — silently, because both spellings resolve to something git will happily check out.
remote_branch_ref() { printf '%s\n' "refs/remotes/origin/$1"; }

# remote_branch_exists <name> — does the remote carry a branch called <name> that this clone has
# fetched, when no local ref for it is left? That is what a run made on another machine and pushed
# looks like here after a `git fetch`: refs/remotes/origin/<name> and nothing under refs/heads/
# (issue #186). branch_exists answers no about it, and the cut-from-default arm below would then
# lay a brand-new branch over a name the remote already uses, abandoning every commit the previous
# run pushed — silently, because every script involved succeeds.
#
# A separate function rather than a second ref namespace inside branch_exists: that one is also
# what default_branch_name asks about `main` and `master`, where "we have fetched a remote copy of
# it" is not the question — it needs a local ref it can cut from.
remote_branch_exists() { ref_exists "$(remote_branch_ref "$1")"; }

# The branch is cut from the DEFAULT branch, never from HEAD — cutting from HEAD would inherit
# whatever the caller's checkout happened to be sitting on, which is the collision this script
# exists to prevent.
#
# With a remote the base is the REMOTE's tip, not the local branch of the same name, and it is
# fetched first (issue #174). The local `main` here lags `origin/main` by design: pulling the
# primary clone while a conductor is live would change the scripts running under it, so the pull
# waits (#165). A branch cut from that stale local ref starts out behind and its PR then owes a
# rebase over everything that landed meanwhile — replayed one `refactor:` commit at a time,
# through whatever conflicts concurrent issues left in the same files.
#
# `git fetch origin <default>` refreshes refs/remotes/origin/<default> and nothing else: it moves
# no local branch ref and touches no working tree, so #165's reason for not pulling stays intact.
#
# Two questions, asked by the two functions below, because they are not one question: what the
# default branch is CALLED is something this clone can answer on its own, while whether the base
# is the remote's copy of that branch turns on there being a remote at all.

# default_branch_name — the name the default branch carries, the same one on the remote side and
# locally. origin/HEAD is git's own record of it, and it comes back as `origin/main`, so
# ${head#origin/} strips the prefix (# removes the shortest match from the front) to leave just
# the name — which is the half of `origin/main` that `git fetch` takes.
#
# A repository can have an origin and carry no such symref: `git remote add` plus a fetch writes
# none, a clone taken before git started writing one has none, and `git remote set-head -d` takes
# it off. So the fallback to the two names git itself ships as defaults is not the "no remote"
# arm — it is the "nobody wrote down which branch it is" arm, and either kind of repository can
# reach it.
default_branch_name() {
  local head candidate
  if head="$(git symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null)"; then
    printf '%s\n' "${head#origin/}"
    return 0
  fi
  for candidate in main master; do
    if branch_exists "$candidate"; then
      printf '%s\n' "$candidate"
      return 0
    fi
  done

  # No origin/HEAD and no local main or master: nothing is left to name, so there is nothing to cut
  # from. Said here for the same reason the fetch's refusal is said where the fetch is — this is
  # the only place that knows which of the two ways out was taken, and once each has named itself
  # the caller does the same thing either way, so it needs no status to tell them apart.
  echo "issue-worktree: cannot determine the default branch (no origin/HEAD, no local main or master)" >&2
  return 2
}

# default_base — the one ref `git worktree add -b` is handed, and the name the caller binds.
#
# What decides between the two arms is whether an `origin` remote is CONFIGURED, never whether
# origin/HEAD is there to be read. Those look like the same question in a clone, which is how the
# symref came to stand in for it, but a repository with an origin and no symref is ordinary
# (#174) — and reading the symref as the test sends exactly that repository down the local arm,
# back to the stale `main` the fetch exists to get away from, silently and in the shape that
# looks like every other clone from the outside. `git remote get-url` asks git's configuration
# and nothing else, so a repository with no remote reaches no network for an answer it could not
# use — the observable case 17 pins by requiring stderr to stay silent.
default_base() {
  local name
  name="$(default_branch_name)" || return 2

  if ! git remote get-url origin >/dev/null 2>&1; then
    printf '%s\n' "$name"
    return 0
  fi

  # A fetch that fails is a refusal, never a fallback. refs/remotes/origin/<default> is still
  # there in the clone, pointing at whatever tip the last successful fetch left — so carrying on
  # would cut the branch from a base as stale as the local one this fetch exists to get away
  # from, and whether a run starts from the remote's tip would come to depend on whether the
  # network happened to be up. Return 2, the script's "no answer could be obtained": the remote
  # we were told to cut from could not be read. Said here, where the fetch is, because this is
  # the only place that knows the fetch was what broke; git's own message never says the word.
  # $name is what both the fetch and the message are built from, so the line a human trusts when
  # the remote is unreachable cannot come to name a fetch nobody ran.
  if ! git fetch -q origin "$name" >&2; then
    echo "issue-worktree: git fetch origin $name failed — refusing to cut $branch from a stale origin/$name" >&2
    return 2
  fi
  printf '%s\n' "origin/$name"
}

# worktree_add <args…> — the `git worktree add` all three arms below run, carrying the two
# things none of them may forget: -q, and git's own output on stderr. stdout here belongs to
# the single line the caller parses — the worktree's path — so an arm that dropped either
# would print "Preparing worktree" into that answer and the conductor would `cd` to it.
# Written once, the flags cannot come to differ between the arm a test exercised and the arm
# it did not, and the reason is read where it is enforced rather than at whichever arm
# happened to state it.
worktree_add() { git worktree add -q "$@" >&2; }

# One `git worktree add`, in one of three shapes, and a single print of the path afterwards —
# whichever shape ran, the caller parses the same line.
#
# A branch that already exists — a resume after the last run's worktree was removed, or one
# fetched back from the remote — gets checked out, not cut again. `git worktree add -b` refuses
# outright once the ref is there, and re-cutting it from the default branch would silently
# abandon whatever the previous run committed on it. Naming the branch as `add`'s second
# argument (no -b) is how git says "check this existing branch out here". The holder check above
# already established no other worktree has it, so taking it steals nothing.
if branch_exists "$branch"; then
  worktree_add "$path" "$branch"
elif remote_branch_exists "$branch"; then
  # Only on the remote: make the local branch at the remote's tip, so the worktree arrives carrying
  # the previous run's commits and — the part that decides whether a resume is even recognised as
  # one — its committed `.tdd/issue-<n>.md` ledger. The conductor's resume check asks whether that
  # file exists *in the worktree*, so a worktree cut from the default branch reads as a new run and
  # re-plans from scratch over work that is already on the remote.
  #
  # The start point is spelled out in full — remote_branch_ref names it — rather than left to git's
  # DWIM. `git worktree add <path> <branch>` does guess a unique refs/remotes/*/<branch> into a new
  # local branch — but that guess is off entirely under `checkout.guess=false` in a user's config,
  # and a behaviour this script depends on must not be one a config setting can take away without
  # a word.
  worktree_add -b "$branch" "$path" "$(remote_branch_ref "$branch")"
else
  # Exit 2 — "no answer could be obtained" — rather than guessing: a repo whose default branch we
  # cannot name is plumbing broken before any TDD cycle starts, not a step that legitimately failed.
  #
  # Two ways out of default_base — the fetch failed, or there was no default branch to name at all —
  # and both are that same exit. Each has already said which one it was on stderr, next to the
  # condition that knows, so nothing here has to tell them apart: adding a second message would only
  # bury the one line a human has to read.
  base="$(default_base)" || exit 2

  # -b creates the branch at <base> and checks it out in the new worktree in one move.
  #
  # --no-track: with $base now a remote-tracking ref (`origin/main`), git's default
  # branch.autoSetupMerge would read the shape as "you presumably want to track it" and write
  # branch.<name>.remote/.merge for the new branch — so `tdd/<n>-<slug>` would arrive tracking the
  # remote's default branch, and a bare `git pull` in the issue worktree would pull main into it
  # while a bare `git push` aimed at main on the remote. The branch that carries a PR points
  # nowhere by itself. This is a cost of the remote base, not of the old behaviour: a local `main`
  # set up no tracking at all, so the tracking arrives with the remote base and goes off with it.
  worktree_add --no-track -b "$branch" "$path" "$base"
fi

printf '%s\n' "$path"
