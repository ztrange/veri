"""skill-drift.sh's block, run in-process."""
import os
import re
import subprocess
import sys

SUFFIX = re.compile(r"\(#(\d+)\)\s*$")


def run(clone, *args):
    return subprocess.run(["git", "-C", clone, *args], capture_output=True, text=True)


def git(clone, *args):
    return run(clone, *args).stdout


def resolves(clone, rev):
    return bool(git(clone, "rev-parse", "--verify", "--quiet", rev + "^{commit}").strip())


def unavailable(reason):
    sys.stdout.write("Skill drift: unavailable — %s\n" % reason)
    return 0


def main(argv):
    commit = os.environ.get("VERI_SKILL_COMMIT", "")
    if os.environ.get("VERI_SKILL_UNPINNED") == "1" or not commit:
        return unavailable("run was not pinned to a skill commit")
    clone = os.environ.get("VERI_SKILL_CLONE", "")
    if not clone or git(clone, "rev-parse", "--is-inside-work-tree").strip() != "true":
        return unavailable("skill clone not known")
    if not resolves(clone, commit):
        return unavailable("pinned commit %s is not in %s" % (commit, clone))
    ref = os.environ.get("VERI_SKILL_REF", "")
    if not ref:
        return unavailable("skill ref not known")
    fetched = run(clone, "fetch", "-q", "origin").returncode == 0
    if not resolves(clone, ref):
        return unavailable("%s does not resolve in %s" % (ref, clone))
    log = git(clone, "log", "--format=%h %s", "%s..%s" % (commit, ref),
              "--", ":(top)skills/tdd", ":(top,exclude)skills/tdd/scripts/tests")
    groups = {}
    for line in log.splitlines():
        sha, subject = line.split(" ", 1)
        match = SUFFIX.search(subject)
        key = match.group(1) if match else sha
        suffixed, newest, count = groups.get(key, (bool(match), subject, 0))
        groups[key] = (suffixed, newest, count + 1)
    short = git(clone, "rev-parse", "--short", commit).strip()
    lines = ["#### Skill drift since the pinned commit",
             "Pinned skill commit: %s." % short,
             "Conductor-path changes on %s since then:%s" % (ref, "" if groups else " none.")]
    if groups:
        for key, (suffixed, newest, count) in groups.items():
            lines.append("- #%s — %s (%d commits)" % (key, newest, count) if suffixed else "- %s %s" % (key, newest))
        lines.append("Resume with VERI_NEW_SKILL=1 to run on these.")
    if not fetched:
        lines.append("origin could not be fetched — list is as of the last fetch of %s" % ref)
    sys.stdout.write("\n".join(lines) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
