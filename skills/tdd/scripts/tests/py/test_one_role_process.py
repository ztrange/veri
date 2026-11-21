"""PRD 026.8: the role scripts, run as the shims they are, refuse `coord` and leave its state files alone (CR1,
CR5); no tracked file under skills/tdd outside its tests names the retired role (CR7)."""
import re
import subprocess
from pathlib import Path

import pytest

from conftest import INTERPRETER_VENV

SCRIPTS = Path(__file__).resolve().parents[2]
ROOT = SCRIPTS.parents[2]
CALLS = [
    ("role-state.sh", ["coord", "show"]),
    ("role-state.sh", ["coord", "--lane", "mu", "set", "n", "2"]),
    ("status.sh", ["--recover", "coord"]),
]


@pytest.mark.process("git init of a scratch repository, then each role script run as the /bin/sh shim it is")
@pytest.mark.parametrize("shim,argv", CALLS)
def test_issue_4103_a_role_script_given_coord_exits_2_with_its_usage_and_leaves_role_coord_state_byte_for_byte(
        shim, argv, tmp_path):
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=tmp_path, check=True)
    tdd = tmp_path / ".tdd"
    tdd.mkdir()
    transcript = tmp_path / "t.jsonl"
    transcript.write_text("{}\n")
    before = {"role-coord.state": "n=3\ncoordinator=sess-1\ntranscript=%s\nrecovered-at=2026-11-12T10:02:30\n" % transcript,
              "role-coord-mu.state": "n=1\nlane=mu\ntranscript=%s\n" % transcript,
              "reset-request-coord": "2026-11-12T10:00:00\n", "reset-request-coord-mu": "2026-11-12T10:00:00\n"}
    for name, text in before.items():
        (tdd / name).write_text(text)

    done = subprocess.run([str(SCRIPTS / shim), *argv], cwd=tmp_path, stdin=subprocess.DEVNULL, capture_output=True,
                          text=True, timeout=20,
                          env={"PATH": "/usr/bin:/bin", "HOME": str(tmp_path), "VERI_VENV": INTERPRETER_VENV,
                               "VERI_POLL": "0.05", "CLAUDE_CODE_SESSION_ID": "sess-1"})

    after = {p.name: p.read_text() for p in tdd.iterdir()}
    usage = [l for l in done.stderr.splitlines() if l.startswith("usage:")]
    names_dev_alone = bool(usage) and re.search(r"\bdev\b", usage[-1]) is not None and "coord" not in usage[-1]
    assert (done.returncode, done.stdout, after, names_dev_alone) == (2, "", before, True), done.stderr


WORDS = r"vcoord|coordinator|VERI_RESET_GROWTH_COORD|coord"
EXCEPTION = ("skills/tdd/scripts/veri/install_links.py", re.compile(r'^RETIRED = \((?:"\w+", )*"vcoord"(?:, "\w+")*\)$'))


def sweep(root):
    """Every file:line under skills/tdd, outside its tests, naming the retired role, but the one closed exception."""
    run = subprocess.run(["git", "-C", str(root), "grep", "-n", "-I", "-i", "-w", "-E", WORDS, "--", "skills/tdd",
                          ":(exclude)skills/tdd/scripts/tests"], capture_output=True, text=True)
    assert run.returncode in (0, 1), run.stderr
    hits = []
    for line in run.stdout.splitlines():
        path, number, text = line.split(":", 2)
        found = re.findall(r"(?<![A-Za-z0-9_])(?:%s)(?![A-Za-z0-9_])" % WORDS, text, re.I)
        if path == EXCEPTION[0] and EXCEPTION[1].match(text) and found == ["vcoord"]:
            continue
        hits.append("%s:%s" % (path, number))
    return hits


@pytest.mark.process("git grep over the repository this suite runs in")
def test_no_tracked_file_under_skills_tdd_outside_its_tests_names_the_retired_coord_role_4103():
    hits = sweep(ROOT)
    assert hits == [], "the retired role named at: " + ", ".join(hits)


INSTALL = 'LINKED = ("vdev", "vfile")\nRETIRED = ("vcoord", "vready")\n'


def _repo(tmp_path, files):
    subprocess.run(["git", "-C", str(tmp_path), "init", "-q", "-b", "main"], check=True)
    for name, text in files.items():
        (tmp_path / name).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / name).write_text(text)
    subprocess.run(["git", "-C", str(tmp_path), "add", "-A"], check=True)
    return tmp_path


@pytest.mark.process("git init, add and grep on a throwaway repository")
def test_the_sweep_passes_vcoord_only_in_install_links_retired_tuple_and_any_word_under_tests(tmp_path):
    repo = _repo(tmp_path, {"skills/tdd/scripts/veri/install_links.py": INSTALL,
                            "skills/tdd/scripts/tests/py/test_x.py": "role = 'coord'  # coordinator\n",
                            "skills/vdev/SKILL.md": "coord\n"})
    assert sweep(repo) == []


@pytest.mark.process("git init, add and grep on a throwaway repository")
def test_the_sweep_names_each_word_put_back_under_skills_tdd(tmp_path):
    repo = _repo(tmp_path, {"skills/tdd/scripts/veri/install_links.py": INSTALL,
                            "skills/tdd/SCRIPTS.md": "ok\n`role-state.sh <coord|dev>`\n",
                            "skills/tdd/REQUIREMENTS.md": "the Coordinator\n",
                            "skills/tdd/scripts/veri/role_growth.py": 'KNOB = "VERI_RESET_GROWTH_COORD"\n'})
    assert sweep(repo) == ["skills/tdd/REQUIREMENTS.md:1", "skills/tdd/SCRIPTS.md:2",
                           "skills/tdd/scripts/veri/role_growth.py:1"]


@pytest.mark.process("git init, add and grep on a throwaway repository")
def test_the_sweep_names_vcoord_put_back_in_install_links_linked_tuple(tmp_path):
    repo = _repo(tmp_path, {"skills/tdd/scripts/veri/install_links.py": INSTALL.replace('("vdev",', '("vcoord", "vdev",')})
    assert sweep(repo) == ["skills/tdd/scripts/veri/install_links.py:1"]
