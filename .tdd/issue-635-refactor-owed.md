### under `make test`, a suite under tests/unit/ that calls real git, python3, gh or curl fails, and the output names the command it called ⟦criterion 1⟧
- the "no line of 'make …' names git" check (`grep -qw git < <(grep -v '^== ' <<< "$out")`) appears in both case 5 and the new case and could become one helper, but the two messages differ and the saving is small
