# Plan for #4111 — PRD 031.5: a region with no seam gets one bounded dependency-breaking edit

- [x] `build-develop-prompt.sh break` renders `prompts/develop-break.md`; `break` is in `PHASES`, `WANT` and `REVISABLE_PHASES` ⟦criterion 1⟧
- [x] `build-verify-prompt.sh break <base-sha>` renders `prompts/verify-break.md`, exit 2 for a value not matching `^[0-9a-f]{7,40}$`; `break` is in `PHASES` and `NEEDS` ⟦criterion 2⟧
- [x] docs: `LEGACY.md` catalogue and the break procedure, `develop-break.md`, `verify-break.md`, rows and grades ⟦criterion 3⟧ ⟦criterion 4⟧ ⟦criterion 5⟧
