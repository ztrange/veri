"""Did a leaf change the repository, and put it back: the verifier's tree guard.

A verifier leaf must change nothing. `verify` snapshots the repository before the leaf runs, asks the guard
what changed after each run, and has the guard put a changed tree back before relaunching or refusing.
The guard returns values and prints nothing; the refusal lines are `verify`'s.

Interface:
- `snapshot(record=None, root=None)` -> `Guard`, or `Unreadable` / `ConfigUnreadable` when the before-state
  cannot be read. `record` is the absolute path of a pin's own mutation record, the one file the leaf may
  append to; `root` is what that record's path and the commands it records are resolved against.
- `Guard.tree`: the before tree's sha, "" when none was taken (not a repository, git missing, a failing
  `add`): then no tree, HEAD or untracked check is made.
- `Guard.changes()` -> the first finding, in this order: `Unreadable(detail)` (the tree after cannot be
  written), `Changed(paths, before, after)`, `ConfigUnreadable(path, strerror)`, `ConfigChanged(path)`;
  None when nothing changed.
- `Guard.restore(changed)` -> False when a moved HEAD could not be put back, else True.
- `Guard.restore_unreadable()` -> git's complaint naming the file that cannot be read.

Semantics:

| What | How |
|---|---|
| tree | `git add -A` then `git write-tree` into a temporary `GIT_INDEX_FILE` (a fresh directory outside the repo per call); "" when either fails |
| tree unreadable | an empty before tree whose `git add -A` (`LC_ALL=C`) fails saying `Permission denied`; its stderr is the detail |
| HEAD | `git rev-parse --verify HEAD` |
| untracked | `git ls-files --others --exclude-standard -z` |
| config | the bytes of `$HOME/.gitconfig`, None when absent; any other read error is `ConfigUnreadable` |
| changed paths | `git diff-tree -r -z --name-only --no-commit-id <before> <after>`, then `HEAD` when it moved |
| mode flip | a path whose only change is 100644 <-> 100755 (`git diff --raw -z --no-renames`) is chmod-ed back on the spot and not reported |
| own record | when the only changed path is the record, it was a regular file or absent before and its new bytes start with its old ones, the append is no change unless it records a command reaching outside `root`: each such command is reported as `command <line>` |
| unreadable after | a non-empty before tree and an empty after tree |
| restore (changed) | `read-tree -u --reset <before>` in a temporary index (after `add -A` into it), then `git update-ref HEAD <head-before>` when HEAD moved |
| restore (unreadable) | `read-tree <before>` and `checkout-index -a -f` in a temporary index, read the complaint, then remove each path untracked now but not before |
| config changed | the bytes differ; never restored |
"""
