"""The scripts directory each module derives from __file__ stays the unresolved path."""
import importlib.util
import os
import pathlib

SKILL = pathlib.Path(__file__).resolve().parents[4]


def test_each_module_keeps_the_symlinked_scripts_directory_it_was_reached_through(tmp_path):
    link = tmp_path / "skill-link"
    os.symlink(SKILL, link)
    held = {}
    for module, name in (("supervise", "HERE"), ("build_develop_prompt", "HERE"),
                         ("build_verify_prompt", "HERE"), ("run_verdict", "SCRIPTS")):
        path = link / "scripts" / "veri" / f"{module}.py"
        spec = importlib.util.spec_from_file_location(f"symlinked_{module}", path)
        loaded = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(loaded)
        held[module] = getattr(loaded, name)
    scripts = os.path.join(link, "scripts")
    assert held == {"supervise": scripts, "build_develop_prompt": scripts,
                    "build_verify_prompt": scripts, "run_verdict": scripts}


def test_four_more_modules_keep_the_symlinked_scripts_directory_they_were_reached_through(tmp_path):
    link = tmp_path / "skill-link"
    os.symlink(SKILL, link)
    held = {}
    for module, name in (("orchestrate", "SCRIPTS"),
                         ("parallel_conductors", "SCRIPTS"), ("push_branch", "SCRIPTS"),
                         ("run_leaf", "GUARD")):
        path = link / "scripts" / "veri" / f"{module}.py"
        spec = importlib.util.spec_from_file_location(f"symlinked_{module}", path)
        loaded = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(loaded)
        held[module] = getattr(loaded, name)
    scripts = os.path.join(link, "scripts")
    assert held == {"orchestrate": scripts,
                    "parallel_conductors": scripts, "push_branch": scripts,
                    "run_leaf": os.path.join(scripts, "leaf-guard")}


def test_run_conductor_and_solvable_issues_keep_the_symlinked_scripts_directory_they_derive(tmp_path, monkeypatch):
    farm = tmp_path.resolve() / "farm" / "scripts"
    (farm / "veri").mkdir(parents=True)
    loaded = {}
    for module in ("run_conductor", "solvable_issues"):
        os.symlink(SKILL / "scripts" / "veri" / f"{module}.py", farm / "veri" / f"{module}.py")
        spec = importlib.util.spec_from_file_location(f"symlinked_{module}", farm / "veri" / f"{module}.py")
        loaded[module] = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(loaded[module])

    class Stop(Exception):
        pass

    based = []

    def spy_git(base, *args, **kwargs):
        based.append(base)
        raise Stop

    conductor = loaded["run_conductor"]
    monkeypatch.setattr(conductor.launch_floor, "bash_refusal", lambda name: None)
    monkeypatch.setattr(conductor.launch_floor, "python_refusal", lambda name: None)
    monkeypatch.setattr(conductor, "git", spy_git)
    try:
        conductor.main(["1"])
    except Stop:
        pass

    class Listing:
        stdout = f"1 {farm}/run-conductor.sh 7\n"

    issues = loaded["solvable_issues"]
    monkeypatch.setattr(issues.subprocess, "run", lambda *args, **kwargs: Listing())
    assert (based, issues.running_numbers()) == ([str(farm.parent)], {7})


def test_five_modules_resolve_the_symlinked_scripts_directory_to_its_target(tmp_path, monkeypatch):
    link = tmp_path / "skill-link"
    os.symlink(SKILL, link)
    real_scripts = str(SKILL / "scripts")
    monkeypatch.chdir(real_scripts)
    inside = {}
    for module in ("ensure_run_state_ignored", "issue_worktree", "leaf_timeout",
                   "preserve_attempt", "stop_run"):
        path = link / "scripts" / "veri" / f"{module}.py"
        spec = importlib.util.spec_from_file_location(f"symlinked_{module}", path)
        loaded = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(loaded)
        if module == "ensure_run_state_ignored":
            inside[module] = loaded.inside_own_scripts(real_scripts)
        else:
            inside[module] = loaded.inside_own_scripts()
    assert inside == {"ensure_run_state_ignored": True, "issue_worktree": True,
                      "leaf_timeout": True, "preserve_attempt": True, "stop_run": True}


def test_launch_floor_and_suite_reported_derive_their_paths_under_the_symlinked_scripts_directory(tmp_path):
    farm = tmp_path.resolve() / "farm"
    (farm / "scripts" / "veri").mkdir(parents=True)
    (farm / "scripts" / "lib").mkdir()
    (farm / "scripts" / "prompts").mkdir()
    (farm / "scripts" / "lib" / "venv-python.sh").write_text("VENV_FLOOR=9.9\n")
    (farm / "scripts" / "prompts" / "probe.md").write_text("REPORT-FORMAT probe | keys PROBE: | suite exempt: a probe\n")
    loaded = {}
    for module in ("launch_floor", "suite_reported"):
        os.symlink(SKILL / "scripts" / "veri" / f"{module}.py", farm / "scripts" / "veri" / f"{module}.py")
        spec = importlib.util.spec_from_file_location(f"symlinked_{module}", farm / "scripts" / "veri" / f"{module}.py")
        loaded[module] = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(loaded[module])
    assert (loaded["launch_floor"].python_floor(), loaded["suite_reported"]._exempt_keys("probe")) == (
        "9.9", [["PROBE:"]])
