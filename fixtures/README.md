# veri fixtures

Materials to demo the veri walking skeleton (`/solve-issue`) end-to-end on a seeded
single-criterion issue.

- [`demo-project/`](./demo-project) — a minimal, zero-dependency Python target. No
  implementation yet; one trivial passing test keeps the baseline green.
- [`seed-demo-issue.sh`](./seed-demo-issue.sh) — creates the single-criterion fixture
  issue (`slugify(text)`) on a GitHub repo.

## Running the demo

The conductor reads a GitHub issue, pushes a branch, and opens a draft PR, so the demo
runs against a real GitHub repo with push access. Use a throwaway repo:

1. **Stand up a target repo** from the demo project:
   ```sh
   cp -r fixtures/demo-project /tmp/veri-demo && cd /tmp/veri-demo
   git init && git add -A && git commit -m "chore: seed demo project"
   gh repo create veri-demo --private --source=. --push
   ```
   Copy the `solve-issue` skill into the target so it's invocable there:
   ```sh
   mkdir -p .claude/skills && cp -r <veri-repo>/.claude/skills/solve-issue .claude/skills/
   ```

2. **Seed the fixture issue** on that repo:
   ```sh
   <veri-repo>/fixtures/seed-demo-issue.sh   # prints the new issue URL/number
   ```

3. **Run the conductor** from a Claude Code session in `/tmp/veri-demo`:
   ```
   /solve-issue <n>
   ```

## What you should observe

- A `tdd/<n>-demo-add-a-slugify...` branch is created.
- The issue thread carries a start comment, then 🔴 Red, 🟢 Green, 🛠️ Refactor, and a
  final ✅ Done comment with the PR link.
- The full suite (`python3 -m unittest discover -q`) is green before the commits.
- A **draft** PR exists, linked with `Closes #<n>`, **not merged**.
