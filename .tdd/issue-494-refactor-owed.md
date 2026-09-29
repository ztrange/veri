### comment-class.sh classes a `#` line inside a heredoc written to a `.md` file as class 3 ⟦added⟧ ⟦criterion 1⟧
- the new cases 24 and 25 in `unit/comment-class.test.sh` repeat the same setup (two fixtures written with `printf`, `classify`, two `want_line` checks). A helper or loop would remove that, but every other case in the file is written out the same way, so I left them.
