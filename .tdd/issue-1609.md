# Plan for #1609 — refactor-overflow.sh files a duplicate 'Refactor owed by #n' on every resume

- [ ] When an open issue titled `Refactor owed by #<n>` already exists and some of the new candidates are not yet listed in it, refactor-overflow.sh files no new issue, appends those candidates to the existing issue as a comment, and prints that issue's URL; pinned by a case with gh faked (Red moves the expectations of existing cases whose fake gh must now also answer the open-issue lookup) ⟦criterion 1⟧
- [ ] When an open issue titled `Refactor owed by #<n>` already exists and already lists every new candidate, refactor-overflow.sh files no new issue, posts no comment, and prints that issue's URL; pinned by a case with gh faked ⟦criterion 1⟧
- [ ] When no open issue titled `Refactor owed by #<n>` exists, refactor-overflow.sh looks it up, finds none, and files one exactly as today, printing its URL; pinned by a case with gh faked ⟦criterion 1⟧
