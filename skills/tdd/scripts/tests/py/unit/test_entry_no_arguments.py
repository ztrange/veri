"""Cases for veri/entry.py's no_arguments: a script that takes none refuses the first one it is handed."""
from veri import entry

USAGE = "usage: demo-script.sh"


def test_no_arguments_given_none_returns_none_and_writes_nothing(capfdbinary):
    answer = entry.no_arguments([], USAGE)

    assert (answer, capfdbinary.readouterr()) == (None, (b"", b""))


def test_no_arguments_given_one_names_it_then_the_usage_and_returns_2(capfdbinary):
    answer = entry.no_arguments(["--bogus"], USAGE)

    assert (answer, capfdbinary.readouterr().err) == (2, b"demo-script.sh: unexpected argument '--bogus'\nusage: demo-script.sh\n")


def test_no_arguments_given_several_names_only_the_first(capfdbinary):
    answer = entry.no_arguments(["one", "two"], USAGE)

    assert (answer, capfdbinary.readouterr().err) == (2, b"demo-script.sh: unexpected argument 'one'\nusage: demo-script.sh\n")
