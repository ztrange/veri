# Plan for #879 — Readying a PR right after the rebase force-push runs CI on the pre-rebase sha, and wait-ci times out on the head

- [x] gh_pr_ready <n> <head-sha> marks PR <n> ready only once GitHub's pulls/<n> reports <head-sha> as the PR's head: while it reports another sha it reads pulls/<n> again after VERI_POLL seconds and does not mark the PR ready meanwhile
- [ ] gh_pr_ready <n> <head-sha> returns 2 without marking PR <n> ready when pulls/<n> still reports another sha after its bounded number of reads, with a stderr line naming both the expected and the reported sha
- [ ] gh_pr_ready <n> called with no head-sha marks PR <n> ready at once, reading no pulls/<n>, exactly as before
- [ ] SKILL.md's Draft PR step readies the PR with gh_pr_ready <pr-number> "$(git rev-parse HEAD)", so the ready_for_review CI run starts on the head just pushed rather than the pre-rebase sha
