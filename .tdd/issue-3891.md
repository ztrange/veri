# Plan for #3891 — stale-rows.sh signs GRADED with the signature of the text it graded, not of the working tree

- [x] in a tree holding grade_prose.py, a passing grade made through a non-default reader writes the signature of the text that reader returned, under the tree's formula ⟦criterion 1⟧
- [x] a passing grade through the default reader, in a tree whose grade_prose.py signature takes no text, still writes that tree's signature
- [x] a tree whose grade_prose.py cannot sign a given text (too old to take the text as an argument) exits 2 and writes no signature ⟦criterion 2⟧
