# Plan for #1745 — refactor-overflow.sh names a failed comments read, and matches candidates in CRLF bodies

- [x] When reading the existing `Refactor owed by #<n>` issue's comments fails — the fake gh answers the comments read with exit 1 and `{"message":"Not Found"}` on stdout — `refactor-overflow.sh` posts no comment, files no issue, and exits 2 with exactly one stderr line naming the comments read (pytest case, fake gh at the process boundary) ⟦criterion 1⟧
- [x] A candidate already listed as `- <candidate>` in the existing issue's body or in one of its comments whose text uses `\r\n` line endings counts as already listed, so `refactor-overflow.sh` posts no comment for it (pytest case for a CRLF body and for a CRLF comment) ⟦criterion 2⟧
