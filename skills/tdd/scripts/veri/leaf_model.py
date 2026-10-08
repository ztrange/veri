"""leaf-model.sh's resolution, run in-process."""
import os
import sys

from leaf_role import _write, leaf_role

USAGE = "usage: leaf-model.sh <leaf-name>"
WHITESPACE = " \t\n\v\f\r"


def _echo(value):
    if len(value) > 1 and value[0] == "-" and all(c in "neE" for c in value[1:]):
        if "n" not in value:
            _write(sys.stdout, "")
    else:
        _write(sys.stdout, value)


def resolve(name):
    role = leaf_role(name)
    if role is None:
        return None
    actor = role["VERI_ACTOR"]
    model = os.environ.get("VERI_MODEL_" + actor.upper()) or os.environ.get("VERI_MODEL", "")
    if any(c in WHITESPACE for c in model):
        _write(sys.stderr, f"leaf-model: model '{model}' contains whitespace (a model id or alias is one word)")
        return None
    return model


def main(argv):
    if not argv or not argv[0]:
        _write(sys.stderr, USAGE)
        return 2
    model = resolve(argv[0])
    if model is None:
        return 2
    if model:
        _echo(model)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
