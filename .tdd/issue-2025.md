# Plan for #2025 — prose-owed.sh is blind to a graded unit outside skills/ (operator/PRINCIPLES.md)

- [x] prose-owed.sh reports a graded unit outside skills/ — operator/PRINCIPLES.md listed in operator/REQUIREMENTS.md and signed in operator/GRADED — as owed (exit 1, the unit printed) after its prose changes by one byte, exactly as it reports a unit under skills/; a small in-process case on a tmp_path repo ⟦criterion 1⟧
- [x] prose-owed.sh's orphan sweep reports a unit recorded in a GRADED file outside skills/ (operator/GRADED) that no REQUIREMENTS.md lists as an orphan, the same way it reports one in skills/*/GRADED; a small in-process case on a tmp_path repo ⟦criterion 2⟧
