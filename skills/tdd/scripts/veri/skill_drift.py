"""skill-drift.sh's block, run in-process."""
import os
import re
import subprocess
import sys

SUFFIX = re.compile(r"\(#(\d+)\)\s*$")


def git(clone, *args):
    return subprocess.run(["git", "-C", clone, *args], capture_output=True, text=True).stdout


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
    ref = os.environ["VERI_SKILL_REF"]
    if not resolves(clone, ref):
        return unavailable("%s does not resolve in %s" % (ref, clone))
    log = git(clone, "log", "--format=%h %s", "%s..%s" % (commit, ref),
              "--", "skills/tdd", ":(exclude)skills/tdd/scripts/tests")
    groups = {}
    for line in log.splitlines():
        sha, subject = line.split(" ", 1)
        match = SUFFIX.search(subject)
        groups.setdefault(match.group(1) if match else sha, []).append((match, subject))
    short = git(clone, "rev-parse", "--short", commit).strip()
    lines = ["#### Skill drift since the pinned commit",
             "Pinned skill commit: %s." % short,
             "Conductor-path changes on %s since then:%s" % (ref, "" if groups else " none.")]
    if groups:
        lines += ["- #%s — %s (%d commits)" % (k, s[0][1], len(s)) if s[0][0] else "- %s %s" % (k, s[0][1])
                  for k, s in groups.items()]
        lines.append("Resume with VERI_NEW_SKILL=1 to run on these.")
    sys.stdout.write("\n".join(lines) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
