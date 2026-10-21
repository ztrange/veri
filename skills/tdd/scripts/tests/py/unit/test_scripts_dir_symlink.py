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
