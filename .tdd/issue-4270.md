# Plan for #4270 — Progress notes, verifier reasons, needs-user bails, park and preflight-refused comments can publish local paths, account or host name

- [x] every `comment.sh` verb (progress notes, verifier reasons, stopped, step-done) posts its body through one choke point, `github.published`, so a note naming `/Users/someone/x.py` and `/tmp/y` reaches the posted body with neither ⟦criterion 1⟧
- [x] the `needs-user` bail posts the conductor's last paragraph through the choke point, with neither `/Users/someone/x.py` nor `/tmp/y` in the posted body ⟦criterion 1⟧
- [x] the parked comment posts its cause, unblock and question through the choke point, with neither `/Users/someone/x.py` nor `/tmp/y` in the posted body ⟦criterion 1⟧
- [x] a parked comment whose question is dense with local paths is cut on its redacted text, so the posted body stays within COMMENT_LIMIT − MARGIN characters and BYTE_LIMIT − MARGIN bytes ⟦added⟧ ⟦criterion 1⟧
- [x] the preflight-refused comment posts its detail through the choke point, with neither `/Users/someone/x.py` nor `/tmp/y` in the posted body ⟦criterion 1⟧
- [ ] the local-path pattern stops at a path boundary: `/tmpfile` and `/homepage` come through unchanged and `path=/tmp/x,` keeps its comma, while URLs, repo-relative paths and `.tdd/…` come through unchanged ⟦criterion 2⟧
- [ ] a unit audit fails when a module under `veri/` posts an issue or PR comment whose body does not pass through the choke point ⟦criterion 3⟧
