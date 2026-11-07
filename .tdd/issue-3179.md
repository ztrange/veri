# Plan for #3179 — A leaf prompt names the test command twice: name it once

- [x] A developer leaf prompt rendered by build-develop-prompt.sh from a spec whose body carries a `Test command: <cmd>` line names the test command once: the spec it renders omits that line, while the prompt's own test-command section still gives the run's command (a small case in tests/py/unit/test_build_develop_prompt.py on a rendered red prompt; no template or graded unit changes) ⟦criterion 1⟧ ⟂ refactor pending
