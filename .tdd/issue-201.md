# Plan for #201 — A cost report read from the session transcripts

- [x] session-cost.sh totals a day's cost from a transcript, split into cache-read, cache-write and output, with CLAUDE.md's counts moved
- [x] Every project directory whose slug is prefixed by the repo root's slug is summed, not only the exact slug
- [x] Records sharing a requestId are counted once
- [x] 1h and 5m cache writes are priced apart, and a record carrying only cache_creation_input_tokens falls back to the 5m rate
- [x] --since excludes a record outside the window and includes one inside it
- [ ] An sdk-cli session and an interactive session are attributed to their own rows, by entrypoint
- [ ] Per-session rows carry the preamble, the final context and the total context read, and a session dominated by an un-cleared ramp is named as such in words
- [ ] An unknown model's tokens are reported with no cost and named in a footer
- [ ] --json emits the same totals as the text report
