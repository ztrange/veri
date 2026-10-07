"""skill-drift.sh's block, run in-process."""
import os
import re
import subprocess
import sys

SUFFIX = re.compile(r"\(#(\d+)\)\s*$")


def git(clone, *args):
    return subprocess.run(["git", "-C", clone, *args], capture_output=True, text=True).stdout


def main(argv):
    commit = os.environ["VERI_SKILL_COMMIT"]
    clone = os.environ["VERI_SKILL_CLONE"]
    ref = os.environ["VERI_SKILL_REF"]
    log = git(clone, "log", "--format=%s", "%s..%s" % (commit, ref),
              "--", "skills/tdd", ":(exclude)skills/tdd/scripts/tests")
    groups = {}
    for subject in log.splitlines():
        number = SUFFIX.search(subject).group(1)
        groups.setdefault(number, []).append(subject)
    short = git(clone, "rev-parse", "--short", commit).strip()
    lines = ["#### Skill drift since the pinned commit",
             "Pinned skill commit: %s." % short,
             "Conductor-path changes on %s since then:%s" % (ref, "" if groups else " none.")]
    if groups:
        lines += ["- #%s — %s (%d commits)" % (n, s[0], len(s)) for n, s in groups.items()]
        lines.append("Resume with VERI_NEW_SKILL=1 to run on these.")
    sys.stdout.write("\n".join(lines) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
