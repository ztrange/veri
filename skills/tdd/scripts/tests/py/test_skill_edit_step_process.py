"""Cases for skill-edit-step.sh that start the real entry point against a real git repository and a stub claude."""
import json
import subprocess

import pytest

from conftest import SCRIPTS

STEP = SCRIPTS / "skill-edit-step.sh"
OWED = SCRIPTS / "prose-owed.sh"
GRADER = """#!/bin/sh
cat > /dev/null
printf '%s\\n' '{"type":"result","subtype":"success","is_error":false,"result":"BEGIN GRADES\\nA1: PASS - ok\\nA2: PASS - ok\\nVERDICT: PASS\\nEND GRADES"}'
"""
LIST = ("## unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
        "| A1 | The widget is %s. | because |\n| A2 | The widget never hums. | quiet |\n")


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), "-c", "user.name=veri", "-c", "user.email=veri@example.test", *args],
                          capture_output=True, text=True, check=True).stdout.strip()


@pytest.mark.process("skill-edit-step.sh run against a real git repository with a stub grader")
def test_changed_ids_that_already_pass_launch_no_author_and_commit_the_list_and_graded_line_exiting_3(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    (repo / ".gitignore").write_text(".tdd/\n")
    (repo / "unit.md").write_text("The widget is painted a deep blue.\nIt stays silent.\n")
    (repo / "REQUIREMENTS.md").write_text(LIST % "blue")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "feat: unit")
    (repo / "issue.md").write_text(
        "## Requirements\n\n### unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
        "| A1 | The widget is a deep blue. | shade |\n")
    claude = tmp_path / "claude"
    claude.write_text(GRADER)
    claude.chmod(0o755)
    env = {"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "HOME": str(tmp_path), "CLAUDE_BIN": str(claude),
           "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}

    ran = subprocess.run([str(STEP), "issue.md", "unit.md"], cwd=repo, capture_output=True, text=True, env=env)
    owed = subprocess.run([str(OWED), "."], cwd=repo, capture_output=True, text=True, env=env)

    log = repo / ".tdd" / "events.jsonl"
    events = [json.loads(l) for l in log.read_text().splitlines()] if log.exists() else []
    others = [e for e in events if e.get("event") != "grading"]
    assert [ran.returncode, git(repo, "rev-list", "--count", "HEAD"),
            sorted(git(repo, "show", "--name-only", "--format=", "HEAD").splitlines()),
            owed.stdout, any("author" in json.dumps(e) for e in others)] \
        == [3, "2", ["GRADED", "REQUIREMENTS.md"], "", True], (ran.stdout, ran.stderr, events)


STUB_MODEL = """#!/bin/sh
prompt=$2
case "$prompt" in
*"You grade a piece of prose"*)
  n=$(cat "$CAP/grades" 2>/dev/null || echo 0)
  echo $((n + 1)) > "$CAP/grades"
  if [ "$n" = 0 ]; then
    reply='BEGIN GRADES\\nA1: FAIL - prose never says crimson\\nA2: PASS - ok\\nVERDICT: REJECT\\nEND GRADES'
  else
    reply='BEGIN GRADES\\nA1: PASS - ok\\nA2: PASS - ok\\nVERDICT: PASS\\nEND GRADES'
  fi ;;
*)
  printf '%s' "$prompt" > "$CAP/author.txt"
  reply='edited' ;;
esac
printf '%s\\n' '{"type":"result","subtype":"success","is_error":false,"result":"'"$reply"'"}'
"""


@pytest.mark.process("skill-edit-step.sh run against a real git repository with a stub grader and a stub author")
def test_a_failing_changed_id_launches_an_author_leaf_under_the_author_role_whose_prompt_has_the_unit_requirements_and_fail_reasons_but_no_why_cell(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    (repo / ".gitignore").write_text(".tdd/\n")
    (repo / "unit.md").write_text("The widget is painted a deep blue.\nIt stays silent.\n")
    (repo / "REQUIREMENTS.md").write_text(LIST % "blue")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "feat: unit")
    (repo / "issue.md").write_text(
        "## Requirements\n\n### unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
        "| A1 | The widget is crimson. | secret-why-cell |\n")
    cap = tmp_path / "cap"
    cap.mkdir()
    claude = tmp_path / "claude"
    claude.write_text(STUB_MODEL)
    claude.chmod(0o755)
    env = {"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "HOME": str(tmp_path), "CLAUDE_BIN": str(claude),
           "CAP": str(cap), "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
           "GIT_COMMITTER_EMAIL": "t@t"}

    ran = subprocess.run([str(STEP), "issue.md", "unit.md"], cwd=repo, capture_output=True, text=True, env=env)

    log = repo / ".tdd" / "events.jsonl"
    events = [json.loads(l) for l in log.read_text().splitlines()] if log.exists() else []
    launches = [e for e in events if e.get("event") == "launch" and e.get("actor") == "author"]
    author = cap / "author.txt"
    prompt = author.read_text() if author.exists() else ""
    assert len(launches) == 1, (ran.returncode, ran.stderr[-700:])
    for wanted in ["It stays silent.", "A1", "The widget is crimson.", "A2", "The widget never hums.",
                   "prose never says crimson"]:
        assert wanted in prompt, (wanted, prompt)
    for secret in ["secret-why-cell", "quiet", "because"]:
        assert secret not in prompt, (secret, prompt)


STUB_UNCHANGED_FAILS = """#!/bin/sh
prompt=$2
case "$prompt" in
*"You grade a piece of prose"*)
  n=$(cat "$CAP/grades" 2>/dev/null || echo 0)
  echo $((n + 1)) > "$CAP/grades"
  if [ "$n" = 0 ]; then
    reply='BEGIN GRADES\\nA1: PASS - ok\\nA2: FAIL - prose never says silent\\nVERDICT: REJECT\\nEND GRADES'
  else
    reply='BEGIN GRADES\\nA1: PASS - ok\\nA2: PASS - ok\\nVERDICT: PASS\\nEND GRADES'
  fi ;;
*)
  git rev-list --count HEAD > "$CAP/commits-at-author"
  reply='edited' ;;
esac
printf '%s\\n' '{"type":"result","subtype":"success","is_error":false,"result":"'"$reply"'"}'
"""


@pytest.mark.process("skill-edit-step.sh run against a real git repository with a stub grader and a stub author")
def test_changed_ids_that_pass_with_an_unchanged_id_failing_make_no_commit_before_the_author_and_do_not_exit_3(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    (repo / ".gitignore").write_text(".tdd/\n")
    (repo / "unit.md").write_text("The widget is painted a deep blue.\nIt hums.\n")
    (repo / "REQUIREMENTS.md").write_text(LIST % "blue")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "feat: unit")
    (repo / "issue.md").write_text(
        "## Requirements\n\n### unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
        "| A1 | The widget is a deep blue. | shade |\n")
    cap = tmp_path / "cap"
    cap.mkdir()
    claude = tmp_path / "claude"
    claude.write_text(STUB_UNCHANGED_FAILS)
    claude.chmod(0o755)
    env = {"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "HOME": str(tmp_path), "CLAUDE_BIN": str(claude),
           "CAP": str(cap), "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
           "GIT_COMMITTER_EMAIL": "t@t"}

    ran = subprocess.run([str(STEP), "issue.md", "unit.md"], cwd=repo, capture_output=True, text=True, env=env)

    at_author = cap / "commits-at-author"
    log = repo / ".tdd" / "events.jsonl"
    events = [json.loads(l) for l in log.read_text().splitlines()] if log.exists() else []
    launches = [e for e in events if e.get("event") == "launch" and e.get("actor") == "author"]
    assert [ran.returncode != 3, len(launches), at_author.read_text().strip() if at_author.exists() else None] \
        == [True, 1, "1"], (ran.returncode, ran.stderr[-700:])


STUB_ALWAYS_REJECT = """#!/bin/sh
prompt=$2
case "$prompt" in
*"You grade a piece of prose"*)
  reply='BEGIN GRADES\\nA1: FAIL - prose never says crimson\\nA2: FAIL - prose still hums\\nVERDICT: REJECT\\nEND GRADES' ;;
*)
  reply='edited' ;;
esac
printf '%s\\n' '{"type":"result","subtype":"success","is_error":false,"result":"'"$reply"'"}'
"""


@pytest.mark.process("skill-edit-step.sh run against a real git repository with a stub grader and a stub author")
def test_a_grader_that_keeps_rejecting_relaunches_the_author_for_the_default_budget_of_three_then_exits_1_naming_every_failing_id(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    (repo / ".gitignore").write_text(".tdd/\n")
    (repo / "unit.md").write_text("The widget is painted a deep blue.\nIt hums.\n")
    (repo / "REQUIREMENTS.md").write_text(LIST % "blue")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "feat: unit")
    (repo / "issue.md").write_text(
        "## Requirements\n\n### unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
        "| A1 | The widget is crimson. | shade |\n")
    claude = tmp_path / "claude"
    claude.write_text(STUB_ALWAYS_REJECT)
    claude.chmod(0o755)
    env = {"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "HOME": str(tmp_path), "CLAUDE_BIN": str(claude),
           "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}

    ran = subprocess.run([str(STEP), "issue.md", "unit.md"], cwd=repo, capture_output=True, text=True, env=env)

    log = repo / ".tdd" / "events.jsonl"
    events = [json.loads(l) for l in log.read_text().splitlines()] if log.exists() else []
    launches = [e for e in events if e.get("event") == "launch" and e.get("actor") == "author"]
    said = ran.stdout + ran.stderr
    assert [ran.returncode, len(launches), "A1" in said, "A2" in said] == [1, 3, True, True], (ran.stdout, ran.stderr[-700:])


@pytest.mark.process("skill-edit-step.sh run against a real git repository with a stub grader and a stub author")
def test_a_grader_that_keeps_rejecting_relaunches_the_author_exactly_veri_skill_edit_budget_times_then_exits_1_naming_the_failing_ids(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    (repo / ".gitignore").write_text(".tdd/\n")
    (repo / "unit.md").write_text("The widget is painted a deep blue.\nIt hums.\n")
    (repo / "REQUIREMENTS.md").write_text(LIST % "blue")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "feat: unit")
    (repo / "issue.md").write_text(
        "## Requirements\n\n### unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
        "| A1 | The widget is crimson. | shade |\n")
    claude = tmp_path / "claude"
    claude.write_text(STUB_ALWAYS_REJECT)
    claude.chmod(0o755)
    env = {"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "HOME": str(tmp_path), "CLAUDE_BIN": str(claude),
           "VERI_SKILL_EDIT_BUDGET": "2",
           "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}

    ran = subprocess.run([str(STEP), "issue.md", "unit.md"], cwd=repo, capture_output=True, text=True, env=env)

    log = repo / ".tdd" / "events.jsonl"
    events = [json.loads(l) for l in log.read_text().splitlines()] if log.exists() else []
    launches = [e for e in events if e.get("event") == "launch" and e.get("actor") == "author"]
    said = ran.stdout + ran.stderr
    assert [ran.returncode, len(launches), "A1" in said, "A2" in said] == [1, 2, True, True], (ran.stdout, ran.stderr[-700:])


STUB_UNPARSEABLE = """#!/bin/sh
printf '%s\\n' '{"type":"result","subtype":"success","is_error":false,"result":"no verdict here"}'
"""


@pytest.mark.process("skill-edit-step.sh run against a real git repository with a stub grader that gives no verdict")
def test_a_grader_that_gives_no_parseable_verdict_exits_2(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    (repo / ".gitignore").write_text(".tdd/\n")
    (repo / "unit.md").write_text("The widget is painted a deep blue.\nIt stays silent.\n")
    (repo / "REQUIREMENTS.md").write_text(LIST % "blue")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "feat: unit")
    (repo / "issue.md").write_text(
        "## Requirements\n\n### unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
        "| A1 | The widget is a deep blue. | shade |\n")
    claude = tmp_path / "claude"
    claude.write_text(STUB_UNPARSEABLE)
    claude.chmod(0o755)
    env = {"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "HOME": str(tmp_path), "CLAUDE_BIN": str(claude),
           "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}

    ran = subprocess.run([str(STEP), "issue.md", "unit.md"], cwd=repo, capture_output=True, text=True, env=env)

    log = repo / ".tdd" / "events.jsonl"
    events = [json.loads(l) for l in log.read_text().splitlines()] if log.exists() else []
    assert [ran.returncode, git(repo, "rev-list", "--count", "HEAD"),
            [e.get("event") for e in events if e.get("event") == "skill-edit-no-author"],
            "skill-edit-step.sh:" in ran.stderr, "grade-prose.sh: no verdict obtained" in ran.stderr] \
        == [2, "1", [], False, True], (ran.stdout, ran.stderr[-700:])


STUB_AUTHOR_KILLED = """#!/bin/sh
prompt=$2
case "$prompt" in
*"You grade a piece of prose"*)
  n=$(cat "$CAP/grades" 2>/dev/null || echo 0)
  echo $((n + 1)) > "$CAP/grades"
  if [ "$n" = 0 ]; then
    reply='BEGIN GRADES\\nA1: FAIL - prose never says crimson\\nA2: PASS - ok\\nVERDICT: REJECT\\nEND GRADES'
  else
    reply='BEGIN GRADES\\nA1: PASS - ok\\nA2: PASS - ok\\nVERDICT: PASS\\nEND GRADES'
  fi ;;
*)
  exit 2 ;;
esac
printf '%s\\n' '{"type":"result","subtype":"success","is_error":false,"result":"'"$reply"'"}'
"""


@pytest.mark.process("skill-edit-step.sh run against a real git repository with a stub grader and a stub author that exits 2")
def test_an_author_leaf_whose_supervisor_exits_2_exits_2_without_grading_again_or_relaunching(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    (repo / ".gitignore").write_text(".tdd/\n")
    (repo / "unit.md").write_text("The widget is painted a deep blue.\nIt stays silent.\n")
    (repo / "REQUIREMENTS.md").write_text(LIST % "blue")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "feat: unit")
    (repo / "issue.md").write_text(
        "## Requirements\n\n### unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
        "| A1 | The widget is crimson. | shade |\n")
    cap = tmp_path / "cap"
    cap.mkdir()
    claude = tmp_path / "claude"
    claude.write_text(STUB_AUTHOR_KILLED)
    claude.chmod(0o755)
    env = {"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "HOME": str(tmp_path), "CLAUDE_BIN": str(claude),
           "CAP": str(cap), "VERI_STUCK_RETRIES": "0", "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
           "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}

    ran = subprocess.run([str(STEP), "issue.md", "unit.md"], cwd=repo, capture_output=True, text=True, env=env)

    log = repo / ".tdd" / "events.jsonl"
    events = [json.loads(l) for l in log.read_text().splitlines()] if log.exists() else []
    launches = [e for e in events if e.get("event") == "launch" and e.get("actor") == "author"]
    assert [ran.returncode, len(launches), (cap / "grades").read_text().strip(),
            git(repo, "rev-list", "--count", "HEAD")] == [2, 1, "1", "1"], (ran.stdout, ran.stderr[-700:])


STUB_AUTHOR_TOUCHES_GRADED = """#!/bin/sh
prompt=$2
case "$prompt" in
*"You grade a piece of prose"*)
  n=$(cat "$CAP/grades" 2>/dev/null || echo 0)
  echo $((n + 1)) > "$CAP/grades"
  if [ "$n" = 0 ]; then
    reply='BEGIN GRADES\\nA1: FAIL - prose never says crimson\\nA2: PASS - ok\\nVERDICT: REJECT\\nEND GRADES'
  else
    reply='BEGIN GRADES\\nA1: PASS - ok\\nA2: PASS - ok\\nVERDICT: PASS\\nEND GRADES'
  fi ;;
*)
  echo tampered > "$REPO/GRADED"
  reply='edited' ;;
esac
printf '%s\\n' '{"type":"result","subtype":"success","is_error":false,"result":"'"$reply"'"}'
"""


@pytest.mark.process("skill-edit-step.sh run against a real git repository with a stub grader and a stub author that touches GRADED")
def test_an_attempt_that_grades_pass_but_whose_author_touched_graded_is_rejected_spending_the_attempt_and_commits_nothing(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    (repo / ".gitignore").write_text(".tdd/\n")
    (repo / "unit.md").write_text("The widget is painted a deep blue.\nIt stays silent.\n")
    (repo / "REQUIREMENTS.md").write_text(LIST % "blue")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "feat: unit")
    (repo / "issue.md").write_text(
        "## Requirements\n\n### unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
        "| A1 | The widget is crimson. | shade |\n")
    cap = tmp_path / "cap"
    cap.mkdir()
    claude = tmp_path / "claude"
    claude.write_text(STUB_AUTHOR_TOUCHES_GRADED)
    claude.chmod(0o755)
    env = {"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "HOME": str(tmp_path), "CLAUDE_BIN": str(claude),
           "CAP": str(cap), "REPO": str(repo), "VERI_SKILL_EDIT_BUDGET": "1",
           "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}

    ran = subprocess.run([str(STEP), "issue.md", "unit.md"], cwd=repo, capture_output=True, text=True, env=env)

    committed = subprocess.run(["git", "-C", str(repo), "ls-tree", "-r", "--name-only", "HEAD"],
                               capture_output=True, text=True).stdout.split()
    assert [ran.returncode, git(repo, "rev-list", "--count", "HEAD"), "GRADED" in committed] \
        == [1, "1", False], (ran.stdout, ran.stderr[-700:])


STUB_AUTHOR_EDITS_PROSE = STUB_AUTHOR_TOUCHES_GRADED.replace(
    'echo tampered > "$REPO/GRADED"', 'echo "The widget is crimson." >> "$REPO/unit.md"')


@pytest.mark.process("skill-edit-step.sh run against a real git repository with a stub grader and a stub author that edits the prose")
def test_an_attempt_that_grades_pass_and_passes_the_guard_commits_list_prose_and_graded_in_one_commit_exiting_0_leaving_nothing_owed(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    (repo / ".gitignore").write_text(".tdd/\n")
    (repo / "unit.md").write_text("The widget is painted a deep blue.\nIt stays silent.\n")
    (repo / "REQUIREMENTS.md").write_text(LIST % "blue")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "feat: unit")
    (repo / "issue.md").write_text(
        "## Requirements\n\n### unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
        "| A1 | The widget is crimson. | shade |\n")
    cap = tmp_path / "cap"
    cap.mkdir()
    claude = tmp_path / "claude"
    claude.write_text(STUB_AUTHOR_EDITS_PROSE)
    claude.chmod(0o755)
    env = {"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "HOME": str(tmp_path), "CLAUDE_BIN": str(claude),
           "CAP": str(cap), "REPO": str(repo),
           "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}

    ran = subprocess.run([str(STEP), "issue.md", "unit.md"], cwd=repo, capture_output=True, text=True, env=env)
    owed = subprocess.run([str(OWED), "."], cwd=repo, capture_output=True, text=True, env=env)

    assert [ran.returncode, git(repo, "rev-list", "--count", "HEAD"),
            sorted(git(repo, "show", "--name-only", "--format=", "HEAD").splitlines()), owed.stdout] \
        == [0, "2", ["GRADED", "REQUIREMENTS.md", "unit.md"], ""], (ran.stdout, ran.stderr[-700:])


STUB_REASON_PER_GRADING = """#!/bin/sh
prompt=$2
case "$prompt" in
*"You grade a piece of prose"*)
  n=$(cat "$CAP/grades" 2>/dev/null || echo 0)
  echo $((n + 1)) > "$CAP/grades"
  case "$n" in
  0) reply='BEGIN GRADES\\nA1: FAIL - first-reason-alpha\\nA2: PASS - ok\\nVERDICT: REJECT\\nEND GRADES' ;;
  1) reply='BEGIN GRADES\\nA1: FAIL - second-reason-bravo\\nA2: PASS - ok\\nVERDICT: REJECT\\nEND GRADES' ;;
  *) reply='BEGIN GRADES\\nA1: PASS - ok\\nA2: PASS - ok\\nVERDICT: PASS\\nEND GRADES' ;;
  esac ;;
*)
  k=$(cat "$CAP/authors" 2>/dev/null || echo 0)
  echo $((k + 1)) > "$CAP/authors"
  printf '%s' "$prompt" > "$CAP/author-$((k + 1)).txt"
  reply='edited' ;;
esac
printf '%s\\n' '{"type":"result","subtype":"success","is_error":false,"result":"'"$reply"'"}'
"""


@pytest.mark.process("skill-edit-step.sh run against a real git repository with a stub grader giving a different FAIL reason per grading and a stub author")
def test_a_relaunched_authors_prompt_carries_the_fail_reasons_of_the_latest_grading_not_the_first_ones(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    (repo / ".gitignore").write_text(".tdd/\n")
    (repo / "unit.md").write_text("The widget is painted a deep blue.\nIt stays silent.\n")
    (repo / "REQUIREMENTS.md").write_text(LIST % "blue")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "feat: unit")
    (repo / "issue.md").write_text(
        "## Requirements\n\n### unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
        "| A1 | The widget is crimson. | shade |\n")
    cap = tmp_path / "cap"
    cap.mkdir()
    claude = tmp_path / "claude"
    claude.write_text(STUB_REASON_PER_GRADING)
    claude.chmod(0o755)
    env = {"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "HOME": str(tmp_path), "CLAUDE_BIN": str(claude),
           "CAP": str(cap), "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
           "GIT_COMMITTER_EMAIL": "t@t"}

    ran = subprocess.run([str(STEP), "issue.md", "unit.md"], cwd=repo, capture_output=True, text=True, env=env)

    second = cap / "author-2.txt"
    prompt = second.read_text() if second.exists() else ""
    assert "second-reason-bravo" in prompt, (ran.returncode, ran.stderr[-700:], prompt)
    assert "first-reason-alpha" not in prompt, prompt
