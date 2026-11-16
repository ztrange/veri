# Plan for #3937 — PRD 018.4: VERI_SKIP_VERIFY=diff lands ⟦diff-checked⟧ steps without verify-diff

- [ ] On a fresh launch with `VERI_SKIP_VERIFY=diff`, `run-conductor.sh` does not exit 2 over that word and writes `diff` to `.tdd/issue-<n>-skip-verify` ⟦criterion 1⟧
- [ ] `metrics.sh` counts `verify-diff-skipped reason=switched-off` events as `diff <n>` on the `Verifiers switched off:` line, one `<phase> <n>` pair per phase, comma-separated ⟦criterion 7⟧
- [ ] `skills/tdd/JOURNAL.md`'s event table lists `verify-diff-skipped` with its `reason` field (`switched-off`) beside `verify-refactor-skipped` ⟦criterion 9⟧
- [ ] skill-edit step for the unit `skills/tdd/DIFF-CHECKED.md`: add CY152 under `## skills/tdd/DIFF-CHECKED.md`, amend the verifier paragraph, grade and sign ⟦skill-edit⟧ ⟦criterion 10⟧
- [ ] skill-edit step for the unit `skills/tdd/REVISE.md`: check RV68 and RV69 against step 5 with `diff` skippable, name `verify-diff-skipped`, grade and sign ⟦skill-edit⟧ ⟦criterion 11⟧
- [ ] skill-edit step for the unit `skills/tdd/SKILL.md`: add CY153 under `## skills/tdd/SKILL.md`, amend *Green* sub-step 1's `supersede-diff` entry within the byte ceiling, grade and sign ⟦skill-edit⟧ ⟦criterion 12⟧
