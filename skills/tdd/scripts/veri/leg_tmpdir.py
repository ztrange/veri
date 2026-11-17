"""The TMPDIR the pytest leg pins before it starts (#2354), read by run-conductor's free-space check too (#2430)."""

# A local run's scratch matches CI's rather than the Mac's /var/folders/...; the leg (tests/leg/pytest_leg.py) and
# run_conductor.py both read this constant, so a run never imports the leg to learn it (PRD 025.16).
PINNED_TMPDIR = "/tmp"
