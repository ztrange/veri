---
name: voutage
description: >-
  Hold merges through a GitHub incident: read by the dev session, by path, when a merge fails for a reason `vmerge` does not name.
---

# voutage — hold merges through a GitHub outage

Obeys `operator/PRINCIPLES.md` under the veri clone root (`git -C <base dir> rev-parse --show-toplevel`); read it first.

`$S` is `skills/tdd/scripts/`, reached from this skill's base directory as `../tdd/scripts/`.
Every command runs from the target repository's main working tree, and every `.tdd/` path is
under it. Each command below works alone: Bash calls share no shell variables, so nothing is
carried from one call to the next but what the file holds.

The dev session reads this skill itself, never through a subagent, since it acts on the
session's own state. It reaches it after `vmerge`'s own handling of the failed merge is over
(its settle read, its one lock release): this skill takes no merge lock and releases none.

## The mode is a file

*Local mode* is the file `.tdd/github-outage`, and nothing else: re-read it (P1), never remember
it. While it exists, merges are held; when it is gone, they are not. Its lines are the output
lines of `$S/github-status.sh` that started the mode, then one PR url per line, the failed PR's
first: the file's PR urls, top to bottom, are the merge order.

- **Is it on:** `test -f .tdd/github-outage` (exit 0: on; exit 1: off).
- **Its PRs, in order:** `grep '^https://' .tdd/github-outage`.
- **Hold a PR** (`last` appends; `first` puts it before the file's first PR url). The change is
  made under a lock on the file, so a concurrent addition is never lost, and a url already listed
  is not added again:

  ```bash
  perl -e 'my ($at, $u) = @ARGV; open(my $f, "+<", ".tdd/github-outage") or exit 3; flock($f, 2); exit 3 unless (stat $f)[3]; my @l = <$f>; exit 0 if grep { $_ eq "$u\n" } @l; my $i = @l; if ($at eq "first") { for (0 .. $#l) { if ($l[$_] =~ m{^https://}) { $i = $_; last } } } splice(@l, $i, 0, "$u\n"); seek($f, 0, 0); truncate($f, 0); print $f @l' last '<pr-url>'
  ```

  Exit 0: the PR is held. Exit 3: there is no file (local mode has ended), so nothing is held.

## On a failed merge

Run the one-shot check on the components a merge needs (the script's default, so no component
argument), in one command that writes the file only on exit 1 and only when none exists yet:

```bash
out=$($S/github-status.sh < /dev/null); rc=$?; printf '%s\n' "$out" "exit $rc"; if [ "$rc" = 1 ]; then (set -C; printf '%s\n' "$out" '<pr-url>' > .tdd/github-outage) 2>/dev/null && echo created; fi
```

- **Exit 1, `created`.** A counting incident: the script printed one tab-separated line per
  incident (its name, the matched components, its local start, its age in minutes), and the file
  now holds those lines and the failed PR's url. Local mode has begun: tell the human (the
  coordinator, when one is attached, P4) in one line, naming the incident, e.g.
  `Local mode: GitHub incident "<name>" (<age> min); merges held`. Then start the wait
  (*The wait*).
- **Exit 1, no `created`.** The file already existed, so local mode was already on: hold the
  failed PR with the command above and `first`, and leave the rest of the file as it is. Start
  the wait only when none runs (*The wait*). Nothing is told: the mode did not change.
- **Exit 0.** No counting incident: write no file. Report the failed merge in one line as an
  unexplained merge failure, with the `young <minutes> <name>` lines the script printed, if any.
- **Exit 2.** The status page gave no answer (the cause is on stderr). Leave the mode as it is:
  create no file, and leave an existing one in place. Tell the human in one line that the status
  page gave no answer.

On exit 0 or 2 the failed PR is not held; the one line to the human names it.

## While the file exists

No merge starts. A run that ends ✅ Done is reviewed as usual; on a review that is OK (the
caveats exchanged as for any merge) it is not merged: hold its PR with `last`, in the order the
runs ended. A run whose review is not OK is handled as without this skill, and is not held. When
holding exits 3 the file is gone: local mode ended meanwhile, so merge the run as usual.

## The wait

Exactly one background wait runs while the file exists:

```bash
$S/github-status.sh wait 3600
```

Start it as one background command, as `dispatch.sh` is started, never under a Monitor and
never a hand-written script or sleep loop (P3); its exit is what tells you. A wait is running
when `pgrep -f 'github_status.py wait'` prints a pid. Route its exit, after checking
`test -f .tdd/github-outage`; when the file is gone, local mode already ended: start nothing,
say nothing.

- **Exit 3.** The incident is still open after an hour: start the wait again. Nothing is told.
- **Exit 2.** No read in that hour got an answer: tell the human once, in one line, that the
  status page gave no answer for an hour; start the wait again. A later exit 2 in a row is not
  told again.
- **Exit 0.** No counting incident is open: merge the held PRs (*Leaving local mode*).
- **Any other exit** (a wait this session stopped, below): start nothing.

At every slot decision while the file exists, a `pgrep` that prints nothing means no wait runs:
start it.

## Starting, recovering or resuming with the file present

A session that starts, recovers from a reset or resumes from a handoff while
`.tdd/github-outage` exists is in local mode: it runs no one-shot check. It stops any wait left
from before the reset, whose exit would reach no one (`pkill -f 'github_status.py wait'`), then
starts the wait.

## Leaving local mode

On the wait's exit 0, with the file present, merge the held PRs in the file's order, one at a
time, each through `vmerge` as a ✅ Done run is merged (its review was done before it was held):

1. Read the first held PR: `grep -m1 '^https://' .tdd/github-outage`. Nothing printed (exit 1):
   go to step 3.
2. Start its merge through `vmerge`. Once it is started, take it off the file:

   ```bash
   perl -e 'open(my $f, "+<", ".tdd/github-outage") or exit 3; flock($f, 2); my @l = grep { $_ ne "$ARGV[0]\n" } <$f>; if (my ($n) = grep { m{^https://} } @l) { seek($f, 0, 0); truncate($f, 0); print $f @l; print "next $n"; exit 0 } unlink(".tdd/github-outage") or exit 2; print "ended\n"' '<pr-url>'
   ```

   `next <url>`: merge that PR the same way (step 2). `ended`: the merge of the last held PR
   has started and the file is removed, under the same lock, so no PR held meanwhile is lost.
   Exit 3: the file was already gone. Exit 2: the file could not be removed; report it once.
3. With the file removed (`test -f .tdd/github-outage` exits 1), tell the human in one line
   that local mode has ended.

A held PR whose merge fails again arrives as another `merge-failed` line and comes back here
through *On a failed merge*: a new counting incident starts local mode again with that PR first;
anything else is reported as that section says. A held PR `vmerge` refuses for a reason of its
own (red CI, a rebase conflict, a refused push, a billing block) is handled as `vmerge` says.
A reset mid-way loses nothing: the file still lists the PRs whose merge has not started, and the
recovered session's wait exits 0 at its first read.
