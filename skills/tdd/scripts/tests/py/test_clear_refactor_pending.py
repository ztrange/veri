"""In-process cases for veri/clear_refactor_pending.py, the module clear-refactor-pending.sh is a shim over."""
import builtins
import errno
import importlib
import os
import pathlib
import resource
import sys
import tempfile

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
for path in (SCRIPTS, SCRIPTS / "veri"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

USAGE = b"usage: clear-refactor-pending.sh <ledger-file> <matcher>\n"


@pytest.fixture
def clear_refactor_pending():
    return importlib.import_module("veri.clear_refactor_pending")


def test_main_refuses_a_missing_or_empty_ledger_file_clears_the_first_matching_mark_and_exits_3_leaving_an_unmatched_ledger_untouched(
        tmp_path, capsysbinary, clear_refactor_pending):
    seed = "- [x] a ⟂ refactor pending\n- [x] b ⟂ refactor pending\n".encode()
    cleared = tmp_path / "cleared.md"
    cleared.write_bytes(seed)
    unmatched = tmp_path / "unmatched.md"
    unmatched.write_bytes(seed)
    results = {}
    for argv in ([], [""], [str(cleared), "a"], [str(unmatched), "zeta"]):
        code = clear_refactor_pending.main(argv)
        results[tuple(argv)] = (code, *capsysbinary.readouterr())

    assert results == {
        (): (2, b"", USAGE),
        ("",): (2, b"", USAGE),
        (str(cleared), "a"): (0, b"", b""),
        (str(unmatched), "zeta"): (3, b"", b""),
    }
    assert cleared.read_bytes() == "- [x] a\n- [x] b ⟂ refactor pending\n".encode()
    assert unmatched.read_bytes() == seed


def test_main_writes_what_the_ledger_modules_ledger_clear_pending_returns_and_passes_it_the_matcher(
        tmp_path, monkeypatch, capsysbinary, clear_refactor_pending):
    matchers = []

    def substitute(text, matcher):
        matchers.append(matcher)
        return True, f"cleared by the module: {matcher}\n"

    monkeypatch.setattr(sys.modules["ledger"], "ledger_clear_pending", substitute)
    led = tmp_path / "issue-42.md"
    led.write_bytes("- [x] collapse to single hyphen ⟂ refactor pending\n".encode())

    code = clear_refactor_pending.main([str(led), "collapse to single hyphen"])

    assert (code, *capsysbinary.readouterr()) == (0, b"", b"")
    assert matchers == ["collapse to single hyphen"]
    assert led.read_bytes() == b"cleared by the module: collapse to single hyphen\n"


def test_main_returns_2_leaving_the_ledger_byte_identical_when_the_ledger_modules_ledger_clear_pending_hands_back_status_7(
        tmp_path, monkeypatch, capsysbinary, clear_refactor_pending):
    def substitute(text, matcher):
        return 7, "written by a foreign status\n"

    monkeypatch.setattr(sys.modules["ledger"], "ledger_clear_pending", substitute)
    seed = "- [x] a ⟂ refactor pending\n".encode()
    led = tmp_path / "issue-42.md"
    led.write_bytes(seed)

    code = clear_refactor_pending.main([str(led), "a"])

    assert (code, *capsysbinary.readouterr()) == (2, b"", b"")
    assert led.read_bytes() == seed


def test_main_reads_a_lone_ledger_file_as_an_empty_matcher_clearing_the_first_marked_done_step_and_ignores_arguments_after_the_second(
        tmp_path, capsysbinary, clear_refactor_pending):
    seed = "- [x] a ⟂ refactor pending\n- [x] b ⟂ refactor pending\n".encode()
    lone = tmp_path / "lone.md"
    lone.write_bytes(seed)
    extra = tmp_path / "extra.md"
    extra.write_bytes(seed)
    results = {}
    for argv in ([str(lone)], [str(extra), "b", "zeta", "eta"]):
        code = clear_refactor_pending.main(argv)
        results[tuple(argv)] = (code, *capsysbinary.readouterr())

    assert results == {
        (str(lone),): (0, b"", b""),
        (str(extra), "b", "zeta", "eta"): (0, b"", b""),
    }
    assert lone.read_bytes() == "- [x] a\n- [x] b ⟂ refactor pending\n".encode()
    assert extra.read_bytes() == "- [x] a ⟂ refactor pending\n- [x] b\n".encode()


def test_main_matches_the_matcher_as_a_literal_substring_of_the_whole_line_box_and_mark_included(
        tmp_path, capsysbinary, clear_refactor_pending):
    seed = "- [x] a ⟂ refactor pending\n- [x] b * c ⟂ refactor pending\n".encode()
    results = {}
    for name, matcher in (("pending", "refactor pending"), ("box", "[x] a"), ("mark", "a ⟂"),
                          ("star", "*"), ("glob", "b*c")):
        led = tmp_path / f"{name}.md"
        led.write_bytes(seed)
        code = clear_refactor_pending.main([str(led), matcher])
        results[matcher] = (code, *capsysbinary.readouterr(), led.read_bytes())

    first_cleared = "- [x] a\n- [x] b * c ⟂ refactor pending\n".encode()
    assert results == {
        "refactor pending": (0, b"", b"", first_cleared),
        "[x] a": (0, b"", b"", first_cleared),
        "a ⟂": (0, b"", b"", first_cleared),
        "*": (0, b"", b"", "- [x] a ⟂ refactor pending\n- [x] b * c\n".encode()),
        "b*c": (3, b"", b"", seed),
    }


def test_main_exits_3_leaving_an_open_marked_step_a_crlf_mark_and_a_mark_before_a_space_untouched_and_clears_only_the_last_of_a_double_mark(
        tmp_path, capsysbinary, clear_refactor_pending):
    seeds = {
        "open": "- [ ] a ⟂ refactor pending\n".encode(),
        "crlf": "- [x] a ⟂ refactor pending\r\n".encode(),
        "space": "- [x] a ⟂ refactor pending \n".encode(),
        "double": "- [x] a ⟂ refactor pending ⟂ refactor pending\n".encode(),
    }
    results = {}
    for name, seed in seeds.items():
        led = tmp_path / f"{name}.md"
        led.write_bytes(seed)
        code = clear_refactor_pending.main([str(led), "a"])
        results[name] = (code, *capsysbinary.readouterr(), led.read_bytes())

    assert results == {
        "open": (3, b"", b"", seeds["open"]),
        "crlf": (3, b"", b"", seeds["crlf"]),
        "space": (3, b"", b"", seeds["space"]),
        "double": (0, b"", b"", "- [x] a ⟂ refactor pending\n".encode()),
    }


def test_main_rewrites_a_cleared_ledger_ending_in_exactly_one_newline_and_leaves_an_unmatched_or_empty_ledger_byte_identical(
        tmp_path, capsysbinary, clear_refactor_pending):
    seeds = {
        "unterminated": ("- [x] a ⟂ refactor pending".encode(), "a"),
        "triple": ("- [x] a ⟂ refactor pending\n\n\n".encode(), "a"),
        "unmatched": ("- [x] a ⟂ refactor pending\n\n\n".encode(), "zeta"),
        "empty": (b"", "a"),
    }
    results = {}
    for name, (seed, matcher) in seeds.items():
        led = tmp_path / f"{name}.md"
        led.write_bytes(seed)
        code = clear_refactor_pending.main([str(led), matcher])
        results[name] = (code, *capsysbinary.readouterr(), led.read_bytes())

    assert results == {
        "unterminated": (0, b"", b"", b"- [x] a\n"),
        "triple": (0, b"", b"", b"- [x] a\n"),
        "unmatched": (3, b"", b"", seeds["unmatched"][0]),
        "empty": (3, b"", b"", b""),
    }


def test_main_drops_a_nul_byte_on_a_clear_and_passes_a_non_utf8_byte_through_in_the_file_and_the_matcher(
        tmp_path, capsysbinary, clear_refactor_pending):
    nul = tmp_path / "nul.md"
    nul.write_bytes("- [x] a\0z ⟂ refactor pending\n".encode())
    code = clear_refactor_pending.main([str(nul), "a"])
    assert (code, *capsysbinary.readouterr(), nul.read_bytes()) == (0, b"", b"", b"- [x] az\n")

    raw = tmp_path / "raw.md"
    raw.write_bytes(b"- [x] a\xff" + " ⟂ refactor pending\n".encode())
    code = clear_refactor_pending.main([str(raw), os.fsdecode(b"a\xff")])
    assert (code, *capsysbinary.readouterr(), raw.read_bytes()) == (0, b"", b"", b"- [x] a\xff\n")


def test_main_matches_a_step_line_by_the_c_locale_grammar_clearing_a_capital_box_a_tab_and_ascii_space_before_the_dash_but_not_034_or_nbsp(
        tmp_path, capsysbinary, clear_refactor_pending):
    seeds = {
        "capital": "- [X] a ⟂ refactor pending\n".encode(),
        "tab": "-\t[x] a ⟂ refactor pending\n".encode(),
        "spaces": "  - [x] a ⟂ refactor pending\n".encode(),
        "formfeed": "\f- [x] a ⟂ refactor pending\n".encode(),
        "fs": "\034- [x] a ⟂ refactor pending\n".encode(),
        "nbsp": " - [x] a ⟂ refactor pending\n".encode(),
    }
    results = {}
    for name, seed in seeds.items():
        led = tmp_path / f"{name}.md"
        led.write_bytes(seed)
        code = clear_refactor_pending.main([str(led), "a"])
        results[name] = (code, *capsysbinary.readouterr(), led.read_bytes())

    assert results == {
        "capital": (0, b"", b"", b"- [X] a\n"),
        "tab": (0, b"", b"", b"-\t[x] a\n"),
        "spaces": (0, b"", b"", b"  - [x] a\n"),
        "formfeed": (0, b"", b"", b"\f- [x] a\n"),
        "fs": (3, b"", b"", seeds["fs"]),
        "nbsp": (3, b"", b"", seeds["nbsp"]),
    }


def test_main_writes_the_ledger_in_place_keeping_a_symlink_a_symlink_and_reading_a_relative_ledger_file_from_the_working_directory(
        tmp_path, monkeypatch, capsysbinary, clear_refactor_pending):
    seed = "- [x] a ⟂ refactor pending\n".encode()
    target = tmp_path / "target.md"
    target.write_bytes(seed)
    link = tmp_path / "link.md"
    link.symlink_to(target)
    cwd = tmp_path / "cwd"
    cwd.mkdir()
    (cwd / "relative.md").write_bytes(seed)
    (tmp_path / "relative.md").write_bytes(seed)
    monkeypatch.chdir(cwd)
    results = {}
    for argv in ([str(link), "a"], ["relative.md", "a"]):
        code = clear_refactor_pending.main(argv)
        results[argv[0]] = (code, *capsysbinary.readouterr())

    assert results == {str(link): (0, b"", b""), "relative.md": (0, b"", b"")}
    assert (link.is_symlink(), target.read_bytes()) == (True, b"- [x] a\n")
    assert (cwd / "relative.md").read_bytes() == b"- [x] a\n"
    assert (tmp_path / "relative.md").read_bytes() == seed


def test_main_returns_2_without_raising_leaving_the_ledger_byte_identical_and_nothing_beside_it_when_opening_the_ledger_for_writing_fails_1110(
        tmp_path, monkeypatch, capsysbinary, clear_refactor_pending):
    seed = "- [x] a ⟂ refactor pending\n".encode()
    refused = tmp_path / "refused.md"
    refused.write_bytes(seed)
    real_open = builtins.open

    def refusing_open(file, mode="r", *args, **kwargs):
        if os.fspath(file) == str(refused) and "w" in mode:
            raise PermissionError(13, "Permission denied", str(refused))
        return real_open(file, mode, *args, **kwargs)

    monkeypatch.setattr(builtins, "open", refusing_open)
    assert clear_refactor_pending.main([str(refused), "a"]) == 2
    assert b"Traceback" not in capsysbinary.readouterr().err
    assert refused.read_bytes() == seed
    assert sorted(p.name for p in tmp_path.iterdir()) == ["refused.md"]


def test_main_leaves_the_ledger_byte_identical_and_returns_2_when_writing_the_cleared_ledger_fails_817(
        tmp_path, monkeypatch, capsysbinary, clear_refactor_pending):
    seed = "".join(f"- [x] step {n} ⟂ refactor pending\n" for n in range(8)).encode()
    led = tmp_path / "ledger.md"
    led.write_bytes(seed)
    real_open = builtins.open

    class FullDisk:
        def __init__(self, file):
            self.file = file

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            self.file.close()

        def write(self, data):
            self.file.write(data[:len(data) // 2])
            self.file.flush()
            raise OSError(28, "No space left on device", str(led))

    def full_disk_open(file, mode="r", *args, **kwargs):
        opened = real_open(file, mode, *args, **kwargs)
        return FullDisk(opened) if os.fspath(file) == str(led) and "w" in mode else opened

    monkeypatch.setattr(builtins, "open", full_disk_open)
    try:
        code = clear_refactor_pending.main([str(led), "step 3"])
    except OSError as error:
        code = type(error).__name__
    monkeypatch.undo()
    capsysbinary.readouterr()

    assert (code, led.read_bytes()) == (2, seed)


def test_main_leaves_the_ledger_byte_identical_and_returns_2_when_every_write_to_the_ledger_fails_817(
        tmp_path, capsysbinary, clear_refactor_pending):
    seed = "".join(f"- [x] step {n} of a ledger long enough to outgrow the file size limit ⟂ refactor pending\n"
                   for n in range(8)).encode()
    led = tmp_path / "ledger.md"
    led.write_bytes(seed)
    soft, hard = resource.getrlimit(resource.RLIMIT_FSIZE)
    resource.setrlimit(resource.RLIMIT_FSIZE, (64, hard))
    try:
        code = clear_refactor_pending.main([str(led), "step 3"])
    except OSError as error:
        code = type(error).__name__
    finally:
        resource.setrlimit(resource.RLIMIT_FSIZE, (soft, hard))
    capsysbinary.readouterr()

    assert (code, led.read_bytes()) == (2, seed)


def test_main_leaves_the_ledger_byte_identical_and_returns_2_when_the_temporary_file_beside_it_cannot_be_created_817(
        tmp_path, monkeypatch, capsysbinary, clear_refactor_pending):
    seed = "- [x] alpha ⟂ refactor pending\n- [x] beta ⟂ refactor pending\n".encode()
    led = tmp_path / "ledger.md"
    led.write_bytes(seed)
    real_open = os.open

    def refusing_open(path, *args, **kwargs):
        if os.path.dirname(os.path.abspath(path)) == str(tmp_path) and os.path.abspath(path) != str(led):
            raise OSError(errno.ENOSPC, os.strerror(errno.ENOSPC), path)
        return real_open(path, *args, **kwargs)

    monkeypatch.setattr(os, "open", refusing_open)
    try:
        code = clear_refactor_pending.main([str(led), "beta"])
    except OSError as error:
        code = type(error).__name__
    monkeypatch.undo()
    capsysbinary.readouterr()

    assert (code, led.read_bytes()) == (2, seed)


def test_main_leaves_the_ledger_byte_identical_and_returns_2_when_writing_the_cleared_ledger_and_writing_its_old_contents_back_both_fail_817(
        tmp_path, monkeypatch, capsysbinary, clear_refactor_pending):
    seed = "".join(f"- [x] step {n} ⟂ refactor pending\n" for n in range(8)).encode()
    led = tmp_path / "ledger.md"
    led.write_bytes(seed)
    real_open = builtins.open
    real_os_open = os.open

    class FullDisk:
        def __init__(self, file):
            self.file = file

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            self.file.close()

        def write(self, data):
            self.file.write(data[:len(data) // 2])
            self.file.flush()
            raise OSError(errno.ENOSPC, os.strerror(errno.ENOSPC), str(led))

    def full_disk_open(file, mode="r", *args, **kwargs):
        opened = real_open(file, mode, *args, **kwargs)
        return FullDisk(opened) if os.fspath(file) == str(led) and "w" in mode else opened

    def refusing_os_open(path, *args, **kwargs):
        if os.path.abspath(path) == str(led):
            raise OSError(errno.EIO, os.strerror(errno.EIO), path)
        return real_os_open(path, *args, **kwargs)

    monkeypatch.setattr(builtins, "open", full_disk_open)
    monkeypatch.setattr(os, "open", refusing_os_open)
    try:
        code = clear_refactor_pending.main([str(led), "step 3"])
    except OSError as error:
        code = type(error).__name__
    monkeypatch.undo()
    capsysbinary.readouterr()

    assert (code, led.read_bytes()) == (2, seed)


def test_main_leaves_the_ledger_byte_identical_and_returns_2_when_the_in_place_write_the_write_back_and_the_fallback_temporary_file_all_fail_817(
        tmp_path, monkeypatch, capsysbinary, clear_refactor_pending):
    seed = "".join(f"- [x] step {n} ⟂ refactor pending\n" for n in range(8)).encode()
    led = tmp_path / "ledger.md"
    led.write_bytes(seed)
    real_open = builtins.open
    real_os_open = os.open
    real_mkstemp = tempfile.mkstemp
    made = []

    class FullDisk:
        def __init__(self, file):
            self.file = file

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            self.file.close()

        def write(self, data):
            self.file.write(data[:len(data) // 2])
            self.file.flush()
            raise OSError(errno.ENOSPC, os.strerror(errno.ENOSPC), str(led))

    def full_disk_open(file, mode="r", *args, **kwargs):
        opened = real_open(file, mode, *args, **kwargs)
        return FullDisk(opened) if os.fspath(file) == str(led) and "w" in mode else opened

    def refusing_os_open(path, *args, **kwargs):
        if os.path.abspath(path) == str(led):
            raise OSError(errno.EIO, os.strerror(errno.EIO), path)
        return real_os_open(path, *args, **kwargs)

    def mkstemp_once(*args, **kwargs):
        if made:
            raise OSError(errno.ENOSPC, os.strerror(errno.ENOSPC), str(tmp_path))
        made.append(True)
        return real_mkstemp(*args, **kwargs)

    monkeypatch.setattr(builtins, "open", full_disk_open)
    monkeypatch.setattr(os, "open", refusing_os_open)
    monkeypatch.setattr(tempfile, "mkstemp", mkstemp_once)
    try:
        code = clear_refactor_pending.main([str(led), "step 3"])
    except OSError as error:
        code = type(error).__name__
    monkeypatch.undo()
    capsysbinary.readouterr()

    assert (code, led.read_bytes()) == (2, seed)


def test_main_returns_2_without_raising_leaving_the_ledger_byte_identical_and_nothing_beside_it_when_every_write_and_the_restore_of_its_backup_fail_1110(
        tmp_path, monkeypatch, capsysbinary, clear_refactor_pending):
    seed = "".join(f"- [x] step {n} ⟂ refactor pending\n" for n in range(8)).encode()
    led = tmp_path / "ledger.md"
    led.write_bytes(seed)
    real_open = builtins.open
    real_os_open = os.open
    real_replace = os.replace

    class FullDisk:
        def __init__(self, file):
            self.file = file

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            self.file.close()

        def write(self, data):
            raise OSError(errno.ENOSPC, os.strerror(errno.ENOSPC), str(led))

    def full_disk_open(file, mode="r", *args, **kwargs):
        if os.fspath(file) == str(led) and "w" in mode:
            return FullDisk(real_open(file, "rb"))
        return real_open(file, mode, *args, **kwargs)

    def refusing_os_open(path, *args, **kwargs):
        if os.path.abspath(path) == str(led):
            raise OSError(errno.EIO, os.strerror(errno.EIO), path)
        return real_os_open(path, *args, **kwargs)

    def refusing_replace(src, dst, *args, **kwargs):
        if os.path.abspath(dst) == str(led):
            raise OSError(errno.EIO, os.strerror(errno.EIO), dst)
        return real_replace(src, dst, *args, **kwargs)

    monkeypatch.setattr(builtins, "open", full_disk_open)
    monkeypatch.setattr(os, "open", refusing_os_open)
    monkeypatch.setattr(os, "replace", refusing_replace)
    try:
        code = clear_refactor_pending.main([str(led), "step 3"])
    except OSError as error:
        code = type(error).__name__
    monkeypatch.undo()
    err = capsysbinary.readouterr().err

    assert (code, b"Traceback" in err, led.read_bytes(), sorted(p.name for p in tmp_path.iterdir())) == (
        2, False, seed, ["ledger.md"])


def test_main_returns_2_without_raising_and_nothing_beside_the_ledger_when_removing_its_backup_fails_after_a_failed_open_or_a_failed_restore_1110(
        tmp_path, monkeypatch, capsysbinary, clear_refactor_pending):
    seed = "".join(f"- [x] step {n} ⟂ refactor pending\n" for n in range(8)).encode()
    real_open = builtins.open
    real_os_open = os.open
    real_replace = os.replace
    real_unlink = os.unlink

    class FullDisk:
        def __init__(self, file):
            self.file = file

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            self.file.close()

        def write(self, data):
            raise OSError(errno.ENOSPC, os.strerror(errno.ENOSPC), "ledger.md")

    def refusing_open(led):
        def fake(file, mode="r", *args, **kwargs):
            if os.fspath(file) == str(led) and "w" in mode:
                raise OSError(errno.EIO, os.strerror(errno.EIO), str(led))
            return real_open(file, mode, *args, **kwargs)
        return fake

    def full_disk_open(led):
        def fake(file, mode="r", *args, **kwargs):
            if os.fspath(file) == str(led) and "w" in mode:
                return FullDisk(real_open(file, "rb"))
            return real_open(file, mode, *args, **kwargs)
        return fake

    def refusing_os_open(led):
        def fake(path, *args, **kwargs):
            if os.path.abspath(path) == str(led):
                raise OSError(errno.EIO, os.strerror(errno.EIO), path)
            return real_os_open(path, *args, **kwargs)
        return fake

    def refusing_replace(led):
        def fake(src, dst, *args, **kwargs):
            if os.path.abspath(dst) == str(led):
                raise OSError(errno.EIO, os.strerror(errno.EIO), dst)
            return real_replace(src, dst, *args, **kwargs)
        return fake

    def failing_unlink(led):
        def fake(path, *args, **kwargs):
            real_unlink(path, *args, **kwargs)
            if os.path.dirname(os.path.abspath(path)) == str(led.parent):
                raise OSError(errno.EIO, os.strerror(errno.EIO), path)
        return fake

    scenarios = {
        "open": lambda led: [(builtins, "open", refusing_open(led))],
        "restore": lambda led: [(builtins, "open", full_disk_open(led)), (os, "open", refusing_os_open(led)),
                                (os, "replace", refusing_replace(led))],
    }
    results = {}
    for name, fakes in scenarios.items():
        (tmp_path / name).mkdir()
        led = tmp_path / name / "ledger.md"
        led.write_bytes(seed)
        for target, attr, fake in fakes(led) + [(os, "unlink", failing_unlink(led))]:
            monkeypatch.setattr(target, attr, fake)
        try:
            code = clear_refactor_pending.main([str(led), "step 3"])
        except OSError as error:
            code = type(error).__name__
        monkeypatch.undo()
        err = capsysbinary.readouterr().err
        results[name] = (code, b"Traceback" in err, led.read_bytes(), sorted(p.name for p in led.parent.iterdir()))

    assert results == {name: (2, False, seed, ["ledger.md"]) for name in scenarios}


def test_main_returns_2_without_raising_and_nothing_beside_the_ledger_when_removing_its_backup_fails_after_a_clear_or_a_write_back_1110(
        tmp_path, monkeypatch, capsysbinary, clear_refactor_pending):
    seed = "".join(f"- [x] step {n} ⟂ refactor pending\n" for n in range(8)).encode()
    real_open = builtins.open
    real_unlink = os.unlink

    class FullDisk:
        def __init__(self, file):
            self.file = file

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            self.file.close()

        def write(self, data):
            raise OSError(errno.ENOSPC, os.strerror(errno.ENOSPC), "ledger.md")

    def full_disk_open(led):
        def fake(file, mode="r", *args, **kwargs):
            if os.fspath(file) == str(led) and "w" in mode:
                return FullDisk(real_open(file, "rb"))
            return real_open(file, mode, *args, **kwargs)
        return fake

    def failing_unlink(led):
        def fake(path, *args, **kwargs):
            real_unlink(path, *args, **kwargs)
            if os.path.dirname(os.path.abspath(path)) == str(led.parent):
                raise OSError(errno.EIO, os.strerror(errno.EIO), path)
        return fake

    scenarios = {
        "cleared": lambda led: [],
        "written-back": lambda led: [(builtins, "open", full_disk_open(led))],
    }
    results = {}
    for name, fakes in scenarios.items():
        (tmp_path / name).mkdir()
        led = tmp_path / name / "ledger.md"
        led.write_bytes(seed)
        for target, attr, fake in fakes(led) + [(os, "unlink", failing_unlink(led))]:
            monkeypatch.setattr(target, attr, fake)
        try:
            code = clear_refactor_pending.main([str(led), "step 3"])
        except OSError as error:
            code = type(error).__name__
        monkeypatch.undo()
        err = capsysbinary.readouterr().err
        results[name] = (code, b"Traceback" in err, sorted(p.name for p in led.parent.iterdir()))

    assert results == {name: (2, False, ["ledger.md"]) for name in scenarios}


def test_main_returns_2_without_raising_keeping_the_backup_with_the_old_bytes_and_naming_it_in_one_stderr_line_when_a_truncating_write_the_write_back_and_the_restore_all_fail_1125(
        tmp_path, monkeypatch, capsysbinary, clear_refactor_pending):
    seed = "".join(f"- [x] step {n} ⟂ refactor pending\n" for n in range(8)).encode()
    led = tmp_path / "ledger.md"
    led.write_bytes(seed)
    real_open = builtins.open
    real_os_open = os.open
    real_replace = os.replace

    class FullDisk:
        def __init__(self, file):
            self.file = file

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            self.file.close()

        def write(self, data):
            raise OSError(errno.ENOSPC, os.strerror(errno.ENOSPC), str(led))

    def truncating_full_disk_open(file, mode="r", *args, **kwargs):
        if os.fspath(file) == str(led) and "w" in mode:
            return FullDisk(real_open(file, "wb"))
        return real_open(file, mode, *args, **kwargs)

    def refusing_os_open(path, *args, **kwargs):
        if os.path.abspath(path) == str(led):
            raise OSError(errno.EIO, os.strerror(errno.EIO), path)
        return real_os_open(path, *args, **kwargs)

    def refusing_replace(src, dst, *args, **kwargs):
        if os.path.abspath(dst) == str(led):
            raise OSError(errno.EIO, os.strerror(errno.EIO), dst)
        return real_replace(src, dst, *args, **kwargs)

    monkeypatch.setattr(builtins, "open", truncating_full_disk_open)
    monkeypatch.setattr(os, "open", refusing_os_open)
    monkeypatch.setattr(os, "replace", refusing_replace)
    try:
        code = clear_refactor_pending.main([str(led), "step 3"])
    except OSError as error:
        code = type(error).__name__
    monkeypatch.undo()
    err = capsysbinary.readouterr().err
    beside = [p for p in tmp_path.iterdir() if p.name != "ledger.md"]

    assert (code, b"Traceback" in err, [p.read_bytes() for p in beside]) == (2, False, [seed])
    lines = err.decode().splitlines()
    assert (len(lines), lines[0].startswith("clear-refactor-pending.sh: "), str(beside[0]) in lines[0]) == (
        1, True, True)


def test_main_returns_2_without_raising_writing_back_exactly_the_old_bytes_and_nothing_beside_the_ledger_when_a_failed_write_leaves_it_longer_than_before_1125(
        tmp_path, monkeypatch, capsysbinary, clear_refactor_pending):
    seed = "".join(f"- [x] step {n} ⟂ refactor pending\n" for n in range(8)).encode()
    led = tmp_path / "ledger.md"
    led.write_bytes(seed)
    real_open = builtins.open

    class FullDisk:
        def __init__(self, file):
            self.file = file

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            self.file.close()

        def write(self, data):
            self.file.write(data + data)
            self.file.flush()
            raise OSError(errno.ENOSPC, os.strerror(errno.ENOSPC), str(led))

    def overlong_full_disk_open(file, mode="r", *args, **kwargs):
        opened = real_open(file, mode, *args, **kwargs)
        return FullDisk(opened) if os.fspath(file) == str(led) and "w" in mode else opened

    monkeypatch.setattr(builtins, "open", overlong_full_disk_open)
    try:
        code = clear_refactor_pending.main([str(led), "step 3"])
    except OSError as error:
        code = type(error).__name__
    monkeypatch.undo()
    err = capsysbinary.readouterr().err
    beside = [p.name for p in tmp_path.iterdir() if p.name != "ledger.md"]

    assert (code, b"Traceback" in err, beside, led.read_bytes()) == (2, False, [], seed)


def test_main_returns_2_without_raising_restoring_the_old_bytes_and_nothing_beside_the_ledger_when_a_truncating_write_and_the_write_back_fail_but_the_restore_succeeds_1125(
        tmp_path, monkeypatch, capsysbinary, clear_refactor_pending):
    seed = "".join(f"- [x] step {n} ⟂ refactor pending\n" for n in range(8)).encode()
    led = tmp_path / "ledger.md"
    led.write_bytes(seed)
    real_open = builtins.open
    real_os_open = os.open

    class FullDisk:
        def __init__(self, file):
            self.file = file

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            self.file.close()

        def write(self, data):
            raise OSError(errno.ENOSPC, os.strerror(errno.ENOSPC), str(led))

    def truncating_full_disk_open(file, mode="r", *args, **kwargs):
        if os.fspath(file) == str(led) and "w" in mode:
            return FullDisk(real_open(file, "wb"))
        return real_open(file, mode, *args, **kwargs)

    def refusing_os_open(path, *args, **kwargs):
        if os.path.abspath(path) == str(led):
            raise OSError(errno.EIO, os.strerror(errno.EIO), path)
        return real_os_open(path, *args, **kwargs)

    monkeypatch.setattr(builtins, "open", truncating_full_disk_open)
    monkeypatch.setattr(os, "open", refusing_os_open)
    try:
        code = clear_refactor_pending.main([str(led), "step 3"])
    except OSError as error:
        code = type(error).__name__
    monkeypatch.undo()
    err = capsysbinary.readouterr().err
    beside = [p.name for p in tmp_path.iterdir() if p.name != "ledger.md"]

    assert (code, b"Traceback" in err, led.read_bytes(), beside) == (2, False, seed, [])


def test_main_returns_2_without_raising_and_names_the_leftover_backup_in_one_stderr_line_when_removing_it_raises_without_deleting_it_1125(
        tmp_path, monkeypatch, capsysbinary, clear_refactor_pending):
    seed = "".join(f"- [x] step {n} ⟂ refactor pending\n" for n in range(8)).encode()
    led = tmp_path / "ledger.md"
    led.write_bytes(seed)

    def refusing_unlink(path, *args, **kwargs):
        raise OSError(errno.EIO, os.strerror(errno.EIO), path)

    monkeypatch.setattr(os, "unlink", refusing_unlink)
    try:
        code = clear_refactor_pending.main([str(led), "step 3"])
    except OSError as error:
        code = type(error).__name__
    monkeypatch.undo()
    err = capsysbinary.readouterr().err
    beside = [p for p in tmp_path.iterdir() if p.name != "ledger.md"]

    assert (code, b"Traceback" in err, len(beside)) == (2, False, 1)
    lines = err.decode().splitlines()
    assert (len(lines), all(line.startswith("clear-refactor-pending.sh: ") and str(beside[0]) in line
                            for line in lines)) == (1, True)


def test_main_returns_2_on_a_missing_ledger_with_one_stderr_line_naming_it(
        tmp_path, capsysbinary, clear_refactor_pending):
    code = clear_refactor_pending.main([str(tmp_path / "missing.md"), "a"])
    out, err = capsysbinary.readouterr()
    assert (code, out) == (2, b"")
    assert err.decode() == f"clear-refactor-pending.sh: {tmp_path / 'missing.md'}: No such file or directory\n"


def test_main_returns_2_on_a_directory_as_the_ledger_with_one_stderr_line_naming_it(
        tmp_path, capsysbinary, clear_refactor_pending):
    code = clear_refactor_pending.main([str(tmp_path), "a"])
    out, err = capsysbinary.readouterr()
    assert (code, out) == (2, b"")
    assert err.decode() == f"clear-refactor-pending.sh: {tmp_path}: Is a directory\n"
