"""Cases for skill-edit-step.sh that start the real entry point against a real git repository and a stub claude."""
import json
import subprocess

import pytest

from conftest import INTERPRETER_VENV, SCRIPTS

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
    env = {"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "HOME": str(tmp_path), "VERI_VENV": INTERPRETER_VENV, "CLAUDE_BIN": str(claude),
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
    env = {"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "HOME": str(tmp_path), "VERI_VENV": INTERPRETER_VENV, "CLAUDE_BIN": str(claude),
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
    env = {"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "HOME": str(tmp_path), "VERI_VENV": INTERPRETER_VENV, "CLAUDE_BIN": str(claude),
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
    env = {"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "HOME": str(tmp_path), "VERI_VENV": INTERPRETER_VENV, "CLAUDE_BIN": str(claude),
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
    env = {"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "HOME": str(tmp_path), "VERI_VENV": INTERPRETER_VENV, "CLAUDE_BIN": str(claude),
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
    env = {"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "HOME": str(tmp_path), "VERI_VENV": INTERPRETER_VENV, "CLAUDE_BIN": str(claude),
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
    env = {"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "HOME": str(tmp_path), "VERI_VENV": INTERPRETER_VENV, "CLAUDE_BIN": str(claude),
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
    env = {"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "HOME": str(tmp_path), "VERI_VENV": INTERPRETER_VENV, "CLAUDE_BIN": str(claude),
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
    env = {"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "HOME": str(tmp_path), "VERI_VENV": INTERPRETER_VENV, "CLAUDE_BIN": str(claude),
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
    env = {"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "HOME": str(tmp_path), "VERI_VENV": INTERPRETER_VENV, "CLAUDE_BIN": str(claude),
           "CAP": str(cap), "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
           "GIT_COMMITTER_EMAIL": "t@t"}

    ran = subprocess.run([str(STEP), "issue.md", "unit.md"], cwd=repo, capture_output=True, text=True, env=env)

    second = cap / "author-2.txt"
    prompt = second.read_text() if second.exists() else ""
    assert "second-reason-bravo" in prompt, (ran.returncode, ran.stderr[-700:], prompt)
    assert "first-reason-alpha" not in prompt, prompt


@pytest.mark.process("skill-edit-step.sh run against a real git repository with a stub grader and a bad VERI_SKILL_EDIT_BUDGET")
def test_a_bad_veri_skill_edit_budget_exits_2_from_validating_it_when_every_other_call_before_launching_succeeds(tmp_path):
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
    env = {"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "HOME": str(tmp_path), "VERI_VENV": INTERPRETER_VENV, "CLAUDE_BIN": str(claude),
           "VERI_SKILL_EDIT_BUDGET": "many",
           "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}

    ran = subprocess.run([str(STEP), "issue.md", "unit.md"], cwd=repo, capture_output=True, text=True, env=env)

    log = repo / ".tdd" / "events.jsonl"
    launched = log.exists() and log.read_text().strip() != ""
    assert [ran.returncode, launched, "VERI_SKILL_EDIT_BUDGET" in ran.stderr] == [2, False, True], (ran.stdout, ran.stderr[-700:])


ROWS = "| ID | Requirement | Why |\n|---|---|---|\n| A1 | The widget is blue. | because |\n| A2 | The widget never hums. | quiet |\n"


@pytest.mark.process("skill-edit-step.sh run against a real git repository with a stub grader")
def test_a_unit_holding_its_own_requirements_table_with_no_list_beside_it_has_the_table_moved_into_a_new_requirements_md_in_the_same_commit_1959(tmp_path):
    repo = tmp_path / "repo"
    (repo / "skills" / "veri-dev").mkdir(parents=True)
    git(repo, "init", "-q", "-b", "main")
    (repo / ".gitignore").write_text(".tdd/\n")
    unit = repo / "skills" / "veri-dev" / "SKILL.md"
    unit.write_text("The widget is blue.\nIt stays silent.\n\n## Requirements\n\n" + ROWS)
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "feat: unit")
    (repo / "issue.md").write_text("## Problem\n\nnothing about requirements\n")
    claude = tmp_path / "claude"
    claude.write_text(GRADER)
    claude.chmod(0o755)
    env = {"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "HOME": str(tmp_path), "VERI_VENV": INTERPRETER_VENV, "CLAUDE_BIN": str(claude),
           "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}

    ran = subprocess.run([str(STEP), "issue.md", "skills/veri-dev/SKILL.md"], cwd=repo, capture_output=True,
                         text=True, env=env)

    beside = repo / "skills" / "veri-dev" / "REQUIREMENTS.md"
    moved = beside.read_text() if beside.exists() else ""
    committed = git(repo, "show", "--name-only", "--format=", "HEAD").splitlines()
    assert [ROWS in moved, "## Requirements" in unit.read_text(),
            "skills/veri-dev/REQUIREMENTS.md" in committed and "skills/veri-dev/SKILL.md" in committed] \
        == [True, False, True], (ran.returncode, ran.stdout, ran.stderr[-700:], moved, committed)


@pytest.mark.process("skill-edit-step.sh run against a real git repository")
def test_a_requirements_heading_naming_no_existing_unit_and_not_marked_new_exits_2_naming_the_heading_1959(tmp_path):
    repo = tmp_path / "repo"
    (repo / "skills" / "veri-dev").mkdir(parents=True)
    git(repo, "init", "-q", "-b", "main")
    (repo / ".gitignore").write_text(".tdd/\n")
    (repo / "skills" / "veri-dev" / "SKILL.md").write_text("The widget is blue.\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "feat: unit")
    (repo / "issue.md").write_text("## Requirements\n\n### skills/missing/SKILL.md\n\n" + ROWS)
    env = {"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "HOME": str(tmp_path), "VERI_VENV": INTERPRETER_VENV,
           "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}

    ran = subprocess.run([str(STEP), "issue.md", "skills/veri-dev/SKILL.md"], cwd=repo, capture_output=True,
                         text=True, env=env)

    assert [ran.returncode, "skills/missing/SKILL.md" in ran.stderr] == [2, True], (ran.returncode, ran.stdout, ran.stderr[-700:])


@pytest.mark.process("a real git repository under an in-process skill-edit step with a stub grader and a stub author")
def test_a_rejected_author_attempts_edits_to_the_unit_are_reset_before_the_next_attempt_1959(tmp_path, monkeypatch, run_cli):
    import importlib
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    (repo / "unit.md").write_text("The widget is painted a deep blue.\n")
    (repo / "REQUIREMENTS.md").write_text(LIST % "blue")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "feat: unit")
    (repo / "issue.md").write_text("## Problem\n\nText.\n")
    monkeypatch.chdir(repo)
    for name in ("GIT_AUTHOR_NAME", "GIT_COMMITTER_NAME"):
        monkeypatch.setenv(name, "t")
    for name in ("GIT_AUTHOR_EMAIL", "GIT_COMMITTER_EMAIL"):
        monkeypatch.setenv(name, "t@t")
    skill_edit_step = importlib.import_module("veri.skill_edit_step")
    seen = []

    def author(unit, path, reasons):
        seen.append((repo / unit).read_text())
        with open(repo / unit, "a") as f:
            f.write("A rejected attempt's edit.\n")
        return 0

    monkeypatch.setattr(skill_edit_step, "_grade", lambda *a: (1, "A1: FAIL - no\n"))
    monkeypatch.setattr(skill_edit_step, "_author", author)
    monkeypatch.setattr(skill_edit_step.skill_edit_guard, "main", lambda argv: 0)

    run_cli(skill_edit_step, [str(repo / "issue.md"), "unit.md"], env={"VERI_SKILL_EDIT_BUDGET": "2"})

    assert seen == ["The widget is painted a deep blue.\n"] * 2, seen


@pytest.mark.process("a real git repository under an in-process skill-edit step with a stub grader and a recorded supervise launch")
def test_each_author_attempts_leaf_is_named_author_skill_edit_k_for_its_attempt_number_1959(tmp_path, monkeypatch, run_cli):
    import importlib
    import types
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    (repo / "unit.md").write_text("The widget is painted a deep blue.\n")
    (repo / "REQUIREMENTS.md").write_text(LIST % "blue")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "feat: unit")
    (repo / "issue.md").write_text("## Problem\n\nText.\n")
    monkeypatch.chdir(repo)
    for name in ("GIT_AUTHOR_NAME", "GIT_COMMITTER_NAME"):
        monkeypatch.setenv(name, "t")
    for name in ("GIT_AUTHOR_EMAIL", "GIT_COMMITTER_EMAIL"):
        monkeypatch.setenv(name, "t@t")
    skill_edit_step = importlib.import_module("veri.skill_edit_step")
    real_run = subprocess.run
    names = []

    def run(argv, *args, **kwargs):
        if str(argv[0]).endswith("supervise.sh"):
            names.append(argv[1])
            return types.SimpleNamespace(returncode=0)
        return real_run(argv, *args, **kwargs)

    monkeypatch.setattr(skill_edit_step, "_grade", lambda *a: (1, "A1: FAIL - no\n"))
    monkeypatch.setattr(skill_edit_step.subprocess, "run", run)
    monkeypatch.setattr(skill_edit_step.skill_edit_guard, "main", lambda argv: 0)

    run_cli(skill_edit_step, [str(repo / "issue.md"), "unit.md"], env={"VERI_SKILL_EDIT_BUDGET": "2"})

    assert names == ["author-skill-edit-1", "author-skill-edit-2"], names


@pytest.mark.process("skill-edit-step.sh run against a real git repository with a stub grader")
def test_a_unit_with_no_requirements_list_against_an_issue_with_no_requirements_section_exits_3_leaving_the_unit_unchanged_and_creating_no_requirements_md_1959(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    (repo / ".gitignore").write_text(".tdd/\n")
    (repo / "unit.md").write_text("The widget is painted a deep blue.\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "feat: unit")
    (repo / "issue.md").write_text("## Problem\n\nnothing about requirements\n")
    claude = tmp_path / "claude"
    claude.write_text(GRADER)
    claude.chmod(0o755)
    env = {"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "HOME": str(tmp_path), "VERI_VENV": INTERPRETER_VENV, "CLAUDE_BIN": str(claude),
           "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}

    ran = subprocess.run([str(STEP), "issue.md", "unit.md"], cwd=repo, capture_output=True, text=True, env=env)

    assert [ran.returncode, "Traceback" in ran.stderr, (repo / "unit.md").read_text(),
            (repo / "REQUIREMENTS.md").exists()] \
        == [3, False, "The widget is painted a deep blue.\n", False], (ran.stdout, ran.stderr[-700:])


@pytest.mark.process("skill-edit-step.sh run against a real git repository with a stub grader")
def test_an_issue_rewording_one_row_of_a_unit_below_the_root_with_its_path_section_leaves_one_row_per_id_reworded_in_place_and_no_basename_section_1959(tmp_path):
    repo = tmp_path / "repo"
    (repo / "skills" / "veri-dev").mkdir(parents=True)
    git(repo, "init", "-q", "-b", "main")
    (repo / ".gitignore").write_text(".tdd/\n")
    (repo / "skills" / "veri-dev" / "SKILL.md").write_text("The widget is painted a deep blue.\nIt stays silent.\n")
    beside = repo / "skills" / "veri-dev" / "REQUIREMENTS.md"
    beside.write_text("## skills/veri-dev/SKILL.md\n\n" + ROWS)
    (repo / "issue.md").write_text(
        "## Requirements\n\n### skills/veri-dev/SKILL.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
        "| A1 | The widget is a deep blue. | shade |\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "feat: unit")
    claude = tmp_path / "claude"
    claude.write_text(GRADER)
    claude.chmod(0o755)
    env = {"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "HOME": str(tmp_path), "VERI_VENV": INTERPRETER_VENV, "CLAUDE_BIN": str(claude),
           "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}

    ran = subprocess.run([str(STEP), "issue.md", "skills/veri-dev/SKILL.md"], cwd=repo, capture_output=True,
                         text=True, env=env)

    text = beside.read_text()
    rows = [l for l in text.splitlines() if l.startswith("| A")]
    assert [ran.returncode, rows, "## SKILL.md" in text.splitlines(), git(repo, "status", "--porcelain")] \
        == [3, ["| A1 | The widget is a deep blue. | shade |", "| A2 | The widget never hums. | quiet |"], False, ""], \
        (ran.stdout, ran.stderr[-700:], text)


@pytest.mark.process("skill-edit-step.sh run against a real git repository with a stub grader")
def test_a_new_unit_from_a_path_new_heading_gets_a_requirements_md_section_headed_by_its_repo_relative_path_1959(tmp_path):
    repo = tmp_path / "repo"
    (repo / "skills" / "new-skill").mkdir(parents=True)
    git(repo, "init", "-q", "-b", "main")
    (repo / ".gitignore").write_text(".tdd/\n")
    (repo / "README.md").write_text("hello\n")
    (repo / "issue.md").write_text(
        "## Requirements\n\n### skills/new-skill/SKILL.md (new)\n\n" + ROWS)
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "feat: base")
    claude = tmp_path / "claude"
    claude.write_text(GRADER)
    claude.chmod(0o755)
    env = {"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "HOME": str(tmp_path), "VERI_VENV": INTERPRETER_VENV, "CLAUDE_BIN": str(claude),
           "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}

    ran = subprocess.run([str(STEP), "issue.md", "skills/new-skill/SKILL.md"], cwd=repo, capture_output=True,
                         text=True, env=env)

    beside = repo / "skills" / "new-skill" / "REQUIREMENTS.md"
    headings = [l for l in beside.read_text().splitlines() if l.startswith("## ")] if beside.exists() else []
    assert headings == ["## skills/new-skill/SKILL.md"], (ran.returncode, ran.stdout, ran.stderr[-700:], headings)


@pytest.mark.process("skill-edit-step.sh run against a real git repository with a stub grader")
def test_a_new_unit_from_a_path_new_heading_is_graded_and_signed_exiting_0_or_3_with_a_clean_tree_1959(tmp_path):
    repo = tmp_path / "repo"
    (repo / "skills" / "new-skill").mkdir(parents=True)
    git(repo, "init", "-q", "-b", "main")
    (repo / ".gitignore").write_text(".tdd/\n")
    (repo / "README.md").write_text("hello\n")
    (repo / "issue.md").write_text(
        "## Requirements\n\n### skills/new-skill/SKILL.md (new)\n\n" + ROWS)
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "feat: base")
    claude = tmp_path / "claude"
    claude.write_text(GRADER)
    claude.chmod(0o755)
    env = {"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "HOME": str(tmp_path), "VERI_VENV": INTERPRETER_VENV, "CLAUDE_BIN": str(claude),
           "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}

    ran = subprocess.run([str(STEP), "issue.md", "skills/new-skill/SKILL.md"], cwd=repo, capture_output=True,
                         text=True, env=env)

    graded = repo / "skills" / "new-skill" / "GRADED"
    lines = graded.read_text().splitlines() if graded.exists() else []
    assert [ran.returncode in (0, 3), any("skills/new-skill/SKILL.md" in l for l in lines),
            git(repo, "status", "--porcelain")] == [True, True, ""], \
        (ran.returncode, ran.stdout, ran.stderr[-700:], lines)


@pytest.mark.process("skill-edit-step.sh run against a real git repository with a stub grader")
def test_a_unit_with_no_table_beside_a_requirements_md_holding_only_another_units_section_against_an_issue_stating_no_rows_exits_3_launching_no_grader_leaving_the_tree_clean_1959(tmp_path):
    repo = tmp_path / "repo"
    (repo / "skills" / "veri-dev").mkdir(parents=True)
    git(repo, "init", "-q", "-b", "main")
    (repo / ".gitignore").write_text(".tdd/\n")
    (repo / "skills" / "veri-dev" / "SKILL.md").write_text("The widget is painted a deep blue.\n")
    beside = repo / "skills" / "veri-dev" / "REQUIREMENTS.md"
    original = "## skills/other/SKILL.md\n\n" + ROWS
    beside.write_text(original)
    (repo / "issue.md").write_text("## Problem\n\nnothing about requirements\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "feat: unit")
    launched = tmp_path / "launched"
    claude = tmp_path / "claude"
    claude.write_text(GRADER + "echo run >> '%s'\n" % launched)
    claude.chmod(0o755)
    env = {"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "HOME": str(tmp_path), "VERI_VENV": INTERPRETER_VENV, "CLAUDE_BIN": str(claude),
           "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}

    ran = subprocess.run([str(STEP), "issue.md", "skills/veri-dev/SKILL.md"], cwd=repo, capture_output=True,
                         text=True, env=env)

    assert [ran.returncode, launched.exists(), beside.read_text(), (beside.parent / "GRADED").exists(),
            git(repo, "status", "--porcelain")] == [3, False, original, False, ""], \
        (ran.stdout, ran.stderr[-700:])


@pytest.mark.process("skill-edit-step.sh run against a real git repository with a stub grader")
def test_a_path_new_heading_for_a_unit_in_a_directory_that_does_not_exist_yet_is_not_refused_and_creates_the_unit_1959(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    (repo / ".gitignore").write_text(".tdd/\n")
    (repo / "README.md").write_text("hello\n")
    (repo / "issue.md").write_text(
        "## Requirements\n\n### skills/new-skill/SKILL.md (new)\n\n" + ROWS)
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "feat: base")
    claude = tmp_path / "claude"
    claude.write_text(GRADER)
    claude.chmod(0o755)
    env = {"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "HOME": str(tmp_path), "VERI_VENV": INTERPRETER_VENV, "CLAUDE_BIN": str(claude),
           "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}

    ran = subprocess.run([str(STEP), "issue.md", "skills/new-skill/SKILL.md"], cwd=repo, capture_output=True,
                         text=True, env=env)

    assert [ran.returncode in (0, 3), (repo / "skills" / "new-skill" / "SKILL.md").exists()] == [True, True], \
        (ran.returncode, ran.stdout, ran.stderr[-700:])


@pytest.mark.process("skill-edit-step.sh run against a real git repository with a stub grader")
def test_an_issue_rewording_and_adding_rows_edits_only_the_path_section_leaving_a_following_basename_section_byte_identical_1959(tmp_path):
    repo = tmp_path / "repo"
    (repo / "skills" / "veri-dev").mkdir(parents=True)
    git(repo, "init", "-q", "-b", "main")
    (repo / ".gitignore").write_text(".tdd/\n")
    (repo / "skills" / "veri-dev" / "SKILL.md").write_text("The widget is painted a deep blue.\nIt stays silent.\n")
    beside = repo / "skills" / "veri-dev" / "REQUIREMENTS.md"
    basename_section = "## SKILL.md\n\n" + ROWS
    beside.write_text("## skills/veri-dev/SKILL.md\n\n" + ROWS + "\n" + basename_section)
    (repo / "issue.md").write_text(
        "## Requirements\n\n### skills/veri-dev/SKILL.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
        "| A1 | The widget is a deep blue. | shade |\n| A3 | The widget never rattles. | steady |\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "feat: unit")
    claude = tmp_path / "claude"
    claude.write_text(GRADER.replace("A2: PASS - ok\\n", "A2: PASS - ok\\nA3: PASS - ok\\n")
                        .replace('"is_error":false,', '"is_error":false,"duration_ms":1,"duration_api_ms":1,"num_turns":1,"total_cost_usd":0,"usage":{"input_tokens":1,"output_tokens":1,"cache_read_input_tokens":0,"cache_creation_input_tokens":0},'))
    claude.chmod(0o755)
    env = {"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "HOME": str(tmp_path), "VERI_VENV": INTERPRETER_VENV, "CLAUDE_BIN": str(claude),
           "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}

    ran = subprocess.run([str(STEP), "issue.md", "skills/veri-dev/SKILL.md"], cwd=repo, capture_output=True,
                         text=True, env=env)

    text = beside.read_text()
    path_part, _, basename_part = text.partition("## SKILL.md\n")
    assert [ran.returncode, [l for l in path_part.splitlines() if l.startswith("| A")], "## SKILL.md\n" + basename_part] \
        == [3, ["| A1 | The widget is a deep blue. | shade |", "| A2 | The widget never hums. | quiet |",
                "| A3 | The widget never rattles. | steady |"], basename_section], (ran.stdout, ran.stderr[-700:], text)


STUB_RECORDING_ARGS = STUB_MODEL.replace(
    """  printf '%s' "$prompt" > "$CAP/author.txt\"""",
    """  printf '%s\\n' "$@" > "$CAP/author-args.txt\"""")


@pytest.mark.process("skill-edit-step.sh run against a real git repository with a stub grader and a stub author recording its arguments")
def test_an_author_leaf_is_launched_with_permission_mode_bypass_permissions_2041(tmp_path):
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
        "| A1 | The widget is crimson. | why |\n")
    cap = tmp_path / "cap"
    cap.mkdir()
    claude = tmp_path / "claude"
    claude.write_text(STUB_RECORDING_ARGS)
    claude.chmod(0o755)
    env = {"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "HOME": str(tmp_path), "VERI_VENV": INTERPRETER_VENV, "CLAUDE_BIN": str(claude),
           "CAP": str(cap), "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
           "GIT_COMMITTER_EMAIL": "t@t"}

    ran = subprocess.run([str(STEP), "issue.md", "unit.md"], cwd=repo, capture_output=True, text=True, env=env)

    recorded = cap / "author-args.txt"
    args = recorded.read_text().splitlines() if recorded.exists() else None
    assert args is not None, (ran.returncode, ran.stderr[-700:])
    pairs = [args[i:i + 2] for i in range(len(args) - 1)]
    assert ["--permission-mode", "bypassPermissions"] in pairs, args


STUB_ROLE_LOG = """#!/bin/sh
prompt=$2
case "$prompt" in
*"You grade a piece of prose"*)
  echo grader >> "$CAP/roles"
  reply='BEGIN GRADES\\nA1: PASS - ok\\nA2: PASS - ok\\nVERDICT: PASS\\nEND GRADES' ;;
*)
  echo author >> "$CAP/roles"
  reply='edited' ;;
esac
printf '%s\\n' '{"type":"result","subtype":"success","is_error":false,"result":"'"$reply"'"}'
"""


@pytest.mark.process("skill-edit-step.sh run against a real git repository with a stub claude recording every call by role")
def test_a_new_empty_unit_launches_the_author_before_any_grader_call_2072(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    (repo / ".gitignore").write_text(".tdd/\n")
    (repo / "README.md").write_text("hello\n")
    (repo / "issue.md").write_text("## Requirements\n\n### skills/new-skill/SKILL.md (new)\n\n" + ROWS)
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "feat: base")
    cap = tmp_path / "cap"
    cap.mkdir()
    claude = tmp_path / "claude"
    claude.write_text(STUB_ROLE_LOG)
    claude.chmod(0o755)
    env = {"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "HOME": str(tmp_path), "VERI_VENV": INTERPRETER_VENV, "CLAUDE_BIN": str(claude),
           "CAP": str(cap), "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
           "GIT_COMMITTER_EMAIL": "t@t"}

    ran = subprocess.run([str(STEP), "issue.md", "skills/new-skill/SKILL.md"], cwd=repo, capture_output=True,
                         text=True, env=env)

    roles = cap / "roles"
    calls = roles.read_text().split() if roles.exists() else []
    assert calls[:1] == ["author"], (calls, ran.returncode, ran.stderr[-700:])


STUB_WRITES_UNIT = STUB_ROLE_LOG.replace(
    "  reply='edited' ;;",
    "  echo 'The new skill is described.' >skills/new-skill/SKILL.md\n  reply='edited' ;;")


@pytest.mark.process("skill-edit-step.sh run against a real git repository with a stub claude whose author writes the new unit")
def test_a_new_empty_unit_the_author_then_writes_exits_zero_and_is_committed_2072(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    (repo / ".gitignore").write_text(".tdd/\n")
    (repo / "README.md").write_text("hello\n")
    (repo / "issue.md").write_text("## Requirements\n\n### skills/new-skill/SKILL.md (new)\n\n" + ROWS)
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "feat: base")
    cap = tmp_path / "cap"
    cap.mkdir()
    claude = tmp_path / "claude"
    claude.write_text(STUB_WRITES_UNIT)
    claude.chmod(0o755)
    env = {"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "HOME": str(tmp_path), "VERI_VENV": INTERPRETER_VENV, "CLAUDE_BIN": str(claude),
           "CAP": str(cap), "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
           "GIT_COMMITTER_EMAIL": "t@t"}

    ran = subprocess.run([str(STEP), "issue.md", "skills/new-skill/SKILL.md"], cwd=repo, capture_output=True,
                         text=True, env=env)

    committed = subprocess.run(["git", "show", "HEAD:skills/new-skill/SKILL.md"], cwd=repo, capture_output=True,
                               text=True).stdout
    assert [ran.returncode, committed] == [0, "The new skill is described.\n"], (ran.returncode, ran.stderr[-700:])


@pytest.mark.process("skill-edit-step.sh run against a real git repository with a stub claude recording every call by role")
def test_a_non_empty_existing_unit_is_graded_first_and_a_grader_that_passes_every_row_launches_no_author_exiting_3_2072(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    (repo / ".gitignore").write_text(".tdd/\n")
    (repo / "unit.md").write_text("The widget is blue.\nIt stays silent.\n")
    (repo / "REQUIREMENTS.md").write_text(LIST % "blue")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "feat: unit")
    (repo / "issue.md").write_text(
        "## Requirements\n\n### unit.md\n\n| ID | Requirement | Why |\n|---|---|---|\n"
        "| A1 | The widget is a deep blue. | shade |\n")
    cap = tmp_path / "cap"
    cap.mkdir()
    claude = tmp_path / "claude"
    claude.write_text(STUB_ROLE_LOG)
    claude.chmod(0o755)
    env = {"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "HOME": str(tmp_path), "VERI_VENV": INTERPRETER_VENV, "CLAUDE_BIN": str(claude),
           "CAP": str(cap), "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
           "GIT_COMMITTER_EMAIL": "t@t"}

    ran = subprocess.run([str(STEP), "issue.md", "unit.md"], cwd=repo, capture_output=True, text=True, env=env)

    roles = cap / "roles"
    calls = roles.read_text().split() if roles.exists() else []
    assert [ran.returncode, calls] == [3, ["grader"]], (ran.returncode, calls, ran.stderr[-700:])
