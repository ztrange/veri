# Plan for #145 — A quoted Test-command marker in an issue's prose is taken as the test command, so a leaf can be handed a prose fragment or a docs suite

- [x] A body whose first marker is inside a backtick span, and whose later line states the marker with `make test`, answers `make test` — and the script header's rule-0 paragraph says why a quoted marker is skipped
- [x] A body whose only marker is inside a backtick span falls through to the next rule, exactly as a body with no marker does
- [x] A line carrying a quoted marker followed by a stated marker with `` `make docs-test` `` answers `make docs-test`
- [x] A development issue whose prose quotes a docs issue's marker with `make docs-test`, and whose Notes state the marker with `make test`, answers `make test`
- [x] #144's body as of 2026-09-13 (a fixture copy) answers `make test`
