"""Case for how skills/tdd/SKILL.md computes the refactor loop's touched-files list, run in a scratch git repository."""
import os
import pathlib
import re
import subprocess

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
SKILL = SCRIPTS.parent / "SKILL.md"


def git(repo, *args):
    cmd = ["git", "-C", str(repo), "-c", "user.name=veri", "-c", "user.email=veri@example.test", *args]
    return subprocess.run(cmd, capture_output=True, text=True, check=True).stdout


@pytest.mark.process("git commits in a scratch repository, and bash running each touched= line of SKILL.md in it")
def test_skill_md_computes_the_refactor_touched_files_list_through_refactor_touched_sh_in_the_cycle_loop_and_in_resume_and_both_name_only_the_green_commits_source_files(tmp_path):
    repo = tmp_path / "green"
    (repo / ".tdd").mkdir(parents=True)
    (repo / "lib").mkdir()
    (repo / "src").mkdir()
    git(repo, "init", "-q", "-b", "main")
    (repo / ".tdd" / "issue-7.md").write_text("- [ ] a step\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "plan: scope #7")
    (repo / "src" / "zeta.sh").write_text("zeta\n")
    (repo / "lib" / "alpha.test.sh").write_text("alpha\n")
    (repo / ".tdd" / "issue-7.md").write_text("- [x] a step ⟂ refactor pending\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "feat: a step (#7)")
    expected = ["lib/alpha.test.sh", "src/zeta.sh"]
    green = git(repo, "rev-parse", "HEAD").strip()

    lines = [l.strip() for l in (SKILL.read_text() + SKILL.with_name('RESUME.md').read_text()).splitlines() if re.match(r'^\s*touched="\$\(', l)]

    problems = []
    if len(lines) != 2:
        problems.append(f'SKILL.md has {len(lines)} touched="$(…)" computations, expected 2 (cycle loop and Resume)')
    for l in lines:
        if "$S/refactor-touched.sh" not in l:
            problems.append(f"SKILL.md computes touched without $S/refactor-touched.sh: {l}")
        env = {**os.environ, "S": str(SCRIPTS), "green": green}
        run = subprocess.run(["bash", "-c", l + '\nprintf %s "$touched"'], cwd=repo, env=env,
                             capture_output=True, text=True)
        got = [x for x in (run.stdout + run.stderr).replace(",", "\n").split("\n") if x]
        if got != expected:
            problems.append(f"{l} → {','.join(got)!r}, expected {','.join(expected)!r}")
    assert not problems, "\n".join(problems)
