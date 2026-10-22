"""The one __main__ entry point every ported module calls."""
import os
import sys

BROKEN_PIPE = 141


def _shim_name(main):
    module = os.path.splitext(os.path.basename(main.__code__.co_filename))[0]
    return module.replace("_", "-") + ".sh"


def refusal(main, exc):
    reason = " ".join(str(exc).split())
    return f"{_shim_name(main)}: {type(exc).__name__}: {reason}\n"


def write(stream, text):
    stream.flush()
    stream.buffer.write(os.fsencode(text + "\n"))
    stream.buffer.flush()


def silence_stdout():
    try:
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
    except (AttributeError, OSError, ValueError):
        pass


def exit_code(main, argv, on_broken_pipe=silence_stdout):
    try:
        code = main(argv)
        sys.stdout.flush()
    except BrokenPipeError:
        on_broken_pipe()
        return BROKEN_PIPE
    except Exception as exc:
        sys.stderr.write(refusal(main, exc))
        return 2
    return code


def run(main, argv):
    sys.exit(exit_code(main, argv))
