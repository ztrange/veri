"""leaf-model.sh's resolution, run in-process."""
import os
import sys

USAGE = "usage: leaf-model.sh <leaf-name>"


def _write(stream, line):
    stream.flush()
    stream.buffer.write(os.fsencode(line + "\n"))
    stream.buffer.flush()


def main(argv):
    if not argv or not argv[0]:
        _write(sys.stderr, USAGE)
        return 2
    model = os.environ.get("VERI_MODEL", "")
    if model:
        _write(sys.stdout, model)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
