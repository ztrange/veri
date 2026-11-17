"""PRD 026.5 (RM9): no tracked file outside specs/, docs/adr/, .tdd/ and skills/tdd/ names vcoord or a coordinator."""
import re
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[5]
WORDS = re.compile(r"vcoord|coordinator", re.I)
EXCLUDED = ("specs", "docs/adr", ".tdd", "skills/tdd")


def _install_removal_sentence(text):
    """The one closed exception: the sentence of README.md's `## Install` listing the links /vinstall removes."""
    section = re.search(r"^## Install\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    if not section:
        return None
    for found in re.finditer(r"[^.]*(?:\.(?!\s)[^.]*)*\.", section.group(1)):
        if "`removed <name>`" in found.group(0) and "is removed" in found.group(0):
            start = section.start(1) + found.start()
            return start, start + len(found.group(0))
    return None


def _readme_hits(text):
    span = _install_removal_sentence(text)
    hits = []
    for found in WORDS.finditer(text):
        excused = (found.group(0) == "vcoord" and span is not None and span[0] <= found.start() < span[1])
        if not excused:
            hits.append("README.md:%d" % (text.count("\n", 0, found.start()) + 1))
    return hits


def sweep(root):
    """Every file:line naming vcoord or a coordinator, but the one closed exception."""
    run = subprocess.run(
        ["git", "-C", str(root), "grep", "-n", "-I", "-i", "-E", "vcoord|coordinator", "--", ".", ":(exclude)README.md"]
        + [":(exclude)" + p for p in EXCLUDED],
        capture_output=True, text=True)
    assert run.returncode in (0, 1), run.stderr
    hits = [":".join(line.split(":", 2)[:2]) for line in run.stdout.splitlines()]
    listed = subprocess.run(["git", "-C", str(root), "ls-files", "--", "README.md"], capture_output=True, text=True)
    if listed.stdout.strip():
        hits += _readme_hits((Path(root) / "README.md").read_text())
    return sorted(set(hits))


@pytest.mark.process("git grep over the repository this suite runs in")
def test_no_tracked_file_outside_specs_adr_tdd_and_skills_tdd_names_vcoord_or_a_coordinator_4102():
    hits = sweep(ROOT)
    assert hits == [], "vcoord or coordinator named at: " + ", ".join(hits)


README = """# x

## Install

`/vinstall` links five skills. A link an earlier install left to `vcoord` or `vstop` is removed,
reported as `removed <name>`. To type one, link it by hand.

## Next
"""


def _repo(tmp_path, files):
    subprocess.run(["git", "-C", str(tmp_path), "init", "-q", "-b", "main"], check=True)
    for name, text in files.items():
        (tmp_path / name).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / name).write_text(text)
    subprocess.run(["git", "-C", str(tmp_path), "add", "-A"], check=True)
    return tmp_path


@pytest.mark.process("git init, add and grep on a throwaway repository")
def test_the_sweep_passes_vcoord_only_in_the_install_sentence_that_lists_the_removed_links(tmp_path):
    repo = _repo(tmp_path, {"README.md": README, "specs/prd.md": "vcoord coordinator\n",
                            "skills/tdd/SKILL.md": "the coordinator\n", "skills/vdev/SKILL.md": "the dev session\n"})
    assert sweep(repo) == []


@pytest.mark.process("git init, add and grep on a throwaway repository")
def test_the_sweep_names_a_coordinator_put_back_in_a_tracked_skill_file(tmp_path):
    repo = _repo(tmp_path, {"README.md": README, "skills/vdev/SKILL.md": "one\nreport to the Coordinator\n"})
    assert sweep(repo) == ["skills/vdev/SKILL.md:2"]


@pytest.mark.process("git init, add and grep on a throwaway repository")
def test_the_sweep_names_vcoord_in_another_readme_sentence_and_coordinator_in_the_install_sentence(tmp_path):
    text = README.replace("To type one,", "Run `/vcoord` first. To type one,").replace("or `vstop`", "or a coordinator")
    repo = _repo(tmp_path, {"README.md": text})
    assert sweep(repo) == ["README.md:5", "README.md:6"]
