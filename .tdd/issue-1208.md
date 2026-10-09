# Plan for #1208 — orchestrate.test.sh's #1126 SIGPIPE case flakes on CI: the writer records -1, not 143

- [x] The #1126 SIGTERM-to-process-group case in orchestrate.test.sh records the writer's exit status before the case reads it, so under any scheduling it never reads -1, and still tells 143 (SIGTERM) from 141 (SIGPIPE) ⟦diff-checked⟧ ⟦criterion 1⟧
- [x] The repaired case has been watched go red: the conductor made to die of SIGPIPE on purpose, the case seen failing, the fix restored ⟦human-owed⟧ ⟦criterion 2⟧
