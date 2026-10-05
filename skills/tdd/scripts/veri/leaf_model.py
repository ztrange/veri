"""leaf-model.sh's resolution, run in-process."""
import os
import sys

from leaf_role import leaf_role

USAGE = "usage: leaf-model.sh <leaf-name>"
WHITESPACE = " \t\n\v\f\r"


def _write(stream, line, end="\n"):
    stream.flush()
    stream.buffer.write(os.fsencode(line + end))
    stream.buffer.flush()


def _echo(value):
    if len(value) > 1 and value[0] == "-" and all(c in "neE" for c in value[1:]):
        _write(sys.stdout, "", "" if "n" in value else "\n")
    else:
        _write(sys.stdout, value)


def main(argv):
    if not argv or not argv[0]:
        _write(sys.stderr, USAGE)
        return 2
    role = leaf_role(argv[0])
    if role is None:
        return 2
    actor = role["VERI_ACTOR"]
    model = os.environ.get("VERI_MODEL_" + actor.upper()) or os.environ.get("VERI_MODEL", "")
    if any(c in WHITESPACE for c in model):
        _write(sys.stderr, f"leaf-model: model '{model}' contains whitespace (a model id or alias is one word)")
        return 2
    if model:
        _echo(model)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
