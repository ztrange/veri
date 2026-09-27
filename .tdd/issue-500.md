# Plan for #500 — the developer prompts stop writing rationale comments

- [x] Every developer prompt states the comment rule: a comment may only be a contract header (usage line and exit-code table) or a succinct warning where the shell itself is the hazard, and nothing else is written — no rationale, no issue archaeology, no restatement of the next line ⟦criterion 1⟧
- [x] Every developer prompt states where rationale goes instead of a comment: a test first, an ADR second, and nowhere third ⟦criterion 2⟧
- [x] The verify-green prompt tells the verifier to REJECT code carrying a rationale comment outside the two allowed classes ⟦criterion 3⟧
- [x] The verify-refactor prompt tells the verifier to REJECT code carrying a rationale comment outside the two allowed classes ⟦criterion 3⟧
- [x] The verify-green and verify-refactor prompts tell the verifier that a contract header or a shell-hazard warning is not grounds for REJECT ⟦criterion 4⟧
