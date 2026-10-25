# Plan for #2343 — park-issue.sh exits 2, naming the write, when a gh write it makes fails

- [x] Given a `<pr>` argument, park-issue.sh also labels that PR `parked` (its PR write), and when gh fails only that PR write it exits 2 and names the PR write on stderr, the issue label and comment writes having succeeded ⟦criterion 1⟧
- [x] When the repository already has the `parked` label, so gh answers the label-creation call with HTTP 422 (already exists), park-issue.sh still labels the issue, posts the comment and exits 0: an existing label is not a failed write ⟦criterion 1⟧
- [x] When gh fails to create a `parked` label the repository lacks, park-issue.sh exits 2 and names the issue label write on stderr, instead of ignoring the failed creation ⟦criterion 1⟧
