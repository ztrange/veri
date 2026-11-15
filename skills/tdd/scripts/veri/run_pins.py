"""A run's per-issue pin files: the settings the launcher records under `.tdd/` and later readers honour.

One owner per file: the function that writes a pin sits beside the one that reads it, and the
path comes from run_dir. File names and bytes are what runs pinned on an older skill snapshot
already read, so they never change. (The hard-timeout pin is owned by leaf_timeout.)

    issue-<n>-skip-verify       the VERI_SKIP_VERIFY list the run was launched with
    issue-<n>-conductor-model   the model the conductor was launched on
"""
import contextlib
import os

import run_dir


def _read(issue, suffix, roots):
    for root in roots:
        path = run_dir.issue_file(root, issue, suffix)
        if os.path.exists(path):
            with contextlib.suppress(OSError):
                with open(path) as recorded:
                    return recorded.read().strip()
            return None
    return None


def write_skip_verify(root, issue, listed):
    """Record the skipped verifier phases: `<listed>\\n`, or an empty file when none are listed."""
    with open(run_dir.issue_file(root, issue, "-skip-verify"), "w") as skip:
        skip.write(listed + "\n" if listed else "")


def skip_verify(issue, *roots):
    """The stripped phase list in the pin of the first of `roots` (a directory holding a `.tdd/`) that
    has one, `""` for an empty pin, None when none does or the file is unreadable."""
    return _read(issue, "-skip-verify", roots)


def write_conductor_model(root, issue, model):
    """Record the conductor's model: `<model>\\n`."""
    with open(run_dir.issue_file(root, issue, "-conductor-model"), "w") as record:
        record.write(model + "\n")


def conductor_model(issue, *roots):
    """The stripped model in the pin of the first of `roots` that has one, None when none does."""
    return _read(issue, "-conductor-model", roots)
