# Plan for #501 — a skill that turns architecture-analysis candidates into veri-shaped issues

- [x] A new veri skill ships as its own directory under skills/ whose SKILL.md frontmatter name matches the directory, and it says it shapes and files candidates without surveying, ranking or judging them
- [x] Given architecture-analysis candidates taken from the conversation, the skill files one GitHub issue per module (not one per smell), each with acceptance criteria phrased as structural predicates carrying a runnable check where one exists ⟦criterion 1⟧
- [x] Given the path to the analysis's HTML report instead of conversation candidates, the skill reads the candidates from that file and files the same issues it would have filed from the conversation ⟦criterion 2⟧
- [x] Every issue the skill files ends its body with a final `Test command:` line and lists under `## Blocked by` only real blockers ⟦criterion 3⟧
- [x] A candidate with no checkable predicate is not filed, and the skill says which candidate was skipped and why ⟦criterion 4⟧
- [x] Re-running the skill over candidates it already filed files no duplicate issue for them ⟦criterion 5⟧
- [ ] The lookup for an already-filed issue finds its marker however many issues the repository holds, so a repository with more than 1,000 issues still files no duplicate ⟦added⟧ ⟦criterion 5⟧
