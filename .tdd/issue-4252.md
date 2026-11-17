# Plan for #4252 — PRD 026.9: an owner's answer to an issue-bound question is recorded on the issue before its question file goes

- [x] record-answer.sh <n> <file> posts `Question: …`, a blank line, `Owner's answer: …` on issue <n> and exits 0; issue-decisions reads it as `owner: Question: …` and park-decision prints it after the newest park ⟦criterion 1⟧
- [x] record-answer.sh posts nothing and exits 3 when a trusted comment already has that body ⟦criterion 2⟧
- [x] record-answer.sh exits 2, posting nothing, with one stderr line, on bad arguments, an unreadable file, a missing heading, an empty or over-2000 answer, or no answer from gh; a question over 2000 characters is cut with `…` ⟦criterion 3⟧
- [x] the posted body has local paths, host and account names redacted before github.py's token redaction ⟦criterion 4⟧
- [x] vdev SKILL.md *Answers* runs record-answer.sh before acting, acts only on exit 0 or 3, deletes the file only after ⟦criterion 5⟧
- [x] SCRIPTS.md lists record-answer.sh with body, bound, redaction, exits and caller ⟦criterion 6⟧
