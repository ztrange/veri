"""In-process cases for veri/tick_ledger.py, the module tick-ledger.sh is a shim over."""
import errno
import importlib
import io
import os
import resource
import sys

import pytest

USAGE = b"usage: tick-ledger.sh [--refactor-pending | --phase <phase> | --phase-owed <phase> | --unpinnable <reason-file> | --already-holds <reason-file>] [--case <id>] <ledger-file> <matcher> (--unpinnable and --already-holds drop every mutation record whose named test is absent from the tree)\n"


@pytest.fixture
def tick_ledger():
    return importlib.import_module("veri.tick_ledger")


def test_main_refuses_a_missing_or_empty_ledger_file_with_the_usage_line_and_exits_3_leaving_an_unmatched_ledger_untouched(
        tmp_path, capsysbinary, tick_ledger):
    ledger = tmp_path / "ledger.md"
    ledger.write_bytes(b"- [ ] alpha\n")
    results = {}
    for argv in ([], [""], ["--refactor-pending"], ["--refactor-pending", ""], [str(ledger), "zeta"]):
        code = tick_ledger.main(argv)
        results[tuple(argv)] = (code, *capsysbinary.readouterr())

    assert results == {
        (): (2, b"", USAGE),
        ("",): (2, b"", USAGE),
        ("--refactor-pending",): (2, b"", USAGE),
        ("--refactor-pending", ""): (2, b"", USAGE),
        (str(ledger), "zeta"): (3, b"", b""),
    }
    assert ledger.read_bytes() == b"- [ ] alpha\n"


def test_main_ticks_the_matching_step_in_place_marking_it_refactor_pending_only_with_the_flag(
        tmp_path, capsysbinary, tick_ledger):
    seed = (b"# Plan for #42\n\n- [ ] add lowercasing\n- [ ] collapse to single hyphen\n"
            b"- [ ] strip edge hyphens\n")
    results = {}
    for flag in (["--refactor-pending"], []):
        ledger = tmp_path / f"ledger{len(flag)}.md"
        ledger.write_bytes(seed)
        code = tick_ledger.main([*flag, str(ledger), "collapse to single hyphen"])
        out, _ = capsysbinary.readouterr()
        results[tuple(flag)] = (code, out, ledger.read_bytes())

    assert results == {
        ("--refactor-pending",): (0, b"", "# Plan for #42\n\n- [ ] add lowercasing\n"
                                  "- [x] collapse to single hyphen ⟂ refactor pending\n"
                                  "- [ ] strip edge hyphens\n".encode()),
        (): (0, b"", b"# Plan for #42\n\n- [ ] add lowercasing\n- [x] collapse to single hyphen\n"
                     b"- [ ] strip edge hyphens\n"),
    }


def test_main_returns_0_for_a_tick_3_for_an_unmatched_matcher_and_2_for_no_argument_every_exit_inside_0_to_3(
        tmp_path, capsysbinary, tick_ledger):
    ledger = tmp_path / "ledger.md"
    ledger.write_bytes(b"- [ ] alpha\n- [ ] beta\n")
    codes = [tick_ledger.main(argv) for argv in ([str(ledger), "alpha"], [str(ledger), "zeta"], [])]
    capsysbinary.readouterr()

    assert codes == [0, 3, 2]
    assert all(0 <= code <= 3 for code in codes)


def test_main_rewrites_the_ledger_as_printf_over_a_command_substitution_collapsing_trailing_newlines_adding_a_final_one_and_dropping_nul(
        tmp_path, capsysbinary, tick_ledger):
    results = {}
    for seed in (b"- [ ] a\n\n\n", b"- [ ] a", b"- [ ] a\0z"):
        ledger = tmp_path / f"ledger{len(results)}.md"
        ledger.write_bytes(seed)
        code = tick_ledger.main([str(ledger), "a"])
        capsysbinary.readouterr()
        results[seed] = (code, ledger.read_bytes())

    assert results == {
        b"- [ ] a\n\n\n": (0, b"- [x] a\n"),
        b"- [ ] a": (0, b"- [x] a\n"),
        b"- [ ] a\0z": (0, b"- [x] az\n"),
    }


def test_main_ticks_the_first_open_step_for_an_omitted_or_empty_matcher_ignores_arguments_after_the_second_and_reads_the_flag_only_first(
        tmp_path, capsysbinary, tick_ledger):
    results = {}
    for argv in ([], [""], ["b", "--refactor-pending"], ["--refactor-pending"]):
        ledger = tmp_path / f"ledger{len(results)}.md"
        ledger.write_bytes(b"- [ ] a\n- [ ] b\n")
        code = tick_ledger.main([str(ledger), *argv])
        results[tuple(argv)] = (code, *capsysbinary.readouterr(), ledger.read_bytes())

    assert results == {
        (): (0, b"", b"", b"- [x] a\n- [ ] b\n"),
        ("",): (0, b"", b"", b"- [x] a\n- [ ] b\n"),
        ("b", "--refactor-pending"): (0, b"", b"", b"- [ ] a\n- [x] b\n"),
        ("--refactor-pending",): (3, b"", b"", b"- [ ] a\n- [ ] b\n"),
    }


def test_main_leaves_an_empty_ledger_unwritten_with_exit_3_marks_a_crlf_step_after_its_cr_and_skips_a_lower_and_upper_x_step(
        tmp_path, capsysbinary, tick_ledger):
    results = {}
    for flag, seed, matcher in (
            ([], b"", "a"),
            (["--refactor-pending"], b"- [ ] a\r\n", "a"),
            ([], b"- [x] a\n- [X] a\n- [ ] a\n", "a")):
        ledger = tmp_path / f"ledger{len(results)}.md"
        ledger.write_bytes(seed)
        os.utime(ledger, ns=(0, 0))
        code = tick_ledger.main([*flag, str(ledger), matcher])
        results[seed] = (code, *capsysbinary.readouterr(), ledger.read_bytes(), ledger.stat().st_mtime_ns == 0)

    assert results == {
        b"": (3, b"", b"", b"", True),
        b"- [ ] a\r\n": (0, b"", b"", "- [x] a\r ⟂ refactor pending\n".encode(), False),
        b"- [x] a\n- [X] a\n- [ ] a\n": (0, b"", b"", b"- [x] a\n- [X] a\n- [x] a\n", False),
    }


def test_main_returns_2_on_a_missing_ledger_with_one_stderr_line_naming_it(
        tmp_path, capsysbinary, tick_ledger):
    code = tick_ledger.main([str(tmp_path / "missing.md"), "a"])
    out, err = capsysbinary.readouterr()
    assert (code, out) == (2, b"")
    assert err.decode() == f"tick-ledger.sh: {tmp_path / 'missing.md'}: No such file or directory\n"


def test_main_returns_2_on_a_directory_as_the_ledger_with_one_stderr_line_naming_it(
        tmp_path, capsysbinary, tick_ledger):
    code = tick_ledger.main([str(tmp_path), "a"])
    out, err = capsysbinary.readouterr()
    assert (code, out) == (2, b"")
    assert err.decode() == f"tick-ledger.sh: {tmp_path}: Is a directory\n"


def test_main_ticks_a_criterion_notation_step_by_a_matcher_carrying_its_criterion_marker_and_marks_it_refactor_pending(
        tmp_path, capsysbinary, tick_ledger):
    ledger = tmp_path / "ledger.md"
    ledger.write_bytes("- [x] add lowercasing ⟦criterion 1⟧\n- [ ] collapse to single hyphen ⟦criterion 1⟧\n"
                       "- [ ] strip edge hyphens\n".encode())
    code = tick_ledger.main(["--refactor-pending", str(ledger), "collapse to single hyphen ⟦criterion 1⟧"])
    out, _ = capsysbinary.readouterr()

    assert (code, out, ledger.read_bytes().decode().split("\n")[1]) == (
        0, b"", "- [x] collapse to single hyphen ⟦criterion 1⟧ ⟂ refactor pending")


def test_main_leaves_the_ledger_byte_identical_and_returns_2_when_writing_the_ticked_ledger_fails_817(
        tmp_path, capsysbinary, tick_ledger):
    seed = "".join(f"- [ ] step {n} of a ledger long enough to outgrow the file size limit\n" for n in range(8)).encode()
    ledger = tmp_path / "ledger.md"
    ledger.write_bytes(seed)
    soft, hard = resource.getrlimit(resource.RLIMIT_FSIZE)
    resource.setrlimit(resource.RLIMIT_FSIZE, (64, hard))
    try:
        code = tick_ledger.main([str(ledger), "step 3"])
    except OSError as error:
        code = type(error).__name__
    finally:
        resource.setrlimit(resource.RLIMIT_FSIZE, (soft, hard))
    capsysbinary.readouterr()

    assert (code, ledger.read_bytes()) == (2, seed)


def test_main_keeps_the_ledger_file_permissions_when_it_ticks_a_step_817(tmp_path, capsysbinary, tick_ledger):
    ledger = tmp_path / "ledger.md"
    ledger.write_bytes(b"- [ ] alpha\n")
    ledger.chmod(0o640)

    code = tick_ledger.main([str(ledger), "alpha"])
    capsysbinary.readouterr()

    assert (code, oct(ledger.stat().st_mode & 0o777)) == (0, oct(0o640))


def test_main_leaves_no_file_but_the_ledger_beside_it_when_writing_the_ticked_ledger_fails_817(
        tmp_path, capsysbinary, tick_ledger):
    seed = "".join(f"- [ ] step {n} of a ledger long enough to outgrow the file size limit\n" for n in range(8)).encode()
    ledger = tmp_path / "ledger.md"
    ledger.write_bytes(seed)
    soft, hard = resource.getrlimit(resource.RLIMIT_FSIZE)
    resource.setrlimit(resource.RLIMIT_FSIZE, (64, hard))
    try:
        code = tick_ledger.main([str(ledger), "step 3"])
    except OSError as error:
        code = type(error).__name__
    finally:
        resource.setrlimit(resource.RLIMIT_FSIZE, (soft, hard))
    capsysbinary.readouterr()

    assert (code, sorted(path.name for path in tmp_path.iterdir())) == (2, ["ledger.md"])


def test_main_leaves_the_ledger_byte_identical_and_returns_2_when_the_temporary_file_beside_it_cannot_be_created_817(
        tmp_path, capsysbinary, tick_ledger, monkeypatch):
    seed = b"- [ ] alpha\n- [ ] beta\n"
    ledger = tmp_path / "ledger.md"
    ledger.write_bytes(seed)
    real_open = os.open

    def refusing_open(path, *args, **kwargs):
        if os.path.dirname(os.path.abspath(path)) == str(tmp_path) and os.path.abspath(path) != str(ledger):
            raise OSError(errno.ENOSPC, os.strerror(errno.ENOSPC), path)
        return real_open(path, *args, **kwargs)

    monkeypatch.setattr(os, "open", refusing_open)
    try:
        code = tick_ledger.main([str(ledger), "beta"])
    except OSError as error:
        code = type(error).__name__
    monkeypatch.undo()
    capsysbinary.readouterr()

    assert (code, ledger.read_bytes()) == (2, seed)


def test_main_returns_2_without_raising_leaving_the_ledger_byte_identical_and_nothing_beside_it_when_putting_the_ticked_ledger_in_place_and_removing_its_temporary_file_both_fail_1110(
        tmp_path, monkeypatch, capsysbinary, tick_ledger):
    seed = b"- [ ] alpha\n- [ ] beta\n"
    ledger = tmp_path / "ledger.md"
    ledger.write_bytes(seed)
    real_replace = os.replace
    real_unlink = os.unlink

    def refusing_replace(src, dst, *args, **kwargs):
        if os.path.abspath(dst) == str(ledger):
            raise OSError(errno.EIO, os.strerror(errno.EIO), dst)
        return real_replace(src, dst, *args, **kwargs)

    def failing_unlink(path, *args, **kwargs):
        real_unlink(path, *args, **kwargs)
        if os.path.dirname(os.path.abspath(path)) == str(tmp_path):
            raise OSError(errno.EIO, os.strerror(errno.EIO), path)

    monkeypatch.setattr(os, "replace", refusing_replace)
    monkeypatch.setattr(os, "unlink", failing_unlink)
    try:
        code = tick_ledger.main([str(ledger), "beta"])
    except OSError as error:
        code = type(error).__name__
    monkeypatch.undo()
    err = capsysbinary.readouterr().err

    assert (code, b"Traceback" in err, ledger.read_bytes(), sorted(p.name for p in tmp_path.iterdir())) == (
        2, False, seed, ["ledger.md"])


def test_main_ticks_the_target_of_a_symlinked_ledger_leaving_the_link_a_link_and_nothing_beside_either_1110(
        tmp_path, capsysbinary, tick_ledger):
    (tmp_path / "real").mkdir()
    (tmp_path / "link").mkdir()
    target = tmp_path / "real" / "ledger.md"
    target.write_bytes(b"- [ ] alpha\n- [ ] beta\n")
    link = tmp_path / "link" / "ledger.md"
    link.symlink_to(target)

    code = tick_ledger.main([str(link), "beta"])
    capsysbinary.readouterr()

    assert (code, link.is_symlink(), target.read_bytes(),
            sorted(p.name for p in target.parent.iterdir()), sorted(p.name for p in link.parent.iterdir())) == (
        0, True, b"- [ ] alpha\n- [x] beta\n", ["ledger.md"], ["ledger.md"])


def test_main_returns_2_without_raising_on_a_dangling_symlinked_ledger_leaving_the_link_a_link_and_nothing_beside_it_1110(
        tmp_path, capsysbinary, tick_ledger):
    link = tmp_path / "ledger.md"
    link.symlink_to(tmp_path / "gone" / "ledger.md")

    try:
        code = tick_ledger.main([str(link), "beta"])
    except OSError as error:
        code = type(error).__name__
    err = capsysbinary.readouterr().err

    assert (code, b"Traceback" in err, link.is_symlink(), sorted(p.name for p in tmp_path.iterdir())) == (
        2, False, True, ["ledger.md"])


def test_main_returns_2_without_raising_leaving_the_ledger_byte_identical_and_names_the_leftover_temporary_file_in_one_stderr_line_when_putting_it_in_place_fails_and_removing_it_raises_without_deleting_it_1125(
        tmp_path, monkeypatch, capsysbinary, tick_ledger):
    seed = b"- [ ] alpha\n- [ ] beta\n"
    ledger = tmp_path / "ledger.md"
    ledger.write_bytes(seed)
    real_replace = os.replace

    def refusing_replace(src, dst, *args, **kwargs):
        if os.path.abspath(dst) == str(ledger):
            raise OSError(errno.EIO, os.strerror(errno.EIO), dst)
        return real_replace(src, dst, *args, **kwargs)

    def refusing_unlink(path, *args, **kwargs):
        raise OSError(errno.EIO, os.strerror(errno.EIO), path)

    monkeypatch.setattr(os, "replace", refusing_replace)
    monkeypatch.setattr(os, "unlink", refusing_unlink)
    try:
        code = tick_ledger.main([str(ledger), "beta"])
    except OSError as error:
        code = type(error).__name__
    monkeypatch.undo()
    err = capsysbinary.readouterr().err
    beside = [p for p in tmp_path.iterdir() if p.name != "ledger.md"]

    assert (code, b"Traceback" in err, ledger.read_bytes(), len(beside)) == (2, False, seed, 1)
    lines = err.decode().splitlines()
    assert (len(lines), all(line.startswith("tick-ledger.sh: ") and str(beside[0]) in line
                            for line in lines)) == (1, True)


def test_main_with_phase_expand_marks_expand_done_on_the_phased_step_in_place_leaving_it_unchecked_and_every_other_line_unchanged(
        tmp_path, capsysbinary, tick_ledger):
    phased = "- [ ] rename the slug helper ⟦phases: expand, migrate, contract-a, contract-b⟧ ⟦criterion 1⟧"
    seed = ("# Plan for #42\n\n- [ ] add lowercasing\n" + phased + "\n- [ ] strip edge hyphens\n").encode()
    ledger = tmp_path / "ledger.md"
    ledger.write_bytes(seed)

    code = tick_ledger.main(["--phase", "expand", str(ledger), "rename the slug helper"])
    out, _ = capsysbinary.readouterr()

    assert (code, out, ledger.read_bytes()) == (
        0, b"", ("# Plan for #42\n\n- [ ] add lowercasing\n" + phased + " ⟂ expand done\n"
                 "- [ ] strip edge hyphens\n").encode())


def test_main_with_phase_marking_every_listed_phase_in_order_finishes_the_step_for_ledger_steps_next_unchecked_and_next_phase(
        tmp_path, monkeypatch, capsysbinary, tick_ledger):
    ledger_steps = importlib.import_module("veri.ledger_steps")
    next_unchecked = importlib.import_module("veri.next_unchecked")
    phases = ("expand", "migrate", "contract-a", "contract-b")
    ledger = tmp_path / "ledger.md"
    ledger.write_bytes((
        "# Plan for #42\n\n- [x] add lowercasing\n"
        "- [ ] rename the slug helper ⟦phases: expand, migrate, contract-a, contract-b⟧ ⟦criterion 1⟧\n"
        "- [ ] strip edge hyphens\n"
        "- [ ] split the slug module ⟦phases: expand, migrate⟧ ⟦criterion 2⟧\n").encode())

    codes = tuple(tick_ledger.main(["--phase", phase, str(ledger), "rename the slug helper"]) for phase in phases)
    capsysbinary.readouterr()
    answers = {}
    for name, module, argv in (("ledger-steps", ledger_steps, []), ("next-unchecked", next_unchecked, []),
                               ("next-phase", ledger_steps, ["next-phase"])):
        monkeypatch.setattr(sys, "stdin", io.TextIOWrapper(io.BytesIO(ledger.read_bytes())))
        code = module.main(argv)
        answers[name] = (code, capsysbinary.readouterr()[0])
    states = [line.split(b"\t")[1] for line in answers["ledger-steps"][1].splitlines()]

    assert (codes, answers["ledger-steps"][0], states, answers["next-unchecked"], answers["next-phase"]) == (
        (0, 0, 0, 0), 0, [b"done", b"done", b"open", b"open"],
        (0, b"strip edge hyphens\n"), (0, b"expand\n"))


def test_main_with_phase_naming_a_phase_the_step_does_not_list_exits_2_leaving_the_ledger_byte_identical(
        tmp_path, capsysbinary, tick_ledger):
    seed = ("# Plan for #42\n\n- [ ] add lowercasing\n"
            "- [ ] split the slug module ⟦phases: expand, migrate⟧ ⟦criterion 2⟧\n"
            "- [ ] strip edge hyphens\n").encode()
    ledger = tmp_path / "ledger.md"
    ledger.write_bytes(seed)

    code = tick_ledger.main(["--phase", "contract-a", str(ledger), "split the slug module"])
    capsysbinary.readouterr()

    assert (code, ledger.read_bytes()) == (2, seed)


def test_main_with_phase_naming_a_listed_phase_before_an_earlier_unmarked_one_exits_2_leaving_the_ledger_byte_identical(
        tmp_path, capsysbinary, tick_ledger):
    seed = ("# Plan for #42\n\n- [ ] add lowercasing\n"
            "- [ ] split the slug module ⟦phases: expand, migrate⟧ ⟦criterion 2⟧\n"
            "- [ ] strip edge hyphens\n").encode()
    ledger = tmp_path / "ledger.md"
    ledger.write_bytes(seed)

    code = tick_ledger.main(["--phase", "migrate", str(ledger), "split the slug module"])
    capsysbinary.readouterr()

    assert (code, ledger.read_bytes()) == (2, seed)


def test_main_without_phase_refuses_a_phased_step_with_exit_2_naming_phase_leaving_the_ledger_byte_identical_while_a_plain_step_still_ticks_1385(
        tmp_path, capsysbinary, tick_ledger):
    seed = ("# Plan for #42\n\n"
            "- [ ] split the slug module ⟦phases: expand, migrate⟧ ⟦criterion 2⟧\n"
            "- [ ] strip edge hyphens\n").encode()
    ledger = tmp_path / "ledger.md"
    ledger.write_bytes(seed)

    phased_code = tick_ledger.main([str(ledger), "split the slug module"])
    _, phased_err = capsysbinary.readouterr()
    phased_ledger = ledger.read_bytes()
    plain_code = tick_ledger.main([str(ledger), "strip edge hyphens"])

    assert (phased_code, phased_err.count(b"\n"), b"--phase" in phased_err, phased_ledger) == (2, 1, True, seed)
    assert (plain_code, *capsysbinary.readouterr(), ledger.read_bytes()) == (
        0, b"", b"", seed.replace(b"- [ ] strip", b"- [x] strip"))


def test_main_refuses_phase_with_refactor_pending_in_either_order_with_exit_2_naming_both_flags_leaving_the_ledger_byte_identical_1385(
        tmp_path, capsysbinary, tick_ledger):
    seed = ("# Plan for #42\n\n"
            "- [ ] split the slug module ⟦phases: expand, migrate⟧ ⟦criterion 2⟧\n"
            "- [ ] strip edge hyphens\n").encode()
    ledger = tmp_path / "ledger.md"
    results = {}
    for flags in (["--refactor-pending", "--phase", "expand"], ["--phase", "expand", "--refactor-pending"]):
        ledger.write_bytes(seed)
        code = tick_ledger.main([*flags, str(ledger), "split the slug module"])
        out, err = capsysbinary.readouterr()
        results[tuple(flags)] = (code, out, err.count(b"\n"), b"--phase" in err, b"--refactor-pending" in err,
                                 ledger.read_bytes())

    assert results == {
        ("--refactor-pending", "--phase", "expand"): (2, b"", 1, True, True, seed),
        ("--phase", "expand", "--refactor-pending"): (2, b"", 1, True, True, seed),
    }


def test_main_prints_a_usage_line_naming_phase_on_a_bad_argument_1385(capsysbinary, tick_ledger):
    code = tick_ledger.main([])
    out, err = capsysbinary.readouterr()

    assert (code, out, err.count(b"\n"), err.startswith(b"usage: tick-ledger.sh "), b"--phase <phase>" in err) == (
        2, b"", 1, True, True)


def test_main_with_phase_owed_marks_the_next_unmarked_phase_owed_leaving_the_step_unchecked_and_refuses_an_unlisted_or_later_phase_with_exit_2_leaving_the_ledger_byte_identical_1410(
        tmp_path, capsysbinary, tick_ledger):
    phased = ("- [ ] rename the slug helper ⟦phases: expand, migrate, contract-a, contract-b⟧ ⟦criterion 1⟧"
              " ⟂ expand done ⟂ migrate done")
    seed = ("# Plan for #42\n\n- [x] add lowercasing\n" + phased + "\n- [ ] strip edge hyphens\n\n"
            "## Owed steps\n\n- rename the slug helper: contract-a\n").encode()
    ledger = tmp_path / "ledger.md"
    results = {}
    for phase in ("contract-c", "contract-b", "contract-a"):
        ledger.write_bytes(seed)
        code = tick_ledger.main(["--phase-owed", phase, str(ledger), "rename the slug helper"])
        out, _ = capsysbinary.readouterr()
        results[phase] = (code, out, ledger.read_bytes())

    assert results == {
        "contract-c": (2, b"", seed),
        "contract-b": (2, b"", seed),
        "contract-a": (0, b"", seed.replace(phased.encode(), (phased + " ⟂ contract-a owed").encode())),
    }


def test_main_prints_a_usage_line_naming_phase_owed_beside_phase_on_a_bad_argument_1410(capsysbinary, tick_ledger):
    code = tick_ledger.main([])
    out, err = capsysbinary.readouterr()

    assert (code, out, err.count(b"\n"), b"--phase <phase>" in err, b"--phase-owed <phase>" in err) == (
        2, b"", 1, True, True)


def test_main_after_phase_owed_keeps_the_contract_owed_refusing_to_mark_it_done_or_tick_the_step_with_exit_2_and_leaves_its_owed_bullet_unchanged_1410(
        tmp_path, capsysbinary, tick_ledger):
    phased = ("- [ ] rename the slug helper ⟦phases: expand, migrate, contract-a⟧ ⟦criterion 1⟧"
              " ⟂ expand done ⟂ migrate done")
    bullet = "- rename the slug helper: contract-a"
    seed = ("# Plan for #42\n\n" + phased + "\n- [ ] strip edge hyphens\n\n## Owed steps\n\n" + bullet + "\n").encode()
    owed = seed.replace(phased.encode(), (phased + " ⟂ contract-a owed").encode())
    ledger = tmp_path / "ledger.md"
    ledger.write_bytes(seed)

    codes = [tick_ledger.main(argv) for argv in (
        ["--phase-owed", "contract-a", str(ledger), "rename the slug helper"],
        ["--phase", "contract-a", str(ledger), "rename the slug helper"],
        [str(ledger), "rename the slug helper"],
    )]
    capsysbinary.readouterr()
    text = ledger.read_bytes().decode()
    step = next(line for line in text.split("\n") if "rename the slug helper ⟦" in line)

    assert (codes, ledger.read_bytes()) == ([0, 2, 2], owed)
    assert (step.startswith("- [ ] "), step.endswith(" ⟂ contract-a owed"), " ⟂ contract-a done" in step,
            text.split("## Owed steps\n\n")[1]) == (True, True, False, bullet + "\n")


def test_main_with_phase_owed_refuses_a_phase_other_than_a_contract_with_exit_2_naming_it_and_leaving_the_ledger_byte_identical_1430(
        tmp_path, capsysbinary, tick_ledger):
    listed = "- [ ] rename the slug helper ⟦phases: expand, migrate, contract-a, contract-b⟧ ⟦criterion 1⟧"
    marks = {
        "expand": "",
        "migrate": " ⟂ expand done",
        "contract-a": " ⟂ expand done ⟂ migrate done",
        "contract-b": " ⟂ expand done ⟂ migrate done ⟂ contract-a done",
    }
    ledger = tmp_path / "ledger.md"
    seeds, results = {}, {}
    for phase, done in marks.items():
        seeds[phase] = ("# Plan for #42\n\n" + listed + done + "\n- [ ] strip edge hyphens\n").encode()
        ledger.write_bytes(seeds[phase])
        code = tick_ledger.main(["--phase-owed", phase, str(ledger), "rename the slug helper"])
        out, err = capsysbinary.readouterr()
        results[phase] = (code, out, phase.encode() in err, ledger.read_bytes())

    def owed(phase):
        line = listed + marks[phase]
        return seeds[phase].replace(line.encode(), (line + f" ⟂ {phase} owed").encode())

    assert results == {
        "expand": (2, b"", True, seeds["expand"]),
        "migrate": (2, b"", True, seeds["migrate"]),
        "contract-a": (0, b"", False, owed("contract-a")),
        "contract-b": (0, b"", False, owed("contract-b")),
    }


def test_main_with_phase_owed_marks_only_skill_md_contract_a_and_contract_b_owed_refusing_any_other_spelling_with_exit_2_leaving_the_ledger_byte_identical_1446(
        tmp_path, capsysbinary, tick_ledger):
    listed = {
        "contract-a": "- [ ] rename the slug helper ⟦phases: expand, migrate, contract-a, contract-b⟧ ⟦criterion 1⟧",
        "contract (a)": "- [ ] rename the slug helper ⟦phases: expand, migrate, contract (a), contract (b)⟧ ⟦criterion 1⟧",
    }
    cases = {
        "expand": (listed["contract-a"], ""),
        "contract-a": (listed["contract-a"], " ⟂ expand done ⟂ migrate done"),
        "contract-b": (listed["contract-a"], " ⟂ expand done ⟂ migrate done ⟂ contract-a done"),
        "contract (a)": (listed["contract (a)"], " ⟂ expand done ⟂ migrate done"),
        "contract (b)": (listed["contract (a)"], " ⟂ expand done ⟂ migrate done ⟂ contract (a) done"),
    }
    ledger = tmp_path / "ledger.md"
    seeds, results = {}, {}
    for phase, (step, done) in cases.items():
        seeds[phase] = ("# Plan for #42\n\n" + step + done + "\n- [ ] strip edge hyphens\n").encode()
        ledger.write_bytes(seeds[phase])
        code = tick_ledger.main(["--phase-owed", phase, str(ledger), "rename the slug helper"])
        out, err = capsysbinary.readouterr()
        results[phase] = (code, out, ledger.read_bytes())

    def owed(phase):
        line = "".join(cases[phase])
        return seeds[phase].replace(line.encode(), (line + f" ⟂ {phase} owed").encode())

    assert results == {
        "expand": (2, b"", seeds["expand"]),
        "contract-a": (0, b"", owed("contract-a")),
        "contract-b": (0, b"", owed("contract-b")),
        "contract (a)": (2, b"", seeds["contract (a)"]),
        "contract (b)": (2, b"", seeds["contract (b)"]),
    }


def test_main_accepts_a_ledger_written_to_skill_md_phase_line_end_to_end_next_phase_printing_contract_a_and_phase_and_phase_owed_both_marking_it_1446(
        tmp_path, monkeypatch, capsysbinary, tick_ledger):
    ledger_steps = importlib.import_module("veri.ledger_steps")
    phased = "- [ ] rename the slug helper ⟦phases: expand, migrate, contract-a, contract-b⟧ ⟦criterion 1⟧"
    seed = ("# Plan for #42\n\n- [x] add lowercasing\n" + phased + "\n- [ ] strip edge hyphens\n").encode()
    ledger = tmp_path / "ledger.md"
    ledger.write_bytes(seed)

    marked = [tick_ledger.main(["--phase", phase, str(ledger), "rename the slug helper"]) for phase in ("expand", "migrate")]
    capsysbinary.readouterr()
    monkeypatch.setattr(sys, "stdin", io.TextIOWrapper(io.BytesIO(ledger.read_bytes())))
    next_code = ledger_steps.main(["next-phase"])
    next_out, _ = capsysbinary.readouterr()
    ready = ledger.read_bytes()
    results = {}
    for flag in ("--phase", "--phase-owed"):
        ledger.write_bytes(ready)
        code = tick_ledger.main([flag, "contract-a", str(ledger), "rename the slug helper"])
        results[flag] = (code, *capsysbinary.readouterr(), ledger.read_bytes())

    line = phased + " ⟂ expand done ⟂ migrate done"
    assert (marked, next_code, next_out, ready, results) == (
        [0, 0], 0, b"contract-a\n", seed.replace(phased.encode(), line.encode()), {
            "--phase": (0, b"", b"", ready.replace(line.encode(), (line + " ⟂ contract-a done").encode())),
            "--phase-owed": (0, b"", b"", ready.replace(line.encode(), (line + " ⟂ contract-a owed").encode())),
        })


def test_main_ticks_a_step_whose_prose_quotes_a_phases_marker_with_a_plain_tick_and_no_phase_refusal_1450(
        tmp_path, capsysbinary, tick_ledger):
    quoting = "- [ ] tick-ledger.sh refuses a step carrying ⟦phases: expand⟧ a plain tick ⟦criterion 2⟧"
    seed = ("# Plan for #42\n\n- [x] add lowercasing\n" + quoting + "\n- [ ] later\n").encode()
    ledger = tmp_path / "ledger.md"
    ledger.write_bytes(seed)

    code = tick_ledger.main(["--refactor-pending", str(ledger), "tick-ledger.sh refuses"])

    assert (code, *capsysbinary.readouterr(), ledger.read_bytes()) == (
        0, b"", b"", seed.replace(quoting.encode(), (quoting.replace("[ ]", "[x]") + " ⟂ refactor pending").encode()))


STEPS = "# Plan for #42\n\n- [ ] add lowercasing\n- [ ] collapse to single hyphen\n- [ ] strip edge hyphens\n"


def test_cli_ticks_the_matching_step_in_place_leaving_the_other_steps_open(tmp_path, run_cli, tick_ledger):
    ledger = tmp_path / "issue-42.md"
    ledger.write_text(STEPS)

    code, out, err = run_cli(tick_ledger, [str(ledger), "collapse to single hyphen"])

    assert (code, out, err, ledger.read_text()) == (
        0, "", "", STEPS.replace("- [ ] collapse", "- [x] collapse"))


def test_cli_exits_3_on_an_unmatched_step_leaving_the_ledger_unchanged(tmp_path, run_cli, tick_ledger):
    ledger = tmp_path / "issue-42.md"
    ledger.write_text(STEPS)

    code, out, err = run_cli(tick_ledger, [str(ledger), "nonexistent step"])

    assert (code, out, err, ledger.read_text()) == (3, "", "", STEPS)


def test_cli_with_no_argument_exits_2_with_nothing_on_stdout_and_the_usage_line_on_stderr(run_cli, tick_ledger):
    code, out, err = run_cli(tick_ledger, [])

    assert (code, out, err) == (2, "", USAGE.decode())


def test_cli_usage_line_names_unpinnable_and_already_holds_with_their_reason_file(run_cli, tick_ledger):
    code, out, err = run_cli(tick_ledger, [])

    assert (code, "--unpinnable <reason-file>" in err, "--already-holds <reason-file>" in err) == (2, True, True)


def test_cli_exits_2_with_one_stderr_line_naming_a_directory_ledger_and_the_reason_without_a_traceback(
        tmp_path, run_cli, tick_ledger):
    ledger = tmp_path / "dir-ledger.md"
    ledger.mkdir()

    code, out, err = run_cli(tick_ledger, [str(ledger), "collapse to single hyphen"])

    assert (code, out, err.count("\n"), str(ledger) in err, "directory" in err.lower(), "Traceback" in err) == (
        2, "", 1, True, True, False)


def test_cli_exits_2_with_one_stderr_line_naming_a_ledger_path_that_does_not_exist_without_a_traceback(
        tmp_path, run_cli, tick_ledger):
    ledger = tmp_path / "absent-ledger.md"

    code, out, err = run_cli(tick_ledger, [str(ledger), "collapse to single hyphen"])

    assert (code, out, err.count("\n"), str(ledger) in err, "Traceback" in err) == (2, "", 1, True, False)


def test_cli_exits_2_with_one_path_and_reason_stderr_line_for_a_ledger_path_running_through_a_regular_file_writing_nothing(
        tmp_path, run_cli, tick_ledger):
    plain = tmp_path / "plain-file"
    plain.write_text("not a directory\n")
    ledger = plain / "issue-42.md"

    code, out, err = run_cli(tick_ledger, [str(ledger), "collapse to single hyphen"])

    assert (code, out, err.count("\n"), err.startswith(f"tick-ledger.sh: {ledger}: "),
            len(err) > len(f"tick-ledger.sh: {ledger}: ") + 1, "Traceback" in err, plain.read_text()) == (
        2, "", 1, True, True, False, "not a directory\n")


def test_cli_of_tick_ledger_and_clear_refactor_pending_exit_3_on_no_match_and_0_on_a_tick_or_clear(
        tmp_path, run_cli, tick_ledger, leave_receipt):
    clear = importlib.import_module("veri.clear_refactor_pending")
    ledger = tmp_path / "issue-42.md"
    ledger.write_text(STEPS)
    leave_receipt(ledger)

    tick_miss = run_cli(tick_ledger, [str(ledger), "nonexistent step"])[0]
    tick_hit = run_cli(tick_ledger, ["--refactor-pending", str(ledger), "collapse to single hyphen"])[0]
    clear_miss = run_cli(clear, [str(ledger), "nonexistent step"])[0]
    clear_hit = run_cli(clear, [str(ledger), "collapse to single hyphen"])[0]

    assert (tick_miss, tick_hit, clear_miss, clear_hit) == (3, 0, 3, 0)
    assert ledger.read_text() == STEPS.replace("- [ ] collapse", "- [x] collapse")


def test_cli_without_refactor_pending_ticks_an_unchecked_suite_repair_line_leaving_no_refactor_pending_mark_2099(
        tmp_path, run_cli, tick_ledger):
    ledger = tmp_path / "issue-42.md"
    ledger.write_text("- [x] add lowercasing\n- [ ] fix the full-suite failure: suite_x ⟦suite-repair⟧\n")

    code = run_cli(tick_ledger, [str(ledger), "⟦suite-repair⟧"])[0]

    assert code == 0
    assert ledger.read_text() == "- [x] add lowercasing\n- [x] fix the full-suite failure: suite_x ⟦suite-repair⟧\n"


def test_main_refuses_a_tick_of_a_step_naming_a_go_red_control_with_no_mutation_record_leaving_the_ledger_untouched_2952(
        tmp_path, capsys, tick_ledger):
    ledger = tmp_path / "issue-7.md"
    seed = ("# Plan for #7\n\n- [ ] A refused start leaves no temp directory behind: the go-red control is "
            "scripts/smoke-core.mjs at ab20a4945 ⟦added⟧ ⟦criterion 3⟧\n").encode()
    ledger.write_bytes(seed)

    code = tick_ledger.main([str(ledger), "A refused start"])
    err = capsys.readouterr().err

    assert (code, "mutations" in err, ledger.read_bytes()) == (2, True, seed)


def test_main_refuses_a_tick_of_a_step_naming_mutation_probe_before_a_sha_with_no_mutation_record_leaving_the_ledger_untouched_2952(
        tmp_path, capsys, tick_ledger):
    ledger = tmp_path / "issue-7.md"
    seed = ("# Plan for #7\n\n- [ ] A refused start leaves no temp directory behind: prove the go-red with "
            "mutation-probe.sh --before 84603a1e8 ⟦added⟧ ⟦criterion 3⟧\n").encode()
    ledger.write_bytes(seed)

    code = tick_ledger.main([str(ledger), "A refused start"])
    err = capsys.readouterr().err

    assert (code, "mutations" in err, ledger.read_bytes()) == (2, True, seed)


def test_main_ticks_a_step_naming_a_before_sha_once_the_mutation_record_holds_a_before_record_for_that_sha_2952(
        tmp_path, tick_ledger):
    ledger = tmp_path / "issue-7.md"
    ledger.write_text("# Plan for #7\n\n- [ ] A refused start leaves no temp directory behind: prove the go-red with "
                      "mutation-probe.sh --before 84603a1e8 ⟦added⟧ ⟦criterion 3⟧\n")
    (tmp_path / "issue-7-mutations.md").write_text(
        "before 9\n84603a1e8\nkeep 4\nt.py\ncommand 6\npytest\ngreen 1\n0\n\n")

    code = tick_ledger.main([str(ledger), "A refused start"])

    assert (code, "- [x] A refused start" in ledger.read_text()) == (0, True)


def test_main_refuses_a_tick_of_a_step_naming_a_before_sha_when_the_mutation_record_holds_only_a_before_record_for_a_different_sha_2952(
        tmp_path, capsys, tick_ledger):
    ledger = tmp_path / "issue-7.md"
    seed = ("# Plan for #7\n\n- [ ] A refused start leaves no temp directory behind: prove the go-red with "
            "mutation-probe.sh --before 84603a1e8 ⟦added⟧ ⟦criterion 3⟧\n").encode()
    ledger.write_bytes(seed)
    (tmp_path / "issue-7-mutations.md").write_text(
        "before 9\n58beded4d\nkeep 4\nt.py\ncommand 6\npytest\ngreen 1\n0\n\n")

    code = tick_ledger.main([str(ledger), "A refused start"])
    err = capsys.readouterr().err

    assert (code, "mutations" in err, ledger.read_bytes()) == (2, True, seed)


def test_main_ticks_a_step_naming_its_go_red_control_file_once_the_mutation_record_holds_a_file_old_new_record_for_that_file_2952(
        tmp_path, tick_ledger):
    ledger = tmp_path / "issue-7.md"
    ledger.write_text("# Plan for #7\n\n- [ ] A refused start leaves no temp directory behind: the go-red control is "
                      "scripts/smoke-core.mjs at ab20a4945 ⟦added⟧ ⟦criterion 3⟧\n")
    (tmp_path / "issue-7-mutations.md").write_text(
        "file 22\nscripts/smoke-core.mjs\nold 3\nabc\nnew 3\nxyz\ncommand 6\npytest\n\n")

    code = tick_ledger.main([str(ledger), "A refused start"])

    assert (code, "- [x] A refused start" in ledger.read_text()) == (0, True)


def test_main_refuses_a_tick_of_a_step_naming_its_go_red_control_file_when_the_mutation_record_holds_only_a_file_old_new_record_for_a_different_file_2952(
        tmp_path, capsys, tick_ledger):
    ledger = tmp_path / "issue-7.md"
    seed = ("# Plan for #7\n\n- [ ] A refused start leaves no temp directory behind: the go-red control is "
            "scripts/smoke-core.mjs at ab20a4945 ⟦added⟧ ⟦criterion 3⟧\n").encode()
    ledger.write_bytes(seed)
    (tmp_path / "issue-7-mutations.md").write_text(
        "file 20\nscripts/other-file.mjs\nold 3\nabc\nnew 3\nxyz\ncommand 6\npytest\n\n")

    code = tick_ledger.main([str(ledger), "A refused start"])
    err = capsys.readouterr().err

    assert (code, "mutations" in err, ledger.read_bytes()) == (2, True, seed)


def test_main_refuses_a_tick_of_a_step_naming_a_go_red_control_file_with_regex_metacharacters_when_the_record_names_a_file_the_unescaped_name_would_match_2952(
        tmp_path, capsys, tick_ledger):
    ledger = tmp_path / "issue-7.md"
    seed = ("# Plan for #7\n\n- [ ] A refused start leaves no temp directory behind: the go-red control is "
            "scripts/smoke-core.mjs at ab20a4945 ⟦added⟧ ⟦criterion 3⟧\n").encode()
    ledger.write_bytes(seed)
    (tmp_path / "issue-7-mutations.md").write_text(
        "file 20\nscripts/smoke-core_mjs\nold 3\nabc\nnew 3\nxyz\ncommand 6\npytest\n\n")

    code = tick_ledger.main([str(ledger), "A refused start"])
    err = capsys.readouterr().err

    assert (code, "mutations" in err, ledger.read_bytes()) == (2, True, seed)


def test_main_ticks_a_step_mentioning_go_red_control_bare_with_neither_wording_and_no_mutation_record_exiting_0_2952(
        tmp_path, tick_ledger):
    ledger = tmp_path / "issue-7.md"
    ledger.write_text("# Plan for #7\n\n- [ ] A refused start leaves no temp directory behind: the go-red control "
                      "needs no record here ⟦added⟧ ⟦criterion 3⟧\n")

    code = tick_ledger.main([str(ledger), "A refused start"])

    assert (code, "- [x] A refused start" in ledger.read_text()) == (0, True)


def test_main_ticks_a_step_naming_its_go_red_control_file_at_a_sha_once_the_mutation_record_holds_a_before_record_for_that_sha_2952(
        tmp_path, tick_ledger):
    ledger = tmp_path / "issue-7.md"
    ledger.write_text("# Plan for #7\n\n- [ ] A refused start leaves no temp directory behind: the go-red control is "
                      "scripts/smoke-core.mjs at ab20a4945 ⟦added⟧ ⟦criterion 3⟧\n")
    (tmp_path / "issue-7-mutations.md").write_text(
        "before 9\nab20a4945\nkeep 4\nt.py\ncommand 6\npytest\ngreen 1\n0\n\n")

    code = tick_ledger.main([str(ledger), "A refused start"])

    assert (code, "- [x] A refused start" in ledger.read_text()) == (0, True)


def test_main_ticks_a_already_satisfied_step_with_no_mutation_record_exiting_0_2952(tmp_path, tick_ledger):
    ledger = tmp_path / "issue-7.md"
    ledger.write_text("# Plan for #7\n\n- [ ] the PR body lists the cogs ⟦added⟧ ⟦already-satisfied⟧ ⟦criterion 4⟧\n")

    code = tick_ledger.main([str(ledger), "the PR body lists the cogs"])

    assert (code, "- [x] the PR body lists the cogs" in ledger.read_text()) == (0, True)


def test_main_ticks_a_human_owed_step_with_no_mutation_record_exiting_0_2952(tmp_path, tick_ledger):
    ledger = tmp_path / "issue-7.md"
    ledger.write_text("# Plan for #7\n\n- [ ] the PR body lists the cogs ⟦added⟧ ⟦human-owed⟧ ⟦criterion 4⟧\n")

    code = tick_ledger.main([str(ledger), "the PR body lists the cogs"])

    assert (code, "- [x] the PR body lists the cogs" in ledger.read_text()) == (0, True)


def test_main_ticks_a_skill_edit_step_with_no_mutation_record_exiting_0_2952(tmp_path, tick_ledger):
    ledger = tmp_path / "issue-7.md"
    ledger.write_text("# Plan for #7\n\n- [ ] the PR body lists the cogs ⟦added⟧ ⟦skill-edit⟧ ⟦criterion 4⟧\n")

    code = tick_ledger.main([str(ledger), "the PR body lists the cogs"])

    assert (code, "- [x] the PR body lists the cogs" in ledger.read_text()) == (0, True)


def test_main_returns_2_naming_pin_recheck_sh_and_leaves_the_ledger_byte_identical_when_ticking_a_diff_checked_step_with_the_pin_recheck_receipt_absent_2972(
        tmp_path, capsysbinary, monkeypatch, tick_ledger):
    monkeypatch.setattr(sys.modules["tests_frozen"], "rerecord_earlier", lambda *args: 0)
    seed = "# Plan for #7\n\n- [ ] the PR body lists the cogs ⟦diff-checked⟧ ⟦criterion 4⟧\n".encode()
    led = tmp_path / "issue-7.md"
    led.write_bytes(seed)

    code = tick_ledger.main([str(led), "the PR body lists the cogs"])

    out, err = capsysbinary.readouterr()
    assert (code, out, b"pin-recheck.sh" in err, led.read_bytes()) == (2, b"", True, seed)


def test_main_returns_2_naming_pin_recheck_sh_and_leaves_the_ledger_byte_identical_when_the_diff_checked_tick_receipt_sha_does_not_resolve_in_git_2972(
        tmp_path, capsysbinary, monkeypatch, tick_ledger):
    import importlib
    import subprocess
    monkeypatch.setattr(sys.modules["tests_frozen"], "rerecord_earlier", lambda *args: 0)
    unresolved = lambda *args, **kwargs: subprocess.CompletedProcess(args, 128, "", "fatal: bad object")
    reals = {importlib.import_module(name).git for name in ("veri.git", "git")}
    for module in list(sys.modules.values()):
        if getattr(module, "git", None) in reals:
            monkeypatch.setattr(module, "git", unresolved)
    seed = "# Plan for #7\n\n- [ ] the PR body lists the cogs ⟦diff-checked⟧ ⟦criterion 4⟧\n".encode()
    led = tmp_path / "issue-7.md"
    led.write_bytes(seed)
    (tmp_path / "pin-recheck-ok").write_text("deadbeef" * 5 + "\n")

    code = tick_ledger.main([str(led), "the PR body lists the cogs"])

    out, err = capsysbinary.readouterr()
    assert (code, out, b"pin-recheck.sh" in err, led.read_bytes()) == (2, b"", True, seed)


def test_main_ticks_a_diff_checked_step_whose_receipt_matches_head_resolving_it_in_the_ledgers_repository_from_a_cwd_outside_it_2972(
        tmp_path, capsysbinary, monkeypatch, tick_ledger):
    import pathlib
    import subprocess
    monkeypatch.setattr(sys.modules["tests_frozen"], "rerecord_earlier", lambda *args: 0)
    repo = tmp_path / "repo"
    (repo / ".tdd").mkdir(parents=True)
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    head = "c" * 40

    def faked_git(*args, **kwargs):
        text = kwargs.get("text") or kwargs.get("universal_newlines")
        where = args[args.index("-C") + 1] if "-C" in args else kwargs.get("cwd") or os.getcwd()
        inside = pathlib.Path(where).resolve().is_relative_to(repo.resolve())
        out = (head + "\n" if "rev-parse" in args else "") if inside else ""
        err = "" if inside else "fatal: not a git repository\n"
        return subprocess.CompletedProcess(args, 0 if inside else 128,
                                           out if text else out.encode(), err if text else err.encode())

    reals = {importlib.import_module(name).git for name in ("veri.git", "git")}
    for module in list(sys.modules.values()):
        if getattr(module, "git", None) in reals:
            monkeypatch.setattr(module, "git", faked_git)
    led = repo / ".tdd" / "issue-7.md"
    led.write_text("# Plan for #7\n\n- [ ] the PR body lists the cogs ⟦diff-checked⟧ ⟦criterion 4⟧\n")
    (repo / ".tdd" / "pin-recheck-ok").write_text(head + "\n")
    monkeypatch.chdir(elsewhere)

    code = tick_ledger.main([str(led), "the PR body lists the cogs"])

    assert (code, "- [x] the PR body lists the cogs" in led.read_text()) == (0, True)


def test_main_returns_2_naming_pin_recheck_sh_and_leaves_the_ledger_byte_identical_when_ticking_a_diff_checked_step_and_a_path_outside_tdd_differs_since_the_receipts_sha_2972(
        tmp_path, capsysbinary, monkeypatch, tick_ledger):
    import importlib
    import subprocess
    monkeypatch.setattr(sys.modules["tests_frozen"], "rerecord_earlier", lambda *args: 0)

    def faked_git(*args, **kwargs):
        text = kwargs.get("text") or kwargs.get("universal_newlines")
        out = "b" * 40 + "\n" if args[:1] == ("rev-parse",) else "src/changed.py\n"
        return subprocess.CompletedProcess(args, 0, out if text else out.encode(), "" if text else b"")

    reals = {importlib.import_module(name).git for name in ("veri.git", "git")}
    for module in list(sys.modules.values()):
        if getattr(module, "git", None) in reals:
            monkeypatch.setattr(module, "git", faked_git)
    seed = "# Plan for #7\n\n- [ ] the PR body lists the cogs ⟦diff-checked⟧ ⟦criterion 4⟧\n".encode()
    led = tmp_path / "issue-7.md"
    led.write_bytes(seed)
    (tmp_path / "pin-recheck-ok").write_text("a" * 40 + "\n")

    code = tick_ledger.main([str(led), "the PR body lists the cogs"])

    out, err = capsysbinary.readouterr()
    assert (code, out, b"pin-recheck.sh" in err, led.read_bytes()) == (2, b"", True, seed)


def test_main_ticks_a_step_not_marked_diff_checked_with_no_pin_recheck_receipt_for_a_plain_refactor_pending_and_phase_tick_2972(
        tmp_path, capsysbinary, tick_ledger):
    phased = "- [ ] rename the slug helper ⟦phases: expand, migrate, contract-a, contract-b⟧ ⟦criterion 1⟧"
    runs = {
        "plain": ([], "- [ ] add lowercasing ⟦criterion 2⟧", "add lowercasing"),
        "pending": (["--refactor-pending"], "- [ ] add lowercasing ⟦criterion 2⟧", "add lowercasing"),
        "phase": (["--phase", "expand"], phased, "rename the slug helper"),
    }
    results = {}
    for name, (flags, step, matcher) in runs.items():
        directory = tmp_path / name
        directory.mkdir()
        led = directory / "issue-7.md"
        led.write_text("# Plan for #7\n\n" + step + "\n")
        code = tick_ledger.main([*flags, str(led), matcher])
        _, err = capsysbinary.readouterr()
        results[name] = (code, b"pin-recheck.sh" in err, led.read_text() != "# Plan for #7\n\n" + step + "\n")

    assert results == {name: (0, False, True) for name in runs}


def test_cli_ticking_an_added_step_ticks_its_line_in_the_added_file_leaving_every_other_line_and_the_growth_verdict_unchanged_2976(
        tmp_path, run_cli, tick_ledger):
    ledger_growth = importlib.import_module("veri.ledger_growth")
    planned = "- [ ] add lowercasing ⟦criterion 1⟧\n"
    first = "- [ ] reject a blank slug ⟦added⟧ ⟦criterion 2⟧\n"
    second = "- [ ] keep unicode letters ⟦added⟧ ⟦criterion 3⟧\n"
    plan = tmp_path / "plan.md"
    plan.write_text("# Plan for #7\n\n" + planned)
    ledger = tmp_path / "issue-7.md"
    ledger.write_text("# Plan for #7\n\n" + planned + first + second)
    added = tmp_path / "issue-7-added.md"
    added.write_text(first + second)
    verdict_before = run_cli(ledger_growth, [str(plan), str(ledger)])[0]

    code = run_cli(tick_ledger, [str(ledger), "reject a blank slug"])[0]
    verdict_after = run_cli(ledger_growth, [str(plan), str(ledger)])[0]

    assert (code, added.read_text(), verdict_before, verdict_after) == (
        0, first.replace("- [ ]", "- [x]") + second, 0, 0)


def test_cli_with_an_added_file_leaves_it_byte_identical_for_a_planned_step_or_a_failed_ledger_write_and_ticks_only_the_equal_line_for_an_added_step_2976(
        tmp_path, run_cli, tick_ledger, monkeypatch):
    planned = "- [ ] add lowercasing ⟦criterion 1⟧\n"
    first = "- [ ] reject a blank slug ⟦added⟧ ⟦criterion 2⟧\n"
    second = "- [ ] keep unicode letters ⟦added⟧ ⟦criterion 3⟧\n"
    seed = "# Plan for #7\n\n" + planned + first + second
    added = tmp_path / "issue-7-added.md"
    results = {}
    for name in ("planned", "write-fails", "added"):
        ledger = tmp_path / f"{name}" / "issue-7.md"
        ledger.parent.mkdir()
        ledger.write_text(seed)
        added = ledger.parent / "issue-7-added.md"
        added.write_text(first + second)
        matcher = "add lowercasing" if name == "planned" else "keep unicode letters"
        if name == "write-fails":
            monkeypatch.setattr(tick_ledger.ledger, "replace_ledger",
                                lambda *_: (_ for _ in ()).throw(OSError("full")))
        results[name] = (run_cli(tick_ledger, [str(ledger), matcher])[0], added.read_text())
        monkeypatch.undo()

    assert results == {
        "planned": (0, first + second),
        "write-fails": (2, first + second),
        "added": (0, first + second.replace("- [ ]", "- [x]")),
    }


def test_cli_ticking_an_added_step_with_refactor_pending_ticks_the_first_still_open_line_of_equal_step_text_in_the_added_file_2976(
        tmp_path, run_cli, tick_ledger):
    done = "- [x] reject a blank slug ⟦added⟧ ⟦criterion 2⟧\n"
    open_line = "- [ ] reject a blank slug ⟦added⟧ ⟦criterion 2⟧\n"
    other = "- [ ] keep unicode letters ⟦added⟧ ⟦criterion 3⟧\n"
    ledger = tmp_path / "issue-7.md"
    ledger.write_text("# Plan for #7\n\n" + open_line + other)
    added = tmp_path / "issue-7-added.md"
    added.write_text(done + open_line + other)

    code = run_cli(tick_ledger, ["--refactor-pending", str(ledger), "reject a blank slug"])[0]

    assert (code, added.read_text()) == (0, done + done + other)


def test_cli_ticking_an_added_step_ticks_only_the_first_of_two_still_open_added_lines_with_equal_step_text_2976(
        tmp_path, run_cli, tick_ledger):
    open_line = "- [ ] reject a blank slug ⟦added⟧ ⟦criterion 2⟧\n"
    ledger = tmp_path / "issue-7.md"
    ledger.write_text("# Plan for #7\n\n" + open_line)
    added = tmp_path / "issue-7-added.md"
    added.write_text(open_line + open_line)

    code = run_cli(tick_ledger, [str(ledger), "reject a blank slug"])[0]

    assert (code, added.read_text()) == (0, open_line.replace("- [ ]", "- [x]") + open_line)


def test_main_unpinnable_retire_keeps_a_mutation_record_whose_tests_names_a_class_qualified_case_that_exists_3289(
        tmp_path, tick_ledger, monkeypatch):
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_a.py").write_text(
        "class TestK:\n    def test_b(self):\n        pass\n")
    tdd = tmp_path / ".tdd"
    tdd.mkdir()
    ledger = tdd / "issue-7.md"
    ledger.write_text("# Plan for #7\n\n- [ ] Pin the thing ⟦criterion 1⟧\n")
    reason = tmp_path / "reason.txt"
    reason.write_text("the case stays green\n")
    command = "pytest TESTS=tests/test_a.py::TestK::test_b"
    record = f"command {len(command)}\n{command}\n\n"
    mutations = tdd / "issue-7-mutations.md"
    mutations.write_text(record)

    monkeypatch.setattr(tick_ledger, "run_case", lambda case, *rest, **kw: 0, raising=False)

    code = tick_ledger.main(["--unpinnable", str(reason), "--case", "tests/py/test_x.py::test_holds", str(ledger), "Pin the thing"])

    assert (code, mutations.read_text()) == (0, record)


def test_main_unpinnable_retire_drops_a_mutation_record_whose_tests_names_a_file_that_does_not_exist_3289(
        tmp_path, tick_ledger, monkeypatch):
    tdd = tmp_path / ".tdd"
    tdd.mkdir()
    ledger = tdd / "issue-7.md"
    ledger.write_text("# Plan for #7\n\n- [ ] Pin the thing ⟦criterion 1⟧\n")
    reason = tmp_path / "reason.txt"
    reason.write_text("the case stays green\n")
    command = "pytest TESTS=tests/test_gone.py::test_never_written"
    mutations = tdd / "issue-7-mutations.md"
    mutations.write_text(f"command {len(command)}\n{command}\n\n")

    monkeypatch.setattr(tick_ledger, "run_case", lambda case, *rest, **kw: 0, raising=False)

    code = tick_ledger.main(["--unpinnable", str(reason), "--case", "tests/py/test_x.py::test_holds", str(ledger), "Pin the thing"])

    assert (code, mutations.read_text()) == (0, "")


def test_main_unpinnable_retire_over_a_malformed_mutation_record_returns_2_naming_that_record_on_stderr_3289(
        tmp_path, capsys, tick_ledger, monkeypatch):
    tdd = tmp_path / ".tdd"
    tdd.mkdir()
    ledger = tdd / "issue-7.md"
    ledger.write_text("# Plan for #7\n\n- [ ] Pin the thing ⟦criterion 1⟧\n")
    reason = tmp_path / "reason.txt"
    reason.write_text("the case stays green\n")
    mutations = tdd / "issue-7-mutations.md"
    mutations.write_text("garbled\n\n")

    monkeypatch.setattr(tick_ledger, "run_case", lambda case, *rest, **kw: 0, raising=False)

    code = tick_ledger.main(["--unpinnable", str(reason), "--case", "tests/py/test_x.py::test_holds", str(ledger), "Pin the thing"])

    assert (code, "garbled" in capsys.readouterr().err) == (2, True)


def test_main_unpinnable_retire_over_a_mutation_record_with_a_non_numeric_size_returns_2_naming_that_record_on_stderr_3289(
        tmp_path, capsys, tick_ledger, monkeypatch):
    tdd = tmp_path / ".tdd"
    tdd.mkdir()
    ledger = tdd / "issue-7.md"
    ledger.write_text("# Plan for #7\n\n- [ ] Pin the thing ⟦criterion 1⟧\n")
    reason = tmp_path / "reason.txt"
    reason.write_text("the case stays green\n")
    mutations = tdd / "issue-7-mutations.md"
    mutations.write_text("name abc\n\n")

    monkeypatch.setattr(tick_ledger, "run_case", lambda case, *rest, **kw: 0, raising=False)

    code = tick_ledger.main(["--unpinnable", str(reason), "--case", "tests/py/test_x.py::test_holds", str(ledger), "Pin the thing"])

    assert (code, "name abc" in capsys.readouterr().err) == (2, True)
