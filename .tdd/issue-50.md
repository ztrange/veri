# Plan for #50 — Per-hunk version tags in script listings: which lines changed, and why

- [x] A script whose only history is its original feat: addition (one tag) renders with no class="l hunk" anywhere in its listing
- [ ] A script with one line last changed by a later feat:/fix: commit (a later tag) renders that line as span class="l hunk" data-tag="vX.Y" title="...", title equal to the commit subject stripped of prefix and any (#N), every other line stays plain span class="l"
- [ ] Two non-adjacent single-line changes from two different feat:/fix: commits at two different tags render as two separate hunk-tagged lines, each with its own distinct data-tag/title
- [ ] A line whose last-touching commit is a non-behaviour commit landed after the feat: commit that introduced it is NOT tagged
- [ ] In a tree with no .git (sandbox()), the build still succeeds and the page contains no class="l hunk" at all
