"""refresh-spec.sh's re-capture, built in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import sys

try:
    from capture_spec import capture, part
    from github import NoAnswer
except ImportError:
    from .capture_spec import capture, part
    from .github import NoAnswer


def boxes(spec):
    return sum(1 for line in part(spec, "Acceptance criteria").split("\n") if line.startswith("- ["))


def main(argv):
    if len(argv) != 2:
        print("usage: refresh-spec.sh <n> <spec-file>", file=sys.stderr)
        return 2
    try:
        live = capture(argv[0])
    except NoAnswer:
        return 2
    with open(argv[1]) as f:
        old = f.read()
    if old == live:
        return 3
    if boxes(old) != boxes(live):
        print("refresh-spec: acceptance criteria checkboxes differ: file %d, live %d"
              % (boxes(old), boxes(live)), file=sys.stderr)
        return 1
    with open(argv[1], "w") as f:
        f.write(live)
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
