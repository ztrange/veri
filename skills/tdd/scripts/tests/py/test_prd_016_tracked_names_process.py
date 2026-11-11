"""PRD 016: no tracked file still names a skill by its long name."""
import re
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[5]
NAMES = ["bail", "coord", "dev", "file", "groom", "handoff", "judge", "merge", "plan", "report", "status", "stop"]
MERGE_TOKEN_FILE = re.compile("veri" + r"-merge-(<pr>|[0-9]+|\*)\.token")
PATTERN = "veri" + "-(" + "|".join(NAMES) + ")([^[:alnum:]_]|$)"


@pytest.mark.process("git grep over the repository this suite runs in")
def test_no_tracked_file_outside_specs_and_tdd_contains_veri_dash_a_renamed_skill_name():
    assert _sweep(ROOT) == []


def _sweep(root):
    run = subprocess.run(
        ["git", "-C", str(root), "grep", "-nIE", PATTERN, "--", ".", ":(exclude)specs", ":(exclude).tdd"],
        capture_output=True,
        text=True,
    )
    assert run.returncode in (0, 1), run.stderr
    long_name = re.compile(PATTERN.replace("[:alnum:]", "A-Za-z0-9"))
    files = []
    for line in run.stdout.splitlines():
        path, _, text = line.split(":", 2)
        if long_name.search(MERGE_TOKEN_FILE.sub("", text)) and path not in files:
            files.append(path)
    return files


@pytest.mark.process("git init, add and grep on a throwaway repository")
def test_the_sweep_reports_a_tracked_file_holding_a_long_name_and_not_one_under_specs(tmp_path):
    (tmp_path / "specs").mkdir()
    (tmp_path / "README.md").write_text("run veri" + "-status now\n")
    (tmp_path / "specs" / "prd.md").write_text("history: veri" + "-bail\n")
    (tmp_path / "clean.md").write_text("run vstatus\n")
    for argv in (["init", "-q"], ["add", "."]):
        subprocess.run(["git", "-C", str(tmp_path), *argv], check=True, capture_output=True)

    assert _sweep(tmp_path) == ["README.md"]


@pytest.mark.process("git init, add and grep on a throwaway repository")
def test_the_sweep_ignores_a_merge_token_file_name_with_a_number_or_a_glob_3579(tmp_path):
    (tmp_path / "token.md").write_text(
        "path veri" + "-merge-42.token\nglob veri" + "-merge-*.token\n"
    )
    for argv in (["init", "-q"], ["add", "."]):
        subprocess.run(["git", "-C", str(tmp_path), *argv], check=True, capture_output=True)

    assert _sweep(tmp_path) == []
