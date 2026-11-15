"""replaces-case-survivors.sh's check, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import sys

from replaces_case import is_replaces_case_step, parse, refusal

USAGE = "usage: replaces-case-survivors.sh <step text>"


def survivors(step):
    """Check the replaces-case `step`; answer `(code, stdout, stderr)` as text, printing nothing.

    `code` is 0 when every named case is gone (or the suite file is), 1 when some
    remain, 2 when the clause is refused, 3 when `step` names no replaced cases.
    `stdout` holds one "still present in <path>: <name>" line per survivor and
    `stderr` the refusal line, each newline-terminated; the other is "".
    The suite path is read relative to the working directory.
    """
    if not is_replaces_case_step(step):
        return 3, "", ""
    refused = refusal(step)
    if refused:
        return 2, "", refused + "\n"
    parsed = parse(step)
    if parsed is None:
        return 3, "", ""
    names, path = parsed
    try:
        with open(path, encoding="utf-8") as f:
            suite = "".join(
                line for line in f if not line.lstrip().startswith("#")
            )
    except FileNotFoundError:
        return 0, "", ""
    remaining = [n for n in names if f'"{n}"' in suite or f"'{n}'" in suite]
    lines = "".join(f"still present in {path}: {name}\n" for name in remaining)
    return (1 if remaining else 0), lines, ""


def main(argv):
    if len(argv) != 1:
        print(USAGE, file=sys.stderr)
        return 2
    code, out, err = survivors(argv[0])
    sys.stderr.write(err)
    sys.stdout.write(out)
    return code


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
