"""build-adjudicate-prompt.sh's prompt builder, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import sys

USAGE = "usage: build-adjudicate-prompt.sh <n> <cause> <exit-code> <stderr-file> <command…>"


def main(argv):
    if not argv:
        print(USAGE, file=sys.stderr)
        return 2
    n, cause, exit_code, stderr_file, *command = argv
    with open(f".tdd/issue-{n}.md") as f:
        steps = [line.rstrip("\n") for line in f if line.startswith(("- [ ]", "- [x]"))]
    step = next((s for s in steps if s.startswith("- [ ]")), steps[-1])
    with open(stderr_file) as f:
        stderr = f.read()
    print(
        f"Cause: {cause}\nCommand: {' '.join(command)}\nExit code: {exit_code}\n"
        f"Stderr:\n{stderr}\nStep: {step}\n\n"
        "End with one final line: ADJUDICATION: retry|bail|route <token> — <reason>"
    )
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
