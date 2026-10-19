"""Cases for grade-prose.sh that start a real process: the launcher and a stub claude."""
import json
import subprocess
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[2]
STUB = """#!/bin/sh
{ printf '%s\\n' "$@"; cat; } > "$STUB_RECORD"
printf '%s\\n' '{"type":"result","subtype":"success","is_error":false,"result":"BEGIN GRADES\\nA1: PASS - ok\\nA2: PASS - ok\\nEND GRADES\\nVERDICT: PASS"}'
"""
REQUIREMENTS = """## guide/unit.md

| ID | Requirement | Why |
|---|---|---|
| A1 | The widget is blue. | because |
| A2 | The widget never hums. | because |
"""
PROSE = "The widget is painted a deep blue.\nIt stays silent.\n"


@pytest.mark.process("grade-prose.sh launching a stub claude through supervise.sh")
def test_a_whole_file_unit_sends_the_stub_claude_the_unit_text_and_every_requirement_id_and_text(tmp_path):
    (tmp_path / "guide").mkdir()
    (tmp_path / "guide" / "unit.md").write_text(PROSE)
    (tmp_path / "REQUIREMENTS.md").write_text(REQUIREMENTS)
    claude = tmp_path / "claude"
    claude.write_text(STUB)
    claude.chmod(0o755)
    record = tmp_path / "record.txt"

    subprocess.run([str(SCRIPTS / "grade-prose.sh"), "REQUIREMENTS.md", "guide/unit.md"], cwd=tmp_path,
                   capture_output=True, env={"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "HOME": str(tmp_path),
                                             "CLAUDE_BIN": str(claude), "STUB_RECORD": str(record)})

    received = record.read_text() if record.exists() else ""
    assert [PROSE in received, "A1" in received, "The widget is blue." in received,
            "A2" in received, "The widget never hums." in received] == [True] * 5, received


@pytest.mark.process("grade-prose.sh launching a stub claude through supervise.sh")
def test_the_prompt_sent_to_the_stub_claude_contains_no_text_from_any_why_cell(tmp_path):
    (tmp_path / "guide").mkdir()
    (tmp_path / "guide" / "unit.md").write_text(PROSE)
    (tmp_path / "REQUIREMENTS.md").write_text(REQUIREMENTS.replace("| because |", "| zebra-rationale-%s |", 1)
                                              .replace("| because |", "| quokka-rationale |") % "one")
    claude = tmp_path / "claude"
    claude.write_text(STUB)
    claude.chmod(0o755)
    record = tmp_path / "record.txt"

    subprocess.run([str(SCRIPTS / "grade-prose.sh"), "REQUIREMENTS.md", "guide/unit.md"], cwd=tmp_path,
                   capture_output=True, env={"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "HOME": str(tmp_path),
                                             "CLAUDE_BIN": str(claude), "STUB_RECORD": str(record)})

    received = record.read_text() if record.exists() else ""
    assert ["The widget never hums." in received, "zebra-rationale" in received, "quokka-rationale" in received] \
        == [True, False, False], received


@pytest.mark.process("grade-prose.sh launching a stub claude through supervise.sh, in a git repo with history")
def test_a_unit_graded_in_a_repo_with_history_gets_a_prompt_carrying_no_diff_and_no_commit_message(tmp_path):
    (tmp_path / "guide").mkdir()
    (tmp_path / "guide" / "unit.md").write_text("The widget was painted green-old-wording.\n")
    (tmp_path / "REQUIREMENTS.md").write_text(REQUIREMENTS)
    claude = tmp_path / "claude"
    claude.write_text(STUB)
    claude.chmod(0o755)
    record = tmp_path / "record.txt"
    env = {"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "HOME": str(tmp_path),
           "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}
    for argv in (["init", "-q"], ["add", "."], ["commit", "-q", "-m", "quokka-commit-message"]):
        subprocess.run(["git", *argv], cwd=tmp_path, env=env, check=True, capture_output=True)
    (tmp_path / "guide" / "unit.md").write_text(PROSE)

    subprocess.run([str(SCRIPTS / "grade-prose.sh"), "REQUIREMENTS.md", "guide/unit.md"], cwd=tmp_path,
                   capture_output=True, env={**env, "CLAUDE_BIN": str(claude), "STUB_RECORD": str(record)})

    received = record.read_text() if record.exists() else ""
    assert [PROSE in received, "quokka-commit-message" in received, "green-old-wording" in received,
            "diff --git" in received] == [True, False, False, False], received


@pytest.mark.process("grade-prose.sh launching a stub claude through supervise.sh")
def test_a_section_unit_sends_only_that_sections_text_from_its_heading_to_the_next_heading_of_the_same_level(tmp_path):
    (tmp_path / "guide").mkdir()
    (tmp_path / "guide" / "unit.md").write_text(
        "# Title\nintro-line-zebra\n## Colour\nThe widget is painted a deep blue.\nIt stays silent.\n"
        "## Sound\nsound-line-quokka\n")
    (tmp_path / "REQUIREMENTS.md").write_text(REQUIREMENTS.replace("## guide/unit.md", "## guide/unit.md#Colour"))
    claude = tmp_path / "claude"
    claude.write_text(STUB)
    claude.chmod(0o755)
    record = tmp_path / "record.txt"

    subprocess.run([str(SCRIPTS / "grade-prose.sh"), "REQUIREMENTS.md", "guide/unit.md#Colour"], cwd=tmp_path,
                   capture_output=True, env={"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "HOME": str(tmp_path),
                                             "CLAUDE_BIN": str(claude), "STUB_RECORD": str(record)})

    received = record.read_text() if record.exists() else ""
    assert ["## Colour\nThe widget is painted a deep blue.\nIt stays silent.\n" in received,
            "intro-line-zebra" in received, "sound-line-quokka" in received] == [True, False, False], received


@pytest.mark.process("grade-prose.sh launching a stub claude through supervise.sh")
def test_a_section_units_text_ends_at_the_next_heading_of_higher_level_as_well_as_the_same_level(tmp_path):
    (tmp_path / "guide").mkdir()
    (tmp_path / "guide" / "unit.md").write_text(
        "# Title\n## Colour\nThe widget is painted a deep blue.\nIt stays silent.\n"
        "# Appendix\nappendix-line-zebra\n")
    (tmp_path / "REQUIREMENTS.md").write_text(REQUIREMENTS.replace("## guide/unit.md", "## guide/unit.md#Colour"))
    claude = tmp_path / "claude"
    claude.write_text(STUB)
    claude.chmod(0o755)
    record = tmp_path / "record.txt"

    subprocess.run([str(SCRIPTS / "grade-prose.sh"), "REQUIREMENTS.md", "guide/unit.md#Colour"], cwd=tmp_path,
                   capture_output=True, env={"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "HOME": str(tmp_path),
                                             "CLAUDE_BIN": str(claude), "STUB_RECORD": str(record)})

    received = record.read_text() if record.exists() else ""
    assert ["## Colour\nThe widget is painted a deep blue.\nIt stays silent.\n" in received,
            "appendix-line-zebra" in received] == [True, False], received


@pytest.mark.process("grade-prose.sh launching a stub claude through supervise.sh")
def test_a_line_starting_with_hash_inside_a_fenced_code_block_never_starts_or_ends_a_section(tmp_path):
    (tmp_path / "guide").mkdir()
    (tmp_path / "guide" / "unit.md").write_text(
        "## Colour\nThe widget is painted a deep blue.\n```sh\n# comment-line-zebra\npaint --blue\n```\n"
        "It stays silent.\n## Sound\nsound-line-quokka\n")
    (tmp_path / "REQUIREMENTS.md").write_text(REQUIREMENTS.replace("## guide/unit.md", "## guide/unit.md#Colour"))
    claude = tmp_path / "claude"
    claude.write_text(STUB)
    claude.chmod(0o755)
    record = tmp_path / "record.txt"

    subprocess.run([str(SCRIPTS / "grade-prose.sh"), "REQUIREMENTS.md", "guide/unit.md#Colour"], cwd=tmp_path,
                   capture_output=True, env={"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "HOME": str(tmp_path),
                                             "CLAUDE_BIN": str(claude), "STUB_RECORD": str(record)})

    received = record.read_text() if record.exists() else ""
    assert ["# comment-line-zebra\npaint --blue\n```\nIt stays silent.\n" in received,
            "sound-line-quokka" in received] == [True, False], received


@pytest.mark.process("grade-prose.sh launching a stub claude through supervise.sh")
def test_the_grader_leaf_is_launched_under_a_leaf_role_distinct_from_every_develop_revise_and_verify_role(tmp_path):
    (tmp_path / "guide").mkdir()
    (tmp_path / "guide" / "unit.md").write_text(PROSE)
    (tmp_path / "REQUIREMENTS.md").write_text(REQUIREMENTS)
    claude = tmp_path / "claude"
    claude.write_text(STUB)
    claude.chmod(0o755)
    record = tmp_path / "record.txt"

    subprocess.run([str(SCRIPTS / "grade-prose.sh"), "REQUIREMENTS.md", "guide/unit.md"], cwd=tmp_path,
                   capture_output=True, env={"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "HOME": str(tmp_path),
                                             "CLAUDE_BIN": str(claude), "STUB_RECORD": str(record)})

    events = tmp_path / ".tdd" / "events.jsonl"
    launches = [json.loads(line) for line in events.read_text().splitlines() if '"event": "launch"' in line] \
        if events.exists() else []
    assert [launch["actor"] for launch in launches] == ["grader"], launches


@pytest.mark.process("grade-prose.sh launching a stub claude through supervise.sh")
def test_the_stub_claude_receives_model_from_grader_conf_and_veri_model_and_verifier_model_do_not_change_it(tmp_path):
    (tmp_path / "guide").mkdir()
    (tmp_path / "guide" / "unit.md").write_text(PROSE)
    (tmp_path / "REQUIREMENTS.md").write_text(REQUIREMENTS)
    claude = tmp_path / "claude"
    claude.write_text(STUB)
    claude.chmod(0o755)
    record = tmp_path / "record.txt"
    conf = SCRIPTS.parents[0] / "grader.conf"
    lines = [l.strip() for l in conf.read_text().splitlines() if l.strip() and not l.lstrip().startswith("#")] \
        if conf.exists() else []
    committed = lines[0].split("=", 1)[-1].strip().strip("'\"") if lines else ""

    subprocess.run([str(SCRIPTS / "grade-prose.sh"), "REQUIREMENTS.md", "guide/unit.md"], cwd=tmp_path,
                   capture_output=True, env={"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "HOME": str(tmp_path),
                                             "CLAUDE_BIN": str(claude), "STUB_RECORD": str(record),
                                             "VERI_MODEL": "env-model-zebra", "VERI_MODEL_VERIFIER": "env-model-quokka"})

    args = (record.read_text() if record.exists() else "").splitlines()
    given = args[args.index("--model") + 1] if "--model" in args else None
    assert committed and given == committed, (given, committed)


@pytest.mark.process("grade-prose.sh launching a stub claude through supervise.sh")
def test_the_command_the_stub_claude_receives_carries_the_same_tool_limits_a_verify_leafs_does(tmp_path):
    (tmp_path / "guide").mkdir()
    (tmp_path / "guide" / "unit.md").write_text(PROSE)
    (tmp_path / "REQUIREMENTS.md").write_text(REQUIREMENTS)
    claude = tmp_path / "claude"
    claude.write_text(STUB)
    claude.chmod(0o755)
    record = tmp_path / "record.txt"

    subprocess.run([str(SCRIPTS / "grade-prose.sh"), "REQUIREMENTS.md", "guide/unit.md"], cwd=tmp_path,
                   capture_output=True, env={"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "HOME": str(tmp_path),
                                             "CLAUDE_BIN": str(claude), "STUB_RECORD": str(record)})

    args = (record.read_text() if record.exists() else "").splitlines()
    settings = json.loads(args[args.index("--settings") + 1]) if "--settings" in args else None
    assert ["--disable-slash-commands" in args, "--strict-mcp-config" in args,
            args[args.index("--mcp-config") + 1] if "--mcp-config" in args else None,
            settings and settings["autoMemoryEnabled"]] == [True, True, '{"mcpServers": {}}', False], args


@pytest.mark.process("grade-prose.sh launching a stub claude through supervise.sh")
def test_a_reply_whose_final_grades_block_has_every_id_line_pass_and_verdict_pass_makes_grade_prose_exit_0(tmp_path):
    (tmp_path / "guide").mkdir()
    (tmp_path / "guide" / "unit.md").write_text(PROSE)
    (tmp_path / "REQUIREMENTS.md").write_text(REQUIREMENTS)
    claude = tmp_path / "claude"
    claude.write_text(STUB)
    claude.chmod(0o755)
    record = tmp_path / "record.txt"

    done = subprocess.run([str(SCRIPTS / "grade-prose.sh"), "REQUIREMENTS.md", "guide/unit.md"], cwd=tmp_path,
                          capture_output=True, text=True,
                          env={"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "HOME": str(tmp_path),
                               "CLAUDE_BIN": str(claude), "STUB_RECORD": str(record)})

    assert done.returncode == 0, (done.returncode, done.stderr)


@pytest.mark.process("grade-prose.sh launching a stub claude through supervise.sh")
def test_a_reply_whose_final_grades_block_has_a_fail_line_and_verdict_reject_makes_grade_prose_exit_1_and_print_the_failing_id_with_its_reason(tmp_path):
    (tmp_path / "guide").mkdir()
    (tmp_path / "guide" / "unit.md").write_text(PROSE)
    (tmp_path / "REQUIREMENTS.md").write_text(REQUIREMENTS)
    claude = tmp_path / "claude"
    claude.write_text(STUB.replace("A2: PASS - ok", "A2: FAIL - the widget hums quokka-loudly")
                      .replace("VERDICT: PASS", "VERDICT: REJECT"))
    claude.chmod(0o755)
    record = tmp_path / "record.txt"

    done = subprocess.run([str(SCRIPTS / "grade-prose.sh"), "REQUIREMENTS.md", "guide/unit.md"], cwd=tmp_path,
                          capture_output=True, text=True,
                          env={"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "HOME": str(tmp_path),
                               "CLAUDE_BIN": str(claude), "STUB_RECORD": str(record)})

    assert [done.returncode, "A2" in done.stdout, "the widget hums quokka-loudly" in done.stdout,
            "A1" in done.stdout] == [1, True, True, False], (done.returncode, done.stdout, done.stderr)


@pytest.mark.process("grade-prose.sh launching a stub claude through supervise.sh")
def test_a_reply_with_two_or_more_fail_lines_prints_every_failing_id_with_its_reason(tmp_path):
    (tmp_path / "guide").mkdir()
    (tmp_path / "guide" / "unit.md").write_text(PROSE)
    (tmp_path / "REQUIREMENTS.md").write_text(REQUIREMENTS.replace(
        "| A2 | The widget never hums. | because |",
        "| A2 | The widget never hums. | because |\n| A3 | The widget is round. | because |"))
    claude = tmp_path / "claude"
    claude.write_text(STUB.replace("A1: PASS - ok", "A1: FAIL - the widget is teal-zebra")
                      .replace("A2: PASS - ok", "A2: PASS - ok\\nA3: FAIL - the widget is square-quokka")
                      .replace("VERDICT: PASS", "VERDICT: REJECT"))
    claude.chmod(0o755)
    record = tmp_path / "record.txt"

    done = subprocess.run([str(SCRIPTS / "grade-prose.sh"), "REQUIREMENTS.md", "guide/unit.md"], cwd=tmp_path,
                          capture_output=True, text=True,
                          env={"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "HOME": str(tmp_path),
                               "CLAUDE_BIN": str(claude), "STUB_RECORD": str(record)})

    assert [done.returncode, "A1" in done.stdout, "teal-zebra" in done.stdout, "A3" in done.stdout,
            "square-quokka" in done.stdout, "A2" in done.stdout] == [1, True, True, True, True, False], \
        (done.returncode, done.stdout, done.stderr)


@pytest.mark.process("grade-prose.sh launching a stub claude through supervise.sh")
def test_a_reply_with_no_grades_block_makes_grade_prose_exit_2_and_name_the_missing_block_on_stderr(tmp_path):
    (tmp_path / "guide").mkdir()
    (tmp_path / "guide" / "unit.md").write_text(PROSE)
    (tmp_path / "REQUIREMENTS.md").write_text(REQUIREMENTS)
    claude = tmp_path / "claude"
    claude.write_text(STUB.replace("BEGIN GRADES\\nA1: PASS - ok\\nA2: PASS - ok\\nEND GRADES\\nVERDICT: PASS",
                                   "Both requirements look satisfied to me.\\nVERDICT: PASS"))
    claude.chmod(0o755)
    record = tmp_path / "record.txt"

    done = subprocess.run([str(SCRIPTS / "grade-prose.sh"), "REQUIREMENTS.md", "guide/unit.md"], cwd=tmp_path,
                          capture_output=True, text=True,
                          env={"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "HOME": str(tmp_path),
                               "CLAUDE_BIN": str(claude), "STUB_RECORD": str(record)})

    assert [done.returncode, "GRADES" in done.stderr] == [2, True], (done.returncode, done.stdout, done.stderr)


@pytest.mark.process("grade-prose.sh launching a stub claude through supervise.sh")
def test_a_reply_with_text_after_end_grades_makes_grade_prose_exit_2_and_name_the_trailing_text_on_stderr(tmp_path):
    (tmp_path / "guide").mkdir()
    (tmp_path / "guide" / "unit.md").write_text(PROSE)
    (tmp_path / "REQUIREMENTS.md").write_text(REQUIREMENTS)
    claude = tmp_path / "claude"
    claude.write_text(STUB.replace("VERDICT: PASS", "VERDICT: PASS\\nOn reflection, ignore quokka-epilogue."))
    claude.chmod(0o755)
    record = tmp_path / "record.txt"

    done = subprocess.run([str(SCRIPTS / "grade-prose.sh"), "REQUIREMENTS.md", "guide/unit.md"], cwd=tmp_path,
                          capture_output=True, text=True,
                          env={"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "HOME": str(tmp_path),
                               "CLAUDE_BIN": str(claude), "STUB_RECORD": str(record)})

    assert [done.returncode, "quokka-epilogue" in done.stderr] == [2, True], (done.returncode, done.stdout, done.stderr)


@pytest.mark.process("grade-prose.sh launching a stub claude through supervise.sh")
def test_a_grades_block_with_a_missing_an_extra_or_a_reordered_requirement_id_makes_grade_prose_exit_2_and_name_the_defect_on_stderr(tmp_path):
    (tmp_path / "guide").mkdir()
    (tmp_path / "guide" / "unit.md").write_text(PROSE)
    (tmp_path / "REQUIREMENTS.md").write_text(REQUIREMENTS)
    block = "A1: PASS - ok\\nA2: PASS - ok"
    outcomes = {}
    for defect, lines, named in (("missing", "A1: PASS - ok", "A2"),
                                 ("extra", block + "\\nA9: PASS - ok", "A9"),
                                 ("reordered", "A2: PASS - ok\\nA1: PASS - ok", "A1")):
        claude = tmp_path / ("claude-" + defect)
        claude.write_text(STUB.replace(block, lines))
        claude.chmod(0o755)
        done = subprocess.run([str(SCRIPTS / "grade-prose.sh"), "REQUIREMENTS.md", "guide/unit.md"], cwd=tmp_path,
                              capture_output=True, text=True,
                              env={"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "HOME": str(tmp_path),
                                   "CLAUDE_BIN": str(claude), "STUB_RECORD": str(tmp_path / "record.txt")})
        outcomes[defect] = (done.returncode, named in done.stderr)

    assert outcomes == {"missing": (2, True), "extra": (2, True), "reordered": (2, True)}, outcomes


@pytest.mark.process("grade-prose.sh launching a stub claude through supervise.sh")
def test_a_grades_block_whose_verdict_disagrees_with_its_lines_makes_grade_prose_exit_2_and_name_the_disagreement_on_stderr(tmp_path):
    (tmp_path / "guide").mkdir()
    (tmp_path / "guide" / "unit.md").write_text(PROSE)
    (tmp_path / "REQUIREMENTS.md").write_text(REQUIREMENTS)
    outcomes = {}
    for defect, text in (("all-pass-but-reject", STUB.replace("VERDICT: PASS", "VERDICT: REJECT")),
                         ("fail-but-pass", STUB.replace("A2: PASS - ok", "A2: FAIL - hums"))):
        claude = tmp_path / ("claude-" + defect)
        claude.write_text(text)
        claude.chmod(0o755)
        done = subprocess.run([str(SCRIPTS / "grade-prose.sh"), "REQUIREMENTS.md", "guide/unit.md"], cwd=tmp_path,
                              capture_output=True, text=True,
                              env={"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "HOME": str(tmp_path),
                                   "CLAUDE_BIN": str(claude), "STUB_RECORD": str(tmp_path / "record.txt")})
        outcomes[defect] = (done.returncode, "VERDICT" in done.stderr)

    assert outcomes == {"all-pass-but-reject": (2, True), "fail-but-pass": (2, True)}, outcomes


@pytest.mark.process("grade-prose.sh launching a stub claude through supervise.sh")
def test_a_grades_block_with_no_verdict_line_makes_grade_prose_exit_2_and_name_the_missing_verdict_on_stderr(tmp_path):
    (tmp_path / "guide").mkdir()
    (tmp_path / "guide" / "unit.md").write_text(PROSE)
    (tmp_path / "REQUIREMENTS.md").write_text(REQUIREMENTS)
    claude = tmp_path / "claude"
    claude.write_text(STUB.replace("\\nVERDICT: PASS", ""))
    claude.chmod(0o755)

    done = subprocess.run([str(SCRIPTS / "grade-prose.sh"), "REQUIREMENTS.md", "guide/unit.md"], cwd=tmp_path,
                          capture_output=True, text=True,
                          env={"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "HOME": str(tmp_path),
                               "CLAUDE_BIN": str(claude), "STUB_RECORD": str(tmp_path / "record.txt")})

    assert (done.returncode, "VERDICT" in done.stderr) == (2, True), (done.returncode, done.stderr)
