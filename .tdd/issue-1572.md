# Plan for #1572 — affected-suites.sh never selects the prompt renderers' suites when a prompt template changes

- [x] Given a range whose only change is one `skills/tdd/scripts/prompts/develop-*.md` template, `affected-suites.sh` prints `tests/build-develop-prompt.test.sh`, `tests/build-verify-prompt.test.sh`, `tests/py/test_build_develop_prompt.py` and `tests/py/test_build_verify_prompt.py`, in addition to what it prints today (pytest case in `tests/py/test_affected_suites.py`, small) ⟦criterion 1⟧
- [x] Given a range whose only change is one `skills/tdd/scripts/prompts/verify-*.md` template, `affected-suites.sh` prints the same four renderer suites, in addition to what it prints today (pytest case, small) ⟦criterion 1⟧
- [x] Given a range whose only change is one `skills/tdd/scripts/prompts/_*.md` partial, `affected-suites.sh` prints the same four renderer suites, in addition to what it prints today (pytest case, small) ⟦criterion 1⟧
- [ ] When one of the four renderer suites does not exist in the tree, a prompt-template change prints the ones that exist and never the missing one (pytest case, small) ⟦criterion 1⟧
- [ ] Given a range that touches no file under `skills/tdd/scripts/prompts/`, `affected-suites.sh` prints none of the four renderer suites on that account (pytest case, small) ⟦criterion 2⟧
