# Plan for #1298 — orchestrate.test.sh's #1126 SIGTERM-group case still flakes on CI after #1232 and #1247

- [ ] The #1126 SIGTERM-group case in orchestrate.test.sh orders its two events by construction: the writer on the conductor's stdout cannot write again after orchestrate.sh's budget stop is triggered until the group's SIGTERM has been delivered to it, so the case can no longer observe a closed stdout before that SIGTERM lands, and it still expects `writer 143`; no other case and no production code changes ⟦diff-checked⟧ ⟦criterion 1⟧
