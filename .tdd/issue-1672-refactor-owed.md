### unlabel-issue.sh whose label-removal request gets no answer from gh (a failure that is not a 404) exits 2 with stderr naming the unanswered request ⟦criterion 1⟧
- `unlabel_issue.py` builds its `unlabel-issue.sh: …` error prefix in three separate messages. This is a small repeat, and extracting it would add an abstraction no test requires.
