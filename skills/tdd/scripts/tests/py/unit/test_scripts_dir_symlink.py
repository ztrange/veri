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


def test_five_more_modules_keep_the_symlinked_scripts_directory_they_were_reached_through(tmp_path):
    link = tmp_path / "skill-link"
    os.symlink(SKILL, link)
    held = {}
    for module, name in (("dashboard", "SCRIPTS"), ("orchestrate", "SCRIPTS"),
                         ("parallel_conductors", "SCRIPTS"), ("push_branch", "SCRIPTS"),
                         ("run_leaf", "GUARD")):
        path = link / "scripts" / "veri" / f"{module}.py"
        spec = importlib.util.spec_from_file_location(f"symlinked_{module}", path)
        loaded = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(loaded)
        held[module] = getattr(loaded, name)
    scripts = os.path.join(link, "scripts")
    assert held == {"dashboard": scripts, "orchestrate": scripts,
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
