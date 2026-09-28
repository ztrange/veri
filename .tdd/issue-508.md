# Plan for #508 — make test's 'never reached its count line' names the suite but not the line that came last, so a flake cannot be diagnosed

- [x] When a suite's last line of output is not a count line, `make test` still prints a line beginning `<suite>: never reached its count line` and that failure also quotes the suite's last output line verbatim ⟦criterion 1⟧
- [ ] When a suite prints no output at all, `make test` reports its output as empty rather than quoting an empty line ⟦criterion 2⟧
- [ ] When a suite's last line is its `<n> passed, <m> failed` count line, `make test` prints no never-reached-its-count-line failure for it, exactly as before ⟦criterion 3⟧
