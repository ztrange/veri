### a GRADES block that leaves out one requirement ID makes grade-prose exit 2 with no verdict, its stderr naming the missing ID as missing, and no grading event appended ⟦criterion 2⟧
- test-only | extract the repeated fixture setup (grader.conf, REQUIREMENTS.md with A1–A3, grade-prose.log, subprocess.run stub, monkeypatching) from the three #2208 tests in test_grade_prose.py into one helper
