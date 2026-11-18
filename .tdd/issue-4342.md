# Plan for #4342 — PRD 038.1: records are caches, and a stage done by hand hands back through seam-settle.sh

- [x] ledger.same_step reads two step texts as one step when they differ only by ⟦…⟧ marks and a trailing ⟂ suffix ⟦criterion 3⟧
- [x] seam_contract names, per record-writing stage, the keys the next stage reads that have no committed source ⟦criterion 5⟧
- [x] after seam-settle.sh red-half test_path=… target_test=…, green-half.sh launches develop-green with those values ⟦criterion 7⟧
- [x] seam-settle.sh writes green-half's and refactor-half's records in their formats, the step from the ledger and green_sha from git ⟦criterion 6⟧
- [x] seam-settle.sh exits 2 naming an unknown stage, or a missing, unknown or empty key ⟦criterion 6⟧
- [x] script-help.sh seam-settle.sh prints the seam-contract table ⟦criterion 5⟧
- [x] green-half.sh compares its record's step with the open step through ledger.same_step ⟦criterion 3⟧
- [x] green-half.sh takes the open step from the ledger and rewrites a stale step in its record ⟦criterion 1⟧
- [x] each record rewrite writes one record-refreshed event naming the stage, the key, and the old and new values ⟦criterion 2⟧
- [x] green-half.sh exits 1 with the seam line when its record is missing or names another step ⟦criterion 4⟧
- [x] refactor-half.sh runs after a plan rewrite that changed only the open step's ⟦…⟧ marks (#4310) ⟦criterion 8⟧
- [x] refactor-half.sh reads green-half's record and takes green_sha from git, rewriting a stale one ⟦criterion 1⟧
- [x] refactor-half.sh exits 1 with the seam line naming green-half when its record is missing ⟦criterion 4⟧
- [x] step-close.sh takes the step, green_sha and verdict from their sources and rewrites a stale record ⟦criterion 1⟧
- [x] step-close.sh exits 1 with the seam line naming refactor-half when its record is missing ⟦criterion 4⟧
- [x] SKILL.md's Red, Green and Refactor hand paths end with their seam-settle.sh call, within the size ceiling ⟦criterion 9⟧
- [ ] no value seam-settle.sh writes reaches build-verify-prompt.sh, whose inputs and guard cases are unchanged ⟦criterion 10⟧
