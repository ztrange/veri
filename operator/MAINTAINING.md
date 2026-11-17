# veri — maintaining notes

Sections moved out of the root `CLAUDE.md`, which every leaf loads, because no leaf role reads them;
they serve the operator and the human maintaining veri.

## Versions are tags, and nothing else

A version is an annotated tag `vN.M` whose message is the capability, in the issue's words —
no `VERSION` file, no changelog. One merged feature/fix issue is one minor bump, cut by the
`vmerge` skill; docs, test and refactor PRs get no tag.

- **`git tag --sort=-v:refname`, never plain `sort`** — lexically `v0.9` outranks `v0.10`.
- **Backfilling needs `GIT_COMMITTER_DATE`**, or retro-cut tags claim today's date.

## `make test` on the development Mac

- Suite stubs are `#!/bin/sh`, and per-leaf helpers are functions sourced from `scripts/lib/`
  (#322, #323): Homebrew bash starts slowly.
- The `test` recipe gives every suite `LC_ALL=C`, `< /dev/null` and a symlink to the real
  `git` first on PATH; remote git is refused by
  `protocol.allow=never`, `gh`/`curl` by the plugin `pytest_leg.py` loads.
- The pytest leg pins `TMPDIR` to `/tmp` before it starts, so a local run's scratch matches CI's
  rather than the Mac's `/var/folders/…` (#2354): the leg's `veri-pytest-*` run dir, `--basetemp`
  and so every case's `tmp_path` live under `/tmp`, whatever `TMPDIR` the caller set. The pycache
  prefix is unaffected (the Makefile computes it from the host `TMPDIR` before
  the leg starts), as are the full-run lock and `~/.veri-pytest-legs`.
- macOS checks each new executable on its first run (~330 ms). Fix:
  `sudo spctl developer-mode enable-terminal`, enable the terminal under Privacy & Security →
  Developer Tools, restart it. A Claude desktop session is not covered; launch conductors
  from the enabled terminal.
- A speed issue states its acceptance criteria as behaviours only; quote `make profile`
  before and after in the PR body. CI's `timeout-minutes` is the only wall-clock gate.
