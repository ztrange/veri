"""Cases for veri/entry.py's `--help`: a module's USAGE, str or bytes, is printed from its `usage: ` on, and main is not called."""
from veri import entry


def run_help(capfdbinary, usage):
    """Run `--help` against a main whose module globals hold usage; return (code, argvs main saw, stdout, stderr)."""
    namespace = {"USAGE": usage, "calls": []}
    exec("def main(argv):\n    calls.append(argv)\n    return 0\n", namespace)
    code = entry.exit_code(namespace["main"], ["--help"])
    seen = capfdbinary.readouterr()
    return code, namespace["calls"], seen.out, seen.err


def test_help_prints_a_str_usage_from_its_usage_marker_and_never_calls_main(capfdbinary):
    assert run_help(capfdbinary, "demo.sh: usage: demo.sh <x>") == (0, [], b"usage: demo.sh <x>\n", b"")


def test_help_prints_a_bytes_usage_as_event_and_stop_requested_declare_it(capfdbinary):
    assert run_help(capfdbinary, b"usage: demo.sh [--clear]\n") == (0, [], b"usage: demo.sh [--clear]\n", b"")


def test_help_adds_no_second_newline_to_a_usage_that_already_ends_in_one_as_stop_run_declares_it(capfdbinary):
    assert run_help(capfdbinary, b"usage: demo.sh\n") == (0, [], b"usage: demo.sh\n", b"")
    assert run_help(capfdbinary, "usage: demo.sh\nsecond line\n") == (0, [], b"usage: demo.sh\nsecond line\n", b"")
