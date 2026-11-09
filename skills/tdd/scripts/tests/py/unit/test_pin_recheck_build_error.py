from types import SimpleNamespace

from veri import pin_recheck


def record(**fields):
    return "".join("%s %d\n%s\n" % (k, len(v), v) for k, v in fields.items()) + "\n"


def test_3333_a_mutated_run_with_no_failure_marker_and_no_shared_line_is_still_did_not_build(
        tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "issue-1-mutations.md").write_text(record(
        file="guard.txt", old="if guard", new="if not guard",
        command="python3 -m pytest -q t.py::case"))
    target = tmp_path / "guard.txt"
    target.write_text("if guard\n")

    def fake_run(command):
        if "if not guard" in target.read_text():
            return SimpleNamespace(returncode=2, stdout="", stderr="SyntaxError: invalid syntax\n")
        return SimpleNamespace(returncode=0, stdout="1 passed in 0.19s\n", stderr="")

    monkeypatch.setattr(pin_recheck, "run_captured", fake_run)
    monkeypatch.setattr(pin_recheck, "git_out", lambda *a: "guard.txt\n" if "--diff-filter=D" not in a else "")
    looks = {}

    status = pin_recheck.recheck(["base"], looks)

    assert (status, looks) == (1, {("guard.txt", "mutation did not build"): 1})


def test_3333_a_single_case_pytest_run_that_fails_is_red_not_did_not_build(
        tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "issue-1-mutations.md").write_text(record(
        file="guard.txt", old="if guard", new="if not guard",
        command="python3 -m pytest -q t.py::case"))
    target = tmp_path / "guard.txt"
    target.write_text("if guard\n")

    def fake_run(command):
        if "if not guard" in target.read_text():
            return SimpleNamespace(
                returncode=1,
                stdout="FAILED t.py::case - AssertionError: assert 1 == 2\n1 failed in 0.21s\n",
                stderr="")
        return SimpleNamespace(returncode=0, stdout="1 passed in 0.19s\n", stderr="")

    monkeypatch.setattr(pin_recheck, "run_captured", fake_run)
    monkeypatch.setattr(pin_recheck, "git_out", lambda *a: "guard.txt\n" if "--diff-filter=D" not in a else "")
    looks = {}

    status = pin_recheck.recheck(["base"], looks)

    assert (status, looks) == (0, {})


def test_3333_a_build_error_with_failed_mid_line_is_still_did_not_build(
        tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "issue-1-mutations.md").write_text(record(
        file="guard.txt", old="if guard", new="if not guard",
        command="python3 -m pytest -q t.py::case"))
    target = tmp_path / "guard.txt"
    target.write_text("if guard\n")

    def fake_run(command):
        if "if not guard" in target.read_text():
            return SimpleNamespace(returncode=2, stdout="", stderr="error: compile FAILED in guard.txt\n")
        return SimpleNamespace(returncode=0, stdout="1 passed in 0.19s\n", stderr="")

    monkeypatch.setattr(pin_recheck, "run_captured", fake_run)
    monkeypatch.setattr(pin_recheck, "git_out", lambda *a: "guard.txt\n" if "--diff-filter=D" not in a else "")
    looks = {}

    status = pin_recheck.recheck(["base"], looks)

    assert (status, looks) == (1, {("guard.txt", "mutation did not build"): 1})


def test_3331_a_pin_whose_old_text_occurs_twice_in_its_file_needs_a_look_and_is_not_mutated(
        tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "issue-1-mutations.md").write_text(record(
        file="guard.txt", old="break", new="continue",
        command="python3 -m pytest -q t.py::case"))
    target = tmp_path / "guard.txt"
    target.write_text("for a in x:\n    break\nfor b in y:\n    break\n")
    seen = []

    def fake_run(command):
        seen.append(target.read_text())
        return SimpleNamespace(returncode=0, stdout="1 passed in 0.19s\n", stderr="")

    monkeypatch.setattr(pin_recheck, "run_captured", fake_run)
    monkeypatch.setattr(pin_recheck, "git_out", lambda *a: "guard.txt\n" if "--diff-filter=D" not in a else "")
    looks = {}

    pin_recheck.recheck(["base"], looks)

    assert (any("continue" in s for s in seen), sorted({f for f, _ in looks}),
            target.read_text()) == (False, ["guard.txt"], "for a in x:\n    break\nfor b in y:\n    break\n")


def test_3331_a_pin_whose_old_text_occurs_once_on_its_recorded_line_still_mutates_and_replays(
        tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "issue-1-mutations.md").write_text(record(
        file="guard.txt", old="break", new="continue", context="    break",
        command="python3 -m pytest -q t.py::case"))
    target = tmp_path / "guard.txt"
    target.write_text("for a in x:\n    break\n")
    seen = []

    def fake_run(command):
        seen.append(target.read_text())
        if "continue" in seen[-1]:
            return SimpleNamespace(
                returncode=1, stdout="FAILED t.py::case - AssertionError\n1 failed in 0.2s\n", stderr="")
        return SimpleNamespace(returncode=0, stdout="1 passed in 0.19s\n", stderr="")

    monkeypatch.setattr(pin_recheck, "run_captured", fake_run)
    monkeypatch.setattr(pin_recheck, "git_out", lambda *a: "guard.txt\n" if "--diff-filter=D" not in a else "")
    looks = {}

    status = pin_recheck.recheck(["base"], looks)

    assert (status, looks, any("continue" in s for s in seen)) == (0, {}, True)


def test_3331_a_pin_whose_old_text_occurs_once_off_its_recorded_line_needs_a_look_and_is_not_mutated(
        tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "issue-1-mutations.md").write_text(record(
        file="guard.txt", old="break", new="continue", context="    if done: break",
        command="python3 -m pytest -q t.py::case"))
    target = tmp_path / "guard.txt"
    target.write_text("for a in x:\n    stop(a)\nfor b in y:\n    break\n")
    seen = []

    def fake_run(command):
        seen.append(target.read_text())
        return SimpleNamespace(returncode=0, stdout="1 passed in 0.19s\n", stderr="")

    monkeypatch.setattr(pin_recheck, "run_captured", fake_run)
    monkeypatch.setattr(pin_recheck, "git_out", lambda *a: "guard.txt\n" if "--diff-filter=D" not in a else "")
    looks = {}

    pin_recheck.recheck(["base"], looks)

    assert (any("continue" in s for s in seen), sorted({f for f, _ in looks}),
            target.read_text()) == (False, ["guard.txt"], "for a in x:\n    stop(a)\nfor b in y:\n    break\n")


def test_3331_a_record_without_context_whose_old_text_occurs_twice_is_reported_as_occurring_more_than_once(
        tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "issue-1-mutations.md").write_text(record(
        file="guard.txt", old="break", new="continue",
        command="python3 -m pytest -q t.py::case"))
    target = tmp_path / "guard.txt"
    target.write_text("for a in x:\n    if a: break\nfor b in y:\n    break\n")
    seen = []

    def fake_run(command):
        seen.append(target.read_text())
        return SimpleNamespace(returncode=0, stdout="1 passed in 0.19s\n", stderr="")

    monkeypatch.setattr(pin_recheck, "run_captured", fake_run)
    monkeypatch.setattr(pin_recheck, "git_out", lambda *a: "guard.txt\n" if "--diff-filter=D" not in a else "")
    looks = {}

    pin_recheck.recheck(["base"], looks)

    assert (seen, looks) == ([], {("guard.txt", "old text occurs more than once"): 1})
