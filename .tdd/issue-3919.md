# Plan for #3919 — PRD 029.4: the plan verifier is shown the touching cases

- [x] build-verify-prompt.sh plan adds, after the ledger, a `### Test cases touching the files the plan names` section listing, under a test file's repo-relative path, the names of its cases and no case body, when a step names a file by its repo-relative path and the test file holds that file's stem ⟦criterion 1⟧
- [x] a step naming a file by its basename alone lists the cases of the test files touching it ⟦criterion 1⟧
- [x] a test file holding the stem with `_` where the file name has `-` touches it ⟦criterion 1⟧
- [x] a test file holding the stem only inside a longer word contributes no case ⟦criterion 1⟧
- [x] with no step naming a file, or no test file touching one, the section is the one line `No test case touches a file the plan names.` ⟦criterion 2⟧
- [x] the section lists at most VERI_PLAN_TOUCHING_CASES case names (a TUNABLES entry, default 100), then one `<file>: <m> more cases` line per test file left over ⟦criterion 3⟧
- [x] a VERI_PLAN_TOUCHING_CASES that is not a whole number makes the plan phase exit 2 with one stderr line naming the knob and nothing on stdout ⟦criterion 4⟧
- [x] a test file under .git, .tdd, .venv or node_modules that touches a named file contributes no case ⟦criterion 5⟧
- [x] the plan input check also refuses a .tdd test file's marker, --step text and a fourth positional, watched red with the walk's .tdd skip removed ⟦criterion 6⟧
- [x] a touching test file that cannot be read, or whose case call never closes, contributes no case and the plan still renders
- [x] the plan phase lists only test files git tracks: an untracked file and one in a gitignored directory are not listed, a tracked one is ⟦criterion 1⟧
- [x] a git ls-files that fails makes the plan phase exit 2, not an empty section ⟦criterion 5⟧
- [x] a touching test file that is a symbolic link is skipped, never followed
- [ ] a tracked test-looking file the reader cannot read or cut, or in a language it does not read, gets one '<file>: cases not readable' line within the cap, and the section never then says no case touches a named file
- [ ] within the cap, files touching a file a step names by its full path come first, then by number of hits, then alphabetically ⟦criterion 3⟧
- [x] prompts/verify-plan.md explains the section and tells the verifier, in the older-cases check, to read those cases in the repository and apply the check to them ⟦skill-edit⟧ ⟦criterion 7⟧
- [x] SCRIPTS.md's build-verify-prompt.sh entry states the plan phase's touching cases, the matching rules, and VERI_PLAN_TOUCHING_CASES with its default ⟦skill-edit⟧ ⟦criterion 8⟧
