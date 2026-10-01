# Plan for #498 — functionality reachable from no declared entry point is removed

Declared entry points: the script invocations in `skills/tdd/SKILL.md` and the procedure files it reads (`SCOPE-LOOP.md`, `WORKER.md`), the Makefile's targets, and the git hooks under `docs/hooks/`.

- [x] `skills/tdd/scripts/unreachable.sh <repo-root>` lists, one per line, each script under `skills/tdd/scripts/` reachable from none of the declared entry points, including one whose only callers are other scripts inside the same orphaned subtree ⟦added⟧ ⟦criterion 1⟧
- [x] unreachable.sh matches a script name as a whole name, not a substring: an orphan whose name is the tail of a reached script's name (e.g. `leaf.sh` beside a reached `run-leaf.sh`) is still listed ⟦added⟧ ⟦criterion 1⟧
- [x] `skills/tdd/scripts/unreachable.sh` run with no `<repo-root>` argument exits 2 with a usage line on stderr and prints nothing on stdout, and it is on the list of scripts `skills/tdd/scripts/tests/unit/missing-argument-exit.test.sh` checks ⟦added⟧ ⟦criterion 1⟧
- [x] a script reached from exactly one kind of entry point — only SKILL.md (or a procedure file it reads), only a Makefile recipe, or only a git hook — directly or through a chain of other scripts or sourced `lib/` files, is not listed by unreachable.sh ⟦criterion 1⟧
- [x] unreachable.sh counts a dynamically constructed invocation as reaching its target — a script or prompt template named only through a built path such as `"$S/build-$kind-prompt.sh"` or `prompts/develop-$phase.md` is not listed, on a fixture where a literal `grep -F` for the target's name finds no caller ⟦criterion 2⟧
- [ ] a script whose only caller is its own test suite is listed by unreachable.sh as test-only, apart from the unreachable ones, and running the check deletes and modifies no file ⟦criterion 4⟧
- [ ] a `VERI_*` knob or a script name that SKILL.md or CLAUDE.md promises and that no script reads, or that does not exist, is listed by unreachable.sh as promised-unread ⟦criterion 5⟧
- [ ] `make unreachable` runs unreachable.sh over this repository and exits 0, so the check is itself reached from a declared entry point
- [ ] every script unreachable.sh lists as unreachable in this repository is removed together with any suite whose every assertion is about it, and the check then lists no unreachable script ⟦criterion 3⟧
- [ ] `make test` is green and no reachable behaviour changes ⟦full-suite⟧ ⟦criterion 6⟧

## Owed steps

- a built path whose file name is only a variable, such as `"$S/$name.sh"` or `prompts/$1.md`, does not count as reaching every file of that extension: an orphan beside such a caller is still listed by unreachable.sh
