"""script-help.sh's lookup, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import pathlib
import sys

USAGE = "usage: script-help.sh <name>"


def main(argv):
    if argv:
        catalogue = pathlib.Path(__file__).resolve().parents[2] / "SCRIPTS.md"
        lines = catalogue.read_text().splitlines(keepends=True)
        prefix = f"- `$S/{argv[0]}"
        start = next((i for i, line in enumerate(lines) if line.startswith(prefix) and line[len(prefix):][:1] in (" ", "`")), None)
        if start is None:
            return 3
        end = next((i for i in range(start + 1, len(lines)) if lines[i][:1] != " "), len(lines))
        print("".join(lines[start:end]).rstrip("\n"))
        return 0
    print(USAGE, file=sys.stderr)
    return 2


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
