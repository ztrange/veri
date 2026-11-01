# Plan for #2830 — install-links.sh handles a repo with no .git/info directory

- [ ] In a repo whose git directory has no `info/` directory (made by `git init --template=`), `install-links.sh <repo>` exits 0, `.git/info/exclude` lists all eight `/.claude/skills/<name>` entries, and the eight links exist (a medium `process` case with real git, in test_install_links_process.py) ⟦criterion 1⟧
