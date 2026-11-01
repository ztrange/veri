# Plan for #2829 — install-links.sh reports each link it creates or repairs

- [ ] Running `install-links.sh` on a repo with none of the eight links prints exactly eight lines on stdout, one per skill name, and exits 0; a process case in skills/tdd/scripts/tests/py/test_install_links_process.py, driving the real script ⟦criterion 1⟧
- [ ] Running `install-links.sh` a second time on a repo already holding all eight links prints nothing on stdout; a process case in skills/tdd/scripts/tests/py/test_install_links_process.py, driving the real script ⟦criterion 2⟧
- [ ] After one veri link is left dangling and recreated by `install-links.sh`, stdout holds exactly one line, for that skill only; a process case in skills/tdd/scripts/tests/py/test_install_links_process.py, driving the real script ⟦criterion 2⟧
