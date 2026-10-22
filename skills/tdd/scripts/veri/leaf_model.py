"""leaf-model.sh's resolution, run in-process."""
import sys

import tunables
from entry import write
from leaf_role import is_revise, leaf_role

USAGE = "usage: leaf-model.sh <leaf-name>"
WHITESPACE = " \t\n\v\f\r"


def _is_echo_option(value):
    return len(value) > 1 and value[0] == "-" and all(c in "neE" for c in value[1:])


def _echo(value):
    if _is_echo_option(value):
        if "n" not in value:
            write(sys.stdout, "")
    else:
        write(sys.stdout, value)


def _env(key):
    value = tunables.read(key, "")
    return "" if not value.strip(WHITESPACE) else value


def resolve(name):
    role = leaf_role(name)
    if role is None:
        return None
    actor = role["VERI_ACTOR"]
    revise = is_revise(name)
    model = ((_env("VERI_MODEL_REVISE") if revise else "")
             or _env("VERI_MODEL_" + actor.upper()) or _env("VERI_MODEL"))
    if not model:
        model = "opus" if revise else "sonnet"
    if any(c in WHITESPACE for c in model):
        write(sys.stderr, f"leaf-model: model '{model}' contains whitespace (a model id or alias is one word)")
        return None
    return model


def leaf_model(name):
    """The model a leaf runs with, as `$(leaf-model.sh <name>)` reads it: its shipped default when no variable is set, empty when refused."""
    model = resolve(name)
    if model is None or _is_echo_option(model):
        return ""
    return model


def main(argv):
    if not argv or not argv[0]:
        write(sys.stderr, USAGE)
        return 2
    model = resolve(argv[0])
    if model is None:
        return 2
    _echo(model)
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
