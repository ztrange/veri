# Plan for #2208 — grade-prose throws away a complete verdict whose GRADES rows are out of file order

- [ ] grade-prose reads a GRADES block naming every requirement ID exactly once but with two rows swapped out of file order, all PASS, as a PASS verdict: exit 0, a grading event with verdict=PASS, the unit's signature recorded in GRADED, as the same rows in file order would give ⟦criterion 1⟧
- [ ] grade-prose reads a GRADES block naming every requirement ID exactly once with a FAIL row swapped out of file order as a REJECT verdict: exit 1, the FAIL row printed and a grading event with verdict=REJECT naming it, as the same rows in file order would give ⟦criterion 1⟧
- [ ] a GRADES block that leaves out one requirement ID makes grade-prose exit 2 with no verdict, its stderr naming the missing ID as missing, and no grading event appended ⟦criterion 2⟧
- [ ] a GRADES block that names one requirement ID twice makes grade-prose exit 2 with no verdict, its stderr naming the repeated ID as repeated, and no grading event appended ⟦criterion 2⟧
- [ ] a GRADES block that names an ID the unit's requirements list does not hold makes grade-prose exit 2 with no verdict, its stderr naming the unknown ID as unknown, and no grading event appended ⟦criterion 2⟧
