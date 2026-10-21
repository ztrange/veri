# Plan for #1887 — grade-prose.sh's grader leaf has no leaf role: leaf-role refuses 'grade-prose' on every grading

- [x] `leaf-role.sh grade-prose` prints the role line `VERI_ACTOR=grader VERI_PHASE=prose VERI_ATTEMPT=1` and exits 0, nothing on stderr, a grader role distinct from developer and verifier (small in-process case; the unknown-leading-word diagnostic text stays exactly as it is) ⟦criterion 1⟧
- [x] `harvest-usage.sh` recognises the grader leaf's name `grade-prose`: the usage event it appends for that leaf carries actor `grader` and phase `prose`, and it prints nothing about leaf roles on stderr (small in-process case; the unknown-leading-word diagnostic text stays exactly as it is) ⟦criterion 1⟧
- [x] A graded run of `grade-prose.sh` with a stub claude, launched through `supervise.sh`, exits 0 and prints nothing about leaf roles (no `leaf-role:` line) on stderr (process case) ⟦criterion 1⟧
- [ ] A leaf name with an unknown leading word still exits 2 with the existing diagnostic, pinned by the existing cases staying green ⟦full-suite⟧ ⟦criterion 2⟧
