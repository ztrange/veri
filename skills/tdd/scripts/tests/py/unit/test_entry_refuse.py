"""Cases for veri/entry.py's refuse and to_contract: the exit contract's shared edges."""
import pytest
from veri import entry


def stderr_of(capfdbinary, *args, **kwargs):
    code = entry.refuse(*args, **kwargs)
    return code, capfdbinary.readouterr().err


def test_refuse_a_bare_message_writes_it_and_a_newline_to_stderr_and_returns_2_as_add_ledger_step_uses_it(
        capfdbinary):
    code, err = stderr_of(capfdbinary, "add-ledger-step.sh: no such ledger")

    assert (code, err) == (2, b"add-ledger-step.sh: no such ledger\n")


def test_refuse_with_usage_writes_the_message_then_usage_with_a_newline_added_as_leaf_timeout_does(capfdbinary):
    from veri import leaf_timeout

    usage = leaf_timeout.USAGE
    code, err = stderr_of(capfdbinary, "leaf-timeout: bad", usage=usage)

    assert not usage.endswith("\n")
    assert (code, err) == (2, b"leaf-timeout: bad\n" + usage.encode() + b"\n")


def test_refuse_usage_already_ending_in_a_newline_gets_no_second_one_as_workqueue_does(capfdbinary):
    from veri import workqueue

    code, err = stderr_of(capfdbinary, "workqueue.sh: no worker", usage=workqueue.USAGE)

    assert workqueue.USAGE.endswith("\n")
    assert (code, err) == (2, b"workqueue.sh: no worker\n" + workqueue.USAGE.encode())


def test_refuse_usage_alone_is_written_with_no_message_line(capfdbinary):
    code, err = stderr_of(capfdbinary, usage="usage: x")

    assert (code, err) == (2, b"usage: x\n")


def test_refuse_prefix_leads_every_line_but_not_usage_as_issue_worktree_prefixes_its_message(capfdbinary):
    code, err = stderr_of(capfdbinary, "first", "second", prefix="issue-worktree: ")
    assert (code, err) == (2, b"issue-worktree: first\nissue-worktree: second\n")

    code, err = stderr_of(capfdbinary, "first", prefix="p: ", usage="usage: u")
    assert (code, err) == (2, b"p: first\nusage: u\n")


def test_refuse_bytes_line_is_written_verbatim_after_a_str_prefix_as_refactor_triage_does(capfdbinary):
    text = b"candidate line has no class: \xff\xfe odd"
    code, err = stderr_of(capfdbinary, text, prefix="refactor-triage: ")

    assert (code, err) == (2, b"refactor-triage: " + text + b"\n")


def test_refuse_skips_none_lines_and_writes_nothing_when_given_only_none(capfdbinary):
    assert stderr_of(capfdbinary, None, "kept", None) == (2, b"kept\n")
    assert stderr_of(capfdbinary, None) == (2, b"")
    assert stderr_of(capfdbinary) == (2, b"")


def test_refuse_writes_str_lines_with_surrogate_escapes_back_to_their_original_bytes(capfdbinary):
    code, err = stderr_of(capfdbinary, "name \udcff")

    assert (code, err) == (2, b"name \xff\n")


@pytest.mark.parametrize("code, mapped", [(0, 0), (1, 1), (2, 2), (3, 3), (4, 2), (-15, 2), (130, 2), (None, 2)])
def test_to_contract_keeps_the_four_codes_and_maps_everything_else_to_2(code, mapped):
    assert entry.to_contract(code) == mapped
