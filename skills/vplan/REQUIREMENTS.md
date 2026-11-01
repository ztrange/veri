## skills/vplan/SKILL.md

| ID | Requirement | Why |
|---|---|---|
| VPL1 | Invoked as `/vplan <idea>`, or `/vplan`; the idea may instead be an existing issue to redefine. | Same short alias form as `/vcoord`. |
| VPL2 | Near its top, the skill says it obeys `operator/PRINCIPLES.md` and reads it first. | Without it no principle reaches the skill. |
| VPL3 | It names no project fact: where PRDs live and which labels apply are read from the target repo's CLAUDE.md, and where that is silent, a spec goes to `specs/prd-<nnn>.md` (P12). | Skills serve foreign repos. |
| VPL4 | Before its first question to the human, it gathers the facts: what exists that the idea touches, a measurement of whatever the idea claims to improve, the next free PRD number, and the open PRDs it overlaps. | A measurement decided the order of PRD 014, and PRD 013's number was nearly reused. |
| VPL5 | It asks through the installed `grilling` skill. When that is not installed, it says so and asks in numbered rounds of every question now answerable, each with a recommendation, worded so that yes accepts it. | One source for the method where present, and a veri install without it still works. |
| VPL6 | A fact is never asked of the human, and no spec is written until no decision is open or the human has said to stop asking. | Facts are the skill's job and decisions the human's. |
| VPL7 | A decision the plan does not need yet is recorded as open, with a recommendation and the sub-PRD that needs it. | Later decisions should not hold up the first delivery. |
| VPL8 | A plan is split into sub-PRDs numbered `<nnn>.<k>`. Each states what the human gets when it lands and what it depends on, and each is worth having if the next never ships. A plan that fits one sub-PRD stays one, and one that fits one issue may be that issue. | The operator wants frequent delivery, not a wait for the full PRD. |
| VPL9 | Only the next sub-PRDs carry requirement rows, in the `ID`, `Requirement`, `Why` format, each one claim that can be marked true or false; the rest are outlines. | Later rows are better written from what earlier sub-PRDs taught. |
| VPL10 | Every measured figure in a plan names its commit and its conditions, and a speed or cost goal is stated as a target in prose, with the criteria being behaviours that force it. | The repo's rule is that wall-clock is never a criterion. |
| VPL11 | Redefining an existing issue keeps its old text in a comment on that issue, and the plan says what happened to each of its decisions: carried, overturned with the reason, or open. | Edit history is a poor home for decisions a spec cites by number. |
| VPL12 | A plan is finished when a fresh session could file from it: the issue points at a spec on the default branch, or holds the rows itself. A spec still on an unmerged PR is reported as unfinished, and the PR merges only when the human says so. | PRD 014's issue first pointed at a file only on an unmerged branch. |
| VPL13 | A PRD issue that is not itself the work carries no opt-in label. | An epic was once taken as an ordinary issue. |
| VPL14 | It files only the children the human names, each through `/vfile`, and titles them `PRD <nnn>.<k>: …`. It never starts a run. | The operator chose to file only 014.1. Starting runs belongs to `/vdev` and `/vcoord`. |
| VPL15 | Every subagent brief it writes asks for a return of at most 10 lines (P6), and says that all writes stay in the project repo and that a fix belonging elsewhere is reported, not made (P11, in its words). | Earlier skills' prose omitted both. |
| VPL16 | A sub-PRD holds at most one capability the human can use. | The README promises sub-PRDs sized for a single `/tdd` run, and clarion2's 001.1 held five deliveries. One sub-PRD meant one wait for five results. Row count did not predict how much a run took, so the cap is capabilities. |
| VPL17 | A sub-PRD holding more than one capability is split, or states in the sub-PRD why it cannot be. | A limit with no consequence changes nothing, and a real exception should be visible to whoever files it. |
| VPL18 | An outline sub-PRD expected to hold more than one capability is split while it is still an outline. | A split after filing comes after the wait it was meant to avoid, and `/tdd` notices only when a run parks on budget. |
| VPL19 | Within one capability, a sub-PRD takes the smallest piece worth having if the next never ships, even when more sub-PRDs cost more in total. | The capability cap bounds what a sub-PRD holds, not how big it gets, and the operator ranks small slices over saving money (P16). |
