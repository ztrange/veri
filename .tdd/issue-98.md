# Plan for #98 — Raise the VERI_HEARTBEAT default to 180s — 45s kills leaves that are thinking, not hung

- [x] a check fails when the heartbeat default encoded in supervise.sh and the prose stating it disagree
- [x] supervise.sh applies a 180-second heartbeat default when VERI_HEARTBEAT is unset, and an explicit value still overrides it
