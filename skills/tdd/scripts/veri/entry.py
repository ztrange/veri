"""The one __main__ entry point every ported module calls, and the exit contract's shared edges.

Interface (stderr/stdout bytes and return values):

run(main, argv)          exits the process with exit_code(main, argv); returns nothing.
exit_code(main, argv, on_broken_pipe=silence_stdout)
                         calls main(argv) and returns its code; `--help` alone prints the module's USAGE
                         to stdout and returns 0; a BrokenPipeError calls on_broken_pipe and returns 141;
                         any other Exception writes refusal(main, exc) to stderr and returns 2.
refuse(*lines, usage=None, prefix="")
                         writes each non-None str/bytes line to stderr as prefix + line + newline, then
                         usage (a newline added only if it lacks one); returns 2.
to_contract(code)        returns code when it is 0, 1, 2 or 3, else 2 (signals, values above 3, None).
write(stream, text, *, before=True, after=True, end="\n")
                         writes str or bytes text plus end to stream.buffer as raw bytes, flushing the
                         stream before and its buffer after; returns nothing.
refusal(main, exc)       returns the one-line stderr text for an escaped exception:
                         "<shim>.sh: <Type>: <reason> (at <file>:<line>)\n".
silence_stdout()         points fd 1 at /dev/null so a broken pipe cannot raise again; returns nothing.
"""
import os
import sys
import traceback

BROKEN_PIPE = 141


def _shim_name(main):
    module = os.path.splitext(os.path.basename(main.__code__.co_filename))[0]
    return module.replace("_", "-") + ".sh"


def refusal(main, exc):
    reason = " ".join(str(exc).split())
    frame = traceback.extract_tb(exc.__traceback__)[-1]
    where = f" (at {os.path.basename(frame.filename)}:{frame.lineno}"
    if isinstance(exc, PermissionError):
        where += f": {frame.line}"
    where += ")"
    return f"{_shim_name(main)}: {type(exc).__name__}: {reason}{where}\n"


def write(stream, text, *, before=True, after=True, end="\n"):
    if before:
        stream.flush()
    data = text if isinstance(text, bytes) else os.fsencode(text)
    stream.buffer.write(data + os.fsencode(end))
    if after:
        stream.buffer.flush()


def refuse(*lines, usage=None, prefix=""):
    """Write each line (str or bytes, None skipped) behind prefix, then usage, to stderr; return 2."""
    lead = os.fsencode(prefix)
    for line in lines:
        if line is not None:
            data = line if isinstance(line, bytes) else os.fsencode(line)
            write(sys.stderr, lead + data)
    if usage is not None:
        data = usage if isinstance(usage, bytes) else os.fsencode(usage)
        write(sys.stderr, data, end="" if data.endswith(b"\n") else "\n")
    return 2


def to_contract(code):
    """Return code when it is one of the four contract codes, else 2."""
    return code if code in (0, 1, 2, 3) else 2


def silence_stdout():
    try:
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
    except (AttributeError, OSError, ValueError):
        pass


def _usage(main):
    usage = main.__globals__["USAGE"]
    return usage[usage.index("usage: "):]


def exit_code(main, argv, on_broken_pipe=silence_stdout):
    try:
        if argv == ["--help"] and "USAGE" in main.__globals__:
            write(sys.stdout, _usage(main))
            return 0
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
