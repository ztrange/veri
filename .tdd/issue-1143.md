# Plan for #1143 — test_build_verify_prompt.py: the blindness-contract and full-suite assertions match one line at a time

- [x] test_build_verify_prompt.py's blindness-contract assertion on the red prompt needs its whole match on one line of the rendered prompt: a red prompt whose contract sentence is split across two lines, or whose `never` and `reason` sit on different lines, makes the case fail ⟦criterion 1⟧
- [x] test_build_verify_prompt.py's full-suite assertion on the green prompt needs its whole `full … test … suite` match on one line of the rendered prompt: a green prompt with `full test` on one line and `suite` on the next makes the case fail ⟦criterion 1⟧
