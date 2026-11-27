"""In-process cases for the `pin` phase's test ids: verify.py's `pin` phase, through build_verify_prompt.py, takes 1 to
5 test ids after the spec file (PRD 044.2, D8, SC650)."""
import importlib

from test_verify import BRANCH, answering_leaf, write_inputs

STEP = "the zorblat is frobbed ⟦criterion 7⟧"


def test_pin_phase_builds_the_pin_prompt_for_5_tracked_ids_carrying_every_id_space_separated(
        tmp_path, monkeypatch, capfdbinary, fake_processes):
    monkeypatch.chdir(tmp_path)
    write_inputs(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path))
    ids = []
    for k in range(1, 6):
        (tmp_path / "tests" / f"test_{k}.py").write_text("def test_case(): pass\n")
        ids.append(f"tests/test_{k}.py::test_case")
    launches = answering_leaf(monkeypatch, fake_processes, b"VERDICT: PASS\ncovered")
    verify = importlib.import_module("veri.verify")

    code = verify.main([*BRANCH, "--step", STEP, "pin", "spec.md", *ids])

    prompts = [prompt for leaf, prompt in launches if leaf == "verify-pin"]
    assert (code, len(prompts)) == (0, 1), capfdbinary.readouterr().err
    assert " ".join(ids) in prompts[0]


def test_pin_phase_refuses_6_tracked_test_ids_with_2_launching_no_verifier(
        tmp_path, monkeypatch, capfdbinary, fake_processes):
    monkeypatch.chdir(tmp_path)
    write_inputs(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path))
    ids = []
    for k in range(1, 7):
        (tmp_path / "tests" / f"test_{k}.py").write_text("def test_case(): pass\n")
        ids.append(f"tests/test_{k}.py::test_case")
    launches = answering_leaf(monkeypatch, fake_processes, b"VERDICT: PASS\ncovered")
    verify = importlib.import_module("veri.verify")

    code = verify.main([*BRANCH, "--step", STEP, "pin", "spec.md", *ids])

    prompts = [prompt for leaf, prompt in launches if leaf == "verify-pin"]
    assert (code, len(prompts)) == (2, 0)
    assert "at most 5" in capfdbinary.readouterr().err.decode()


def test_pin_phase_refuses_an_untracked_test_id_with_2(tmp_path, monkeypatch, capfdbinary, fake_processes):
    monkeypatch.chdir(tmp_path)
    write_inputs(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path))
    (tmp_path / "tests" / "test_1.py").write_text("def test_case(): pass\n")
    ids = ["tests/test_1.py::test_case", "tests/test_ghost.py::test_case"]
    launches = answering_leaf(monkeypatch, fake_processes, b"VERDICT: PASS\ncovered")
    verify = importlib.import_module("veri.verify")

    code = verify.main([*BRANCH, "--step", STEP, "pin", "spec.md", *ids])

    prompts = [prompt for leaf, prompt in launches if leaf == "verify-pin"]
    assert (code, len(prompts)) == (2, 0)
    assert "tests/test_ghost.py is not tracked" in capfdbinary.readouterr().err.decode()


def test_pin_phase_refuses_a_free_text_argument_with_2_launching_no_verifier(
        tmp_path, monkeypatch, capfdbinary, fake_processes):
    monkeypatch.chdir(tmp_path)
    write_inputs(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path))
    (tmp_path / "tests" / "test_1.py").write_text("def test_case(): pass\n")
    ids = ["tests/test_1.py::test_case", "the existing case already covers it"]
    launches = answering_leaf(monkeypatch, fake_processes, b"VERDICT: PASS\ncovered")
    verify = importlib.import_module("veri.verify")

    code = verify.main([*BRANCH, "--step", STEP, "pin", "spec.md", *ids])

    prompts = [prompt for leaf, prompt in launches if leaf == "verify-pin"]
    assert (code, len(prompts)) == (2, 0)
    assert "'the existing case already covers it' is not a test id" in capfdbinary.readouterr().err.decode()


def _git_ls_files(tracked, untracked):
    """`git ls-files -z` as git answers it: the <tracked> paths, plus the <untracked> ones only when asked `--others`."""
    def answer(line, **_):
        listed = list(tracked) + (list(untracked) if "--others" in line.split() else [])
        return 0, "".join(path + "\0" for path in listed), ""
    return answer


def test_4779_a_pin_test_id_in_a_new_file_red_never_staged_is_judged_not_refused(tmp_path, monkeypatch, fake_processes):
    """PRD 044.2: Red writes a PASSES test in a new file and never stages it, and verify-pin runs before the step's
    `test: pin` commit, so an id whose file is untracked but present in the worktree is a test id, not a refusal."""
    monkeypatch.chdir(tmp_path)
    fake_processes.answers({"git ls-files": _git_ls_files(["spec.md", "tests/test_1.py"], ["tests/test_new.py"])})
    build_verify_prompt = importlib.import_module("veri.build_verify_prompt")

    refusal = build_verify_prompt.pin_ids_refusal(("tests/test_1.py::test_case", "tests/test_new.py::test_case"))

    assert refusal == ""


def test_4779_a_pin_test_id_whose_file_is_neither_tracked_nor_in_the_worktree_is_still_refused(tmp_path, monkeypatch, fake_processes):
    monkeypatch.chdir(tmp_path)
    fake_processes.answers({"git ls-files": _git_ls_files(["spec.md", "tests/test_1.py"], ["tests/test_new.py"])})
    build_verify_prompt = importlib.import_module("veri.build_verify_prompt")

    refusal = build_verify_prompt.pin_ids_refusal(("tests/test_new.py::test_case", "tests/test_ghost.py::test_case"))

    assert "tests/test_ghost.py is not" in refusal


def test_4779_a_failing_git_ls_files_refuses_the_pin_ids_naming_the_listing(tmp_path, monkeypatch, fake_processes):
    """A pin whose tracked files cannot be listed cannot check its ids: refused, never judged over an empty listing."""
    monkeypatch.chdir(tmp_path)
    fake_processes.answers({"git ls-files": (128, "", "fatal: not a git repository\n")})
    build_verify_prompt = importlib.import_module("veri.build_verify_prompt")

    refusal = build_verify_prompt.pin_ids_refusal(("tests/test_1.py::test_case",))

    assert refusal.startswith("build-verify-prompt: pin cannot list the tracked files: ")
