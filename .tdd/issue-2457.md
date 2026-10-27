# Plan for #2457 — park-issue.sh accepts a PR URL from any repository and labels that number's PR in this one

- [ ] park-issue.sh given a PR URL whose owner or repo differs from the repository it runs in (its git origin) refuses with the usage line and exit 2, making no gh call of any kind; pinned by a process case running park-issue.sh against a gh stub that records every call, from a scratch git repo whose origin names another owner/repo ⟦criterion 1⟧
- [ ] park-issue.sh given a PR argument of 0 or with leading zeros (a bare 0 or 007, or a PR URL ending /pull/0 or /pull/007) refuses with the usage line and exit 2 before any gh call ⟦criterion 2⟧
- [ ] park-issue.sh given a PR URL naming the repository it runs in labels that PR number parked and records the URL on the comment's PR: line, and a bare PR number still labels that PR parked, exactly as before the fix ⟦criterion 3⟧
- [ ] The criterion-1 refusal case, run against park_issue.py with the owner/repo comparison loosened on purpose, goes red, and goes green again once restored ⟦human-owed⟧ ⟦criterion 4⟧
