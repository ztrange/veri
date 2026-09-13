# Plan for #131 — A 'Test command:' written the way veri's issues write it — mid-line, in backticks — is not recognised, so a docs issue's leaves get make test and a timeout sized for it

- [x] a body line with `Test command:` mid-line followed by a backtick span answers the command inside the backticks, and nothing before the marker or after the closing backtick
- [x] a line that starts `Test command:` followed by a backtick span and more prose answers only the command inside the backticks
- [x] a bare `Test command: <cmd>` at line start, with no backticks, still answers `<cmd>` verbatim, and a body with no marker still falls through to the old precedence
- [x] the real bodies of #71, #75, #80 and #123, saved as fixtures under the suite, each answer `make docs-test`
