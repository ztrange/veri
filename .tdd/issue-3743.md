# Plan for #3743 — vbail resumes a first-bail run without a free slot, so a slot dispatch already refilled puts the lane over N

- [x] `skills/vbail/SKILL.md`'s *A first real bail: resume once* makes the first-bail resume take a slot like any launch: it runs only when the live conductors, counted fresh at that moment with `kill -0`, number fewer than N (an unexpired timed N included, as read from the dev role state); otherwise the resume is held and the next freed slot goes to it ahead of the solvable queue — graded against requirement B14 ⟦skill-edit⟧ ⟦criterion 1⟧
