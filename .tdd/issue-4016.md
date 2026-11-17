# Plan for #4016 — PRD 024.7a: a heading unit is graded on its own section, and the whole-file unit signs only what no heading unit claims

- [x] signing a `file#heading` unit writes its GRADED unit field with each space as `%20` and each `%` as `%25` ⟦criterion 1⟧
- [x] every reader of GRADED decodes the unit field: a signed `file#heading` unit whose heading holds spaces owes nothing, and an orphan one is listed by its heading ⟦criterion 1⟧
- [x] a whole-file unit's GRADED line stays byte for byte and owes nothing when a `file#heading` unit is signed beside it ⟦criterion 1⟧
- [x] `graded-changed.sh <base-sha>` prints a `file#heading` unit when its section text differs between the base and HEAD ⟦criterion 7⟧
- [x] `requirements.list_path` of a `file#heading` unit whose heading holds a `/` is the list beside its file ⟦criterion 8⟧
- [x] `grade_prose.unit_text` of a `file#heading` unit is its own text: up to the next unfenced heading of any level ⟦criterion 2⟧
- [x] `grade-prose.sh` and `prose-owed.sh` exit 2 naming the unit and the match count when a listed heading unit's heading matches no unfenced heading, or more than one ⟦criterion 3⟧
- [x] a whole-file unit with a listed heading unit is split, and its view is the heading lines then the frontmatter and every unclaimed section's own text ⟦criterion 4⟧
- [x] a split whole-file unit signs its view; an edit inside a claimed section owes only that heading unit, and removing the last heading unit unsplits it ⟦criterion 5⟧ ⟦criterion 9⟧
- [ ] `grade-prose.sh` shows the grader a split whole-file unit's view, while `unit_text` still returns the whole file ⟦criterion 6⟧
- [ ] `graded-changed.sh` prints a split whole-file unit only when its view differs ⟦criterion 7⟧
- [ ] the tree audits that split GRADED lines decode the unit field ⟦criterion 1⟧
- [ ] `CLAUDE.md` *Graded prose* states heading units, own text, the split view and signature, and the unit field encoding (CM177–CM179), graded ⟦criterion 10⟧
- [ ] `skills/tdd/SCRIPTS.md` gains `grade-prose.sh` and `graded-changed.sh` entries and `prose-owed.sh`'s exit 2 (SC261–SC263), graded ⟦criterion 10⟧ ⟦criterion 11⟧
