"""A run's per-issue pin files: the settings the launcher records under `.tdd/` and later readers honour.

One owner per file: the function that writes a pin sits beside the one that reads it, and the
path comes from run_dir. File names and bytes are what runs pinned on an older skill snapshot
already read, so they never change. (The hard-timeout pin is owned by leaf_timeout.)

    issue-<n>-skip-verify         the VERI_SKIP_VERIFY list the run was launched with
    issue-<n>-conductor-model     the model the conductor was launched on
    issue-<n>-launch-env          the VERI_* environment a restarted conductor is relaunched with
    issue-<n>-baseline-full-tier  the VERI_BASELINE_FULL_TIER mode the run was launched with
    issue-<n>-snapshot-digest     the digest of the skill snapshot the launch extracted (pinned_scripts.snapshot_digest)
    issue-<n>-branch-base         the run's branch base sha, in the main working tree, written by preflight at the cut

A new pin's suffix is a constant below and joins IGNORED, which derives the `.tdd/.gitignore` seed.
"""
import contextlib
import os

import run_dir

SKIP_VERIFY = "-skip-verify"
CONDUCTOR_MODEL = "-conductor-model"
LAUNCH_ENV = "-launch-env"
BASELINE_FULL_TIER = "-baseline-full-tier"
SKILL_COMMIT = "-skill-commit"  # written by run_conductor, read by pinned_scripts
SNAPSHOT_DIGEST = "-snapshot-digest"
BRANCH_BASE = "-branch-base"

# Seed order is part of the bytes older runs were seeded with.
IGNORED = (SKILL_COMMIT, SKIP_VERIFY, BASELINE_FULL_TIER, CONDUCTOR_MODEL, LAUNCH_ENV, SNAPSHOT_DIGEST, BRANCH_BASE)


def gitignore_seed():
    """The text a run's `.tdd/.gitignore` is seeded with: itself, every pin in IGNORED, the conductor logs, wt/."""
    return "".join(f"{line}\n" for line in
                   [".gitignore", *(f"issue-*{suffix}" for suffix in IGNORED), "conductor-*.log", "wt/"])


def _read(issue, suffix, roots, *, tolerant):
    for root in roots:
        path = run_dir.issue_file(root, issue, suffix)
        if os.path.exists(path):
            with contextlib.suppress(OSError) if tolerant else contextlib.nullcontext():
                with open(path) as recorded:
                    return recorded.read().strip()
            return None
    return None


def write_skip_verify(root, issue, listed):
    """Record the skipped verifier phases: `<listed>\\n`, or an empty file when none are listed."""
    with open(run_dir.issue_file(root, issue, SKIP_VERIFY), "w") as skip:
        skip.write(listed + "\n" if listed else "")


def skip_verify(issue, *roots, unreadable_raises=False):
    """The stripped phase list in the pin of the first of `roots` (a directory holding a `.tdd/`) that
    has one, `""` for an empty pin, None when none does. A pin that exists but cannot be read answers
    None, or raises its OSError when `unreadable_raises`."""
    return _read(issue, SKIP_VERIFY, roots, tolerant=not unreadable_raises)


def write_conductor_model(root, issue, model):
    """Record the conductor's model: `<model>\\n`."""
    with open(run_dir.issue_file(root, issue, CONDUCTOR_MODEL), "w") as record:
        record.write(model + "\n")


def conductor_model(issue, *roots):
    """The stripped model in the pin of the first of `roots` that has one, None when none does."""
    return _read(issue, CONDUCTOR_MODEL, roots, tolerant=True)


def write_launch_env(root, issue, environment):
    """Record the launch environment: one `NAME=value` line per `VERI_*` name of `environment`
    except VERI_NEW_SKILL (a relaunch must not re-pin the skill), sorted by name."""
    with open(run_dir.issue_file(root, issue, LAUNCH_ENV), "w") as record:
        record.write("".join("%s=%s\n" % kv for kv in sorted(environment.items())
                             if kv[0].startswith("VERI_") and kv[0] != "VERI_NEW_SKILL"))


def launch_env(issue, root):
    """The recorded `{name: value}` of the run under `root`, None when it recorded none; lines without
    an `=` are skipped. OSError other than a missing file propagates."""
    try:
        with open(run_dir.issue_file(root, issue, LAUNCH_ENV)) as record:
            lines = list(record)
    except FileNotFoundError:
        return None
    pairs = (line.rstrip("\n").partition("=") for line in lines)
    return {key: value for key, sep, value in pairs if sep}


def write_baseline_full_tier(root, issue, mode):
    """Record the baseline full-tier mode: `<mode>\\n`."""
    with open(run_dir.issue_file(root, issue, BASELINE_FULL_TIER), "w") as pin:
        pin.write(mode + "\n")


def baseline_full_tier(issue, root):
    """The stripped mode the run pinned under `root`, None when it pinned none. OSError propagates."""
    return _read(issue, BASELINE_FULL_TIER, (root,), tolerant=False)


def write_snapshot_digest(root, issue, digest):
    """Record the digest of the launch's skill snapshot, as given."""
    with open(run_dir.issue_file(root, issue, SNAPSHOT_DIGEST), "w") as record:
        record.write(digest)


def snapshot_digest(issue, root):
    """The digest the run recorded under `root`, as written; None when it recorded none. OSError propagates."""
    try:
        with open(run_dir.issue_file(root, issue, SNAPSHOT_DIGEST)) as record:
            return record.read()
    except FileNotFoundError:
        return None


def write_branch_base(root, issue, sha):
    """Record the run's branch base: `<sha>\\n`, the `.tdd/` made when `root` has none."""
    path = run_dir.issue_file(root, issue, BRANCH_BASE)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as record:
        record.write(sha + "\n")


def branch_base(issue, root):
    """The stripped sha the run recorded under `root`. OSError propagates, FileNotFoundError when it recorded none."""
    with open(run_dir.issue_file(root, issue, BRANCH_BASE)) as record:
        return record.read().strip()
