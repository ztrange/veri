### An argument after <kind> that is not --note-file <path> is a bad argument: comment.sh exits 2 with a usage line on stderr, posts nothing, and appends no comment event (the triangulating red already on disk serves it) ⟦added⟧ ⟦criterion 3⟧
- test-only | extract the repeated setup (stub gh_issue_comment, create .git/.tdd, write the ledger) of the three bad-argument cases in test_comment.py into a shared helper or fixture
### the `comment` event's url is the posted comment's .html_url with its trailing newline stripped; pinned by a case that goes red when the newline is kept, and by one that goes red when `-q .html_url` is dropped from github.py RestAdapter.issue_comment ⟦added⟧ ⟦criterion 1⟧
- test-only | extract the repeated `.git`/`.tdd`/ledger setup in test_comment.py into a fixture
