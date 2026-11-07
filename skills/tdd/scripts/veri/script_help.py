"""script-help.sh's lookup, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import pathlib
import sys

USAGE = "usage: script-help.sh <name>"


def entry_for(name):
    catalogue = pathlib.Path(__file__).resolve().parents[2] / "SCRIPTS.md"
    lines = catalogue.read_text().splitlines(keepends=True)
    prefix = f"- `$S/{name}"
    start = next((i for i, line in enumerate(lines) if line.startswith(prefix) and line[len(prefix):][:1] in (" ", "`")), None)
    if start is None:
        return None
    end = next((i for i in range(start + 1, len(lines)) if lines[i][:1] != " "), len(lines))
    return "".join(lines[start:end]).rstrip("\n")


def main(argv):
    if not argv:
        print(USAGE, file=sys.stderr)
        return 2
    entry_text = entry_for(argv[0])
    if entry_text is None:
        return 3
    print(entry_text)
    return 0



if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
