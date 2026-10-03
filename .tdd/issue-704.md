# Plan for #704 — Prose and guard suites share one helper library

- [x] A shared window helper in tests/lib/ prints one ±250-character window per occurrence of a pattern, so two occurrences 100 characters apart each get a window of their own, pinned by a fast-tier case; the six suites that defined win/window/windows source it instead of their copies ⟦criterion 3⟧
- [x] windows() in tests/lib/window.sh terminates on a pattern that can match the empty string (such as x*) instead of looping forever, pinned by a fast-tier case ⟦added⟧ ⟦criterion 3⟧
- [x] A copies guard (no-report-copies.test.sh or a sibling under tests/unit/) names <suite>:<line> for any suite under tests/ or tests/unit/ that defines its own copy of a helper hoisted into tests/lib/, proven on a planted suite, with the window helper's former names win, window and windows on its hoisted list ⟦criterion 2⟧
- [x] plain() (strip * and backticks, lowercase) is defined once in tests/lib/, taking the copy that also joins lines with tr '\n' ' ' as an argument; every suite and record-helpers.sh that defined plain() sources it, and the copies guard lists plain ⟦criterion 1⟧
- [x] The section-end read by next= (the first heading after a line, via head -1 < <(tail -n +… | grep -nE '^#')) is one helper in tests/lib/, used by skill-commit, skill-preflight-launchable and skill-test-command, and on the copies guard's list ⟦criterion 1⟧
- [x] section_end is on the copies guard's hoisted list, so a suite under tests/ or tests/unit/ that defines its own section_end is named <suite>:<line> ⟦added⟧ ⟦criterion 1⟧
- [x] frontmatter_name() is defined once in tests/lib/ and sourced by skill-candidates-identity, skill-fix-identity and skill-identity, and on the copies guard's list ⟦criterion 1⟧
- [x] first_record() and record_number() are defined once in tests/lib/ and used by skill-draft-pr, skill-refactor-pending and the inline reads in skill-criterion-finished, and both names are on the copies guard's list ⟦criterion 1⟧
- [x] fenced_lines() is defined once in tests/lib/ and sourced by skill-metrics and skill-leaf-launch, and on the copies guard's list ⟦criterion 1⟧
- [x] fenced_lines in tests/lib/ restricted to one heading prints only the fenced lines under that heading, pinned by a fast-tier case ⟦added⟧ ⟦criterion 1⟧
- [x] need_claude_md_records() is defined once in tests/lib/ and sourced by model-knobs-recorded and selection-order-recorded, and on the copies guard's list ⟦criterion 1⟧
- [x] probe_every_exemption_carries_a_reason() is defined once in tests/lib/ and sourced by no-sigpipe-pipelines, no-gh-json-argv and no-job-spec-kills, and on the copies guard's list ⟦criterion 1⟧ ⟂ refactor pending
- [ ] The guard suites' verdict() is defined once in tests/lib/ and sourced by count-line-guard, prompt-test-tiers, unit/missing-argument-exit, unit/emitted-text and unit/pending-mark-literal, and on the copies guard's list ⟦criterion 1⟧
- [ ] Copying lib/count-line-guard.sh into a planted tree is one helper in tests/lib/, used by count-line-guard, pytest-leg, prose-lag-green, unit-tier and watch in place of their own copy lines, and on the copies guard's list ⟦criterion 1⟧
- [ ] Every suite that switched to the shared helpers keeps its cases unmodified, and no suite gains a case that runs another suite ⟦diff-checked⟧ ⟦criterion 4⟧
- [ ] The copies guard was broken on purpose and seen red, then restored ⟦human-owed⟧ ⟦criterion 2⟧
- [ ] make test is green ⟦full-suite⟧ ⟦criterion 5⟧
