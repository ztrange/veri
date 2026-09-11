# Plan for #69 — Walkthrough: open with an intro that sells veri

- [x] the build computes the number of issues solved by running veri on itself from git (count of `plan: scope #<n>` commits reachable from HEAD) and degrades to no number when the tree has no git or no matching history, so a tree without that history still builds with the "built with itself" sentence present and the figure absent
- [ ] docs/walkthrough.html opens with a new pitch section placed before the element with id="what" whose prose covers strict TDD instead of vibe coding, built with itself, blind verification, and observability, each claim carrying an in-page link to the section that substantiates it
- [ ] the rail navigation lists the new pitch section as a top-level entry alongside the existing sections
