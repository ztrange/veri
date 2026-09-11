# Plan for #91 — Partition the /solve-issues pool: read the opt-in label from VERI_LABEL so two loops on one repo do not take the same issues

- [x] with VERI_LABEL unset, solvable-issues.sh still selects on the ready-for-agent label exactly as today
- [x] with VERI_LABEL set to another label name, an issue carrying only ready-for-agent is not listed and one carrying that label is
- [x] an issue carrying both labels is listed under either VERI_LABEL value
- [x] VERI_LABEL set to the empty string is refused with exit 2 and a diagnostic on stderr, never treated as any label
- [x] skills/solve-issues/SKILL.md, README.md and CONTEXT.md name VERI_LABEL and the one-label-per-loop partitioning use
- [x] the /solve-issues nothing-to-do message names the label it drained rather than saying ready-for-agent unconditionally
- [x] the committed walkthrough is rebuilt for the edited script so make docs-check passes
