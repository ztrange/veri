---
name: voutage
description: >-
  Hold merges through a GitHub incident: read by the dev session, by path, when a merge fails for a reason `vmerge` does not name.
---

# voutage — hold merges through a GitHub outage

Obeys `operator/PRINCIPLES.md` under the veri clone root (`git -C <base dir> rev-parse --show-toplevel`); read it first.

`$S` is `skills/tdd/scripts/`, reached from this skill's base directory as `../tdd/scripts/`;
in a command, write it as that directory's absolute path.
Every command runs from the target repository's main working tree, and every `.tdd/` path is
under it. Each command below works alone: Bash calls share no shell variables, so nothing is
carried from one call to the next but what the files hold.

The dev session reads this skill itself, never through a subagent, since it acts on the
session's own state. It reaches it after `vmerge`'s own handling of the failed merge is over
(its settle read, its one lock release): this skill takes no merge lock and releases none.

## The mode is a file

*Local mode* is the file `.tdd/github-outage` in the target repository's **main** working tree,
and nothing else: re-read it (P1), never remember it. While it exists, merges are held; when it
is gone, they are not. Every command below therefore starts by going to the main working tree,
from wherever the call starts, a linked worktree included (git's common directory is the main
working tree's `.git`):

```bash
cd "$(git rev-parse --path-format=absolute --git-common-dir)/.." && test -f .tdd/github-outage
```

(exit 0: on; exit 1: off.) Its lines are the output lines of `$S/github-status.sh` that started
the mode, then the PR urls, one per line, then the marker line `-- held after review --`, then
more PR urls. A PR url is a line that is exactly `https://…/pull/<digits>`; no other line is ever
merged. Above the marker are the PRs held because their merge failed, in the order they failed;
below it, the PRs of runs held after their review, in the order the runs ended. The file's PR
urls, top to bottom, are the merge order: the failed PR's first.

`.tdd/github-outage-merging` lists the PRs taken off the file whose merge has been started and
not yet finished, so a reset between the two loses none.

**The file tool.** Every read or change of either file is this one command, run with a verb.
It takes a lock on the file, then checks that the file it holds is still the one on disk (a file
removed meanwhile is no file), reads every line with a trailing `\r` stripped and a last line
without a newline counted whole, and rewrites the file under the same lock, so a concurrent
change is never lost:

```bash
cd "$(git rev-parse --path-format=absolute --git-common-dir)/.." && perl -e 'my ($v, $u) = @ARGV; my $pr = qr{\Ahttps://\S+/pull/[0-9]+\z}; my $m = "-- held after review --"; my $p = ($v eq "merging" || $v eq "merged") ? ".tdd/github-outage-merging" : ".tdd/github-outage"; open(my $f, "+<", $p) or exit 3; flock($f, 2); exit 3 unless (stat $f)[3]; my @l = map { s/\r?\n?\z//r } <$f>; my $say = ""; if ($v eq "list" || $v eq "merging") { print map { "$_\n" } grep { $_ =~ $pr } @l; exit 0 } if ($v eq "first" || $v eq "last") { exit 2 unless $u =~ $pr; exit 0 if grep { $_ eq $u } @l; my ($i) = grep { $l[$_] eq $m } 0 .. $#l; splice(@l, ($v eq "first" && defined $i) ? $i : scalar @l, 0, $u) } elsif ($v eq "take") { my ($i) = grep { $l[$_] =~ $pr } 0 .. $#l; if (!defined $i) { unlink($p) or exit 2; print "ended\n"; exit 0 } my ($t) = splice(@l, $i, 1); open(my $g, ">>", ".tdd/github-outage-merging") or exit 2; flock($g, 2); print $g "$t\n"; close($g) or exit 2; $say = "$t\n" } elsif ($v eq "merged") { exit 2 unless $u =~ $pr; @l = grep { $_ ne $u } @l } elsif ($v eq "no-answer") { if (grep { $_ eq "no-answer" } @l) { print "told\n"; exit 0 } push @l, "no-answer"; $say = "tell\n" } elsif ($v eq "answered") { @l = grep { $_ ne "no-answer" } @l } else { exit 2 } seek($f, 0, 0); truncate($f, 0); print $f map { "$_\n" } @l; close($f) or exit 2; print $say' <verb> [<pr-url>]
```

Exit 3 from any verb: that file does not exist (for `.tdd/github-outage`: local mode is off).
Exit 2: a bad verb or url, or a write that failed. The verbs:

- `list`: print the held PR urls, in order.
- `first <pr-url>`: hold a PR whose merge failed: put it just above the marker, after the PRs
  already held that way, so they stay in the order they failed. `last <pr-url>`: hold a reviewed
  run's PR at the end. A url already held is not added again.
- `take`: take the first held PR off the file and add it to `.tdd/github-outage-merging`, printing
  its url; with no PR left, remove `.tdd/github-outage` and print `ended`.
- `merging`: print the PR urls in `.tdd/github-outage-merging`. `merged <pr-url>`: take one off it.
- `no-answer`: print `tell` and record the marker line `no-answer` in the file, or print `told`
  when it is already there. `answered`: remove that line.

## On a failed merge

Run the one-shot check on the components a merge needs (the script's default, so no component
argument), in one command that writes the file only on exit 1 and only when none exists yet:

```bash
cd "$(git rev-parse --path-format=absolute --git-common-dir)/.." && { out=$($S/github-status.sh < /dev/null); rc=$?; printf '%s\n' "$out" "exit $rc"; if [ "$rc" = 1 ]; then (set -C; printf '%s\n' "$out" '<pr-url>' '-- held after review --' > .tdd/github-outage) 2>/dev/null && echo created; fi; }
```

- **Exit 1, `created`.** A counting incident: the script printed one tab-separated line per
  incident (its name, the matched components, its local start, its age in minutes), and the file
  now holds those lines and the failed PR's url. Local mode has begun: tell the human (the
  coordinator, when one is attached, P4) in one line, naming the incident, e.g.
  `Local mode: GitHub incident "<name>" (<age> min); merges held`. Then arm the wait
  (*The wait*).
- **Exit 1, no `created`.** The file already existed, so local mode was already on: hold the
  failed PR with the file tool's `first`, and arm the wait. Nothing is told: the mode did not
  change. When `first` exits 3, the file vanished between the two commands: run this check again
  from the top, at most twice in all; after that, tell the human in one line that the PR's merge
  failed and the outage file kept vanishing.
- **Exit 0.** No counting incident: write no file. Report the failed merge in one line as an
  unexplained merge failure, with the `young <minutes> <name>` lines the script printed, if any.
- **Exit 2, or any other exit** (127 included). The status page gave no answer (the cause is on
  stderr). Leave the mode as it is: create no file, and leave an existing one in place. Tell the
  human in one line that the status page gave no answer.

On exit 0 or 2 the failed PR is not held; the one line to the human names it.

## While the file exists

No merge starts. A run that ends ✅ Done is reviewed as usual; on a review that is OK (the
caveats exchanged as for any merge) it is not merged: hold its PR with the file tool's `last`, in
the order the runs ended. A run whose review is not OK is handled as without this skill, and is
not held. When `last` exits 3 the file is gone: local mode ended meanwhile, so merge the run as
usual.

## The wait

Exactly one wait runs per main working tree while the file exists, shared by every session on
that tree, detached so it outlives a reset:

```bash
cd "$(git rev-parse --path-format=absolute --git-common-dir)/.." && $S/detach-command.sh start github-outage-wait $S/github-status.sh wait 3600
```

It writes its pid to `.tdd/github-outage-wait.pid`, its output to `.tdd/github-outage-wait.out`
and, when it ends, its exit code to `.tdd/github-outage-wait.exit`. It is live when this prints
`live`:

```bash
cd "$(git rev-parse --path-format=absolute --git-common-dir)/.." && { kill -0 "$(head -n 1 .tdd/github-outage-wait.pid 2>/dev/null)" 2>/dev/null && echo live || echo none; }
```

**Arm the wait**: when the check prints `none`, start it; then wait on it, live or just started,
with this, run as one background command, as `dispatch.sh` is, never under a Monitor and never a
hand-written script or sleep loop (P3); its exit is what tells you:

```bash
cd "$(git rev-parse --path-format=absolute --git-common-dir)/.." && $S/detach-command.sh wait github-outage-wait 3660
```

Nothing is ever killed: a live wait is waited on, never stopped. When the background command
exits, first run the `test -f` command above; when the file is gone, local mode already ended:
arm nothing, say nothing. Otherwise route its exit:

- **Exit 1** (the wait ended with a non-zero code, which `detach-command.sh` printed):
  - **Code 3.** The incident is still open after an hour: run the file tool's `answered`, then
    arm the wait again. Nothing is told.
  - **Code 2, or any other code.** No read in that hour got an answer: run the file tool's
    `no-answer`; on `tell`, tell the human in one line that the status page gave no answer for an
    hour (on `told` nothing is said: the file remembers it was told); arm the wait again.
- **Exit 0.** The wait ended with code 0: no counting incident is open, and its lines are in
  `.tdd/github-outage-wait.out`. Leave local mode (*Leaving local mode*).
- **Exit 3.** The background command's own hour passed with the wait still live: run that
  background command again.
- **Exit 2.** Run the live check. `none`: the wait died without an exit code; arm the wait
  again. `live`: `.tdd/stop` holds `now`, which ends every `detach-command.sh wait`; tell the
  human in one line and arm nothing.

## Starting, recovering or resuming with the file present

A session that starts, recovers from a reset or resumes from a handoff runs no one-shot check.
First it finishes what was in flight: each url the file tool's `merging` prints is merged
through `vmerge` and then taken off with `merged <pr-url>`, in that order, before anything else.
Then, while `.tdd/github-outage` exists, it is in local mode: it arms the wait (live: wait on it;
`none`: start it, then wait on it).

## Leaving local mode

On the wait's exit 0, with the file present, merge the held PRs in the file's order, one at a
time, each through `vmerge` as a ✅ Done run is merged (its review was done before it was held).
The take-off is the claim, so two sessions on one tree never merge the same PR:

1. Run the file tool's `take`. It prints a url: that PR is now off the file and listed in
   `.tdd/github-outage-merging`; go to step 2. It prints `ended`: the last held PR was taken
   and the file removed, under the same lock, so no PR held meanwhile is lost; go to step 3.
   Exit 3: the file was already gone; go to step 3. Exit 2: report it once and stop.
2. Merge that PR through `vmerge`. When `vmerge` has reported, whatever it reported, run the file
   tool's `merged <pr-url>`. When the merge did not land for a cause other than red CI, a rebase
   conflict, a refused push or a billing block, it comes back through *On a failed merge*: when
   that holds it again (`first`), the incident is back: stop here, the wait it arms will resume
   the rest. Otherwise go back to step 1.
3. Tell the human in one line that local mode has ended.

A merge `vmerge` refuses for red CI, a rebase conflict, a refused push or a billing block is
handled as `vmerge` says. A reset mid-way loses nothing: the file still lists the PRs not yet
taken, `.tdd/github-outage-merging` the ones taken whose merge had not finished, and the
recovered session finishes those, then waits on the wait, which exits 0 at its first read.
