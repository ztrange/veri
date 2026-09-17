# Plan for #244 — solvable-issues.sh reads only gh's default 30 issues and PRs

- [x] solvable-issues.sh asks gh for every open issue, not gh's default page of 30: an opted-in, unblocked issue older than the newest 30 is printed
- [x] An issue blocked by an open issue that is older than the newest 30 is not printed
- [x] solvable-issues.sh asks gh for every open pull request, not gh's default page of 30: an open PR past the first 30 saying Closes #<n> still claims its issue ⟂ refactor pending
