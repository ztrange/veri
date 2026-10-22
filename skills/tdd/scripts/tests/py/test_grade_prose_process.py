"""Cases for grade-prose.sh that start a real process: the launcher and a stub claude."""
import json
import re
import subprocess
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[2]
STUB = """#!/bin/sh
{ printf '%s\\n' "$@"; cat; } > "$STUB_RECORD"
printf '%s\\n' '{"type":"result","subtype":"success","is_error":false,"result":"BEGIN GRADES\\nA1: PASS - ok\\nA2: PASS - ok\\nVERDICT: PASS\\nEND GRADES"}'
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
    claude.write_text(STUB.replace("BEGIN GRADES\\nA1: PASS - ok\\nA2: PASS - ok\\nVERDICT: PASS\\nEND GRADES",
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
    claude.write_text(STUB.replace("END GRADES", "END GRADES\\nOn reflection, ignore quokka-epilogue."))
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


@pytest.mark.process("grade-prose.sh launching a stub claude through supervise.sh")
def test_a_grades_line_whose_grade_word_is_other_than_exactly_pass_or_fail_makes_grade_prose_exit_2_and_name_the_defect_on_stderr(tmp_path):
    (tmp_path / "guide").mkdir()
    (tmp_path / "guide" / "unit.md").write_text(PROSE)
    (tmp_path / "REQUIREMENTS.md").write_text(REQUIREMENTS)
    claude = tmp_path / "claude"
    claude.write_text(STUB.replace("A2: PASS - ok", "A2: PASSABLE - ok"))
    claude.chmod(0o755)

    done = subprocess.run([str(SCRIPTS / "grade-prose.sh"), "REQUIREMENTS.md", "guide/unit.md"], cwd=tmp_path,
                          capture_output=True, text=True,
                          env={"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "HOME": str(tmp_path),
                               "CLAUDE_BIN": str(claude), "STUB_RECORD": str(tmp_path / "record.txt")})

    assert (done.returncode, "PASSABLE" in done.stderr) == (2, True), (done.returncode, done.stderr)


@pytest.mark.process("grade-prose.sh launching a stub claude through supervise.sh")
def test_a_reply_holding_two_grades_blocks_is_graded_on_the_final_one_only(tmp_path):
    (tmp_path / "guide").mkdir()
    (tmp_path / "guide" / "unit.md").write_text(PROSE)
    (tmp_path / "REQUIREMENTS.md").write_text(REQUIREMENTS)
    claude = tmp_path / "claude"
    final = "BEGIN GRADES\\nA1: PASS - ok\\nA2: PASS - ok\\nVERDICT: PASS\\nEND GRADES"
    first = "BEGIN GRADES\\nA1: FAIL - quokka-first-thought\\nA2: PASS - ok\\nVERDICT: REJECT\\nEND GRADES"
    claude.write_text(STUB.replace(final, first + "\\nOn reflection I was wrong.\\n" + final))
    claude.chmod(0o755)

    done = subprocess.run([str(SCRIPTS / "grade-prose.sh"), "REQUIREMENTS.md", "guide/unit.md"], cwd=tmp_path,
                          capture_output=True, text=True,
                          env={"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "HOME": str(tmp_path),
                               "CLAUDE_BIN": str(claude), "STUB_RECORD": str(tmp_path / "record.txt")})

    assert (done.returncode, "quokka-first-thought" in done.stdout) == (0, False), \
        (done.returncode, done.stdout, done.stderr)


@pytest.mark.process("grade-prose.sh launching a hanging stub claude through supervise.sh")
def test_a_grader_leaf_the_supervisor_kills_makes_grade_prose_exit_2_and_name_the_defect_on_stderr(tmp_path):
    (tmp_path / "guide").mkdir()
    (tmp_path / "guide" / "unit.md").write_text(PROSE)
    (tmp_path / "REQUIREMENTS.md").write_text(REQUIREMENTS)
    claude = tmp_path / "claude"
    claude.write_text("#!/bin/sh\nexec sleep 30\n")
    claude.chmod(0o755)

    done = subprocess.run([str(SCRIPTS / "grade-prose.sh"), "REQUIREMENTS.md", "guide/unit.md"], cwd=tmp_path,
                          capture_output=True, text=True, timeout=25,
                          env={"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "HOME": str(tmp_path),
                               "CLAUDE_BIN": str(claude), "VERI_HEARTBEAT": "1", "VERI_TIMEOUT": "2",
                               "VERI_STUCK_RETRIES": "0"})

    assert (done.returncode, "no verdict obtained" in done.stderr) == (2, True), (done.returncode, done.stderr)


@pytest.mark.process("grade-prose.sh launching a claude that cannot start through supervise.sh")
def test_a_grader_leaf_that_fails_to_launch_makes_grade_prose_exit_2_say_no_verdict_was_obtained_and_append_no_event(tmp_path):
    (tmp_path / "guide").mkdir()
    (tmp_path / "guide" / "unit.md").write_text(PROSE)
    (tmp_path / "REQUIREMENTS.md").write_text(REQUIREMENTS)

    done = subprocess.run([str(SCRIPTS / "grade-prose.sh"), "REQUIREMENTS.md", "guide/unit.md"], cwd=tmp_path,
                          capture_output=True, text=True, timeout=25,
                          env={"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "HOME": str(tmp_path),
                               "CLAUDE_BIN": str(tmp_path / "no-such-claude"), "VERI_HEARTBEAT": "1",
                               "VERI_TIMEOUT": "2", "VERI_STUCK_RETRIES": "0"})

    events = tmp_path / ".tdd" / "events.jsonl"
    graded = [l for l in (events.read_text().splitlines() if events.exists() else []) if "guide/unit.md" in l]
    assert (done.returncode, "no verdict obtained" in done.stderr, graded) == (2, True, []), \
        (done.returncode, done.stderr, graded)


@pytest.mark.process("grade-prose.sh launching a stub claude that answers with a usage-limit reply through supervise.sh")
def test_a_usage_limit_reply_from_the_grader_leaf_makes_grade_prose_exit_2_say_no_verdict_was_obtained_and_append_no_event(tmp_path):
    (tmp_path / "guide").mkdir()
    (tmp_path / "guide" / "unit.md").write_text(PROSE)
    (tmp_path / "REQUIREMENTS.md").write_text(REQUIREMENTS)
    claude = tmp_path / "claude"
    claude.write_text("#!/bin/sh\ncat > /dev/null\n"
                      "printf '%s\\n' '{\"type\":\"result\",\"subtype\":\"success\",\"is_error\":true,"
                      "\"result\":\"Claude usage limit reached. Your limit will reset at 5pm.\"}'\n")
    claude.chmod(0o755)

    done = subprocess.run([str(SCRIPTS / "grade-prose.sh"), "REQUIREMENTS.md", "guide/unit.md"], cwd=tmp_path,
                          capture_output=True, text=True, timeout=25,
                          env={"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "HOME": str(tmp_path),
                               "CLAUDE_BIN": str(claude), "VERI_HEARTBEAT": "1", "VERI_TIMEOUT": "2",
                               "VERI_STUCK_RETRIES": "0"})

    events = tmp_path / ".tdd" / "events.jsonl"
    graded = [l for l in (events.read_text().splitlines() if events.exists() else []) if "guide/unit.md" in l]
    assert (done.returncode, "no verdict obtained" in done.stderr, graded) == (2, True, []), \
        (done.returncode, done.stderr, graded)


@pytest.mark.process("grade-prose.sh launching a stub claude through supervise.sh")
def test_every_grading_appends_one_event_to_events_jsonl_carrying_the_unit_the_verdict_and_the_failing_ids(tmp_path):
    (tmp_path / "guide").mkdir()
    (tmp_path / "guide" / "unit.md").write_text(PROSE)
    (tmp_path / "REQUIREMENTS.md").write_text(REQUIREMENTS)
    claude = tmp_path / "claude"
    claude.write_text(STUB.replace("A2: PASS - ok", "A2: FAIL - the widget hums")
                      .replace("VERDICT: PASS", "VERDICT: REJECT"))
    claude.chmod(0o755)
    record = tmp_path / "record.txt"

    subprocess.run([str(SCRIPTS / "grade-prose.sh"), "REQUIREMENTS.md", "guide/unit.md"], cwd=tmp_path,
                   capture_output=True, text=True,
                   env={"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "HOME": str(tmp_path),
                        "CLAUDE_BIN": str(claude), "STUB_RECORD": str(record)})

    events = tmp_path / ".tdd" / "events.jsonl"
    lines = events.read_text().splitlines() if events.exists() else []
    graded = [l for l in lines if "guide/unit.md" in l and "REJECT" in l and "A2" in l and "A1" not in l]
    assert len(graded) == 1, lines


@pytest.mark.process("grade-prose.sh launching a stub claude through supervise.sh")
def test_every_grading_event_records_that_gradings_cost_in_dollars_read_from_the_grader_leafs_own_result(tmp_path):
    (tmp_path / "guide").mkdir()
    (tmp_path / "guide" / "unit.md").write_text(PROSE)
    (tmp_path / "REQUIREMENTS.md").write_text(REQUIREMENTS)
    claude = tmp_path / "claude"
    claude.write_text(STUB.replace('"is_error":false,', '"is_error":false,"total_cost_usd":0.04271,'))
    claude.chmod(0o755)
    record = tmp_path / "record.txt"

    subprocess.run([str(SCRIPTS / "grade-prose.sh"), "REQUIREMENTS.md", "guide/unit.md"], cwd=tmp_path,
                   capture_output=True, text=True,
                   env={"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "HOME": str(tmp_path),
                        "CLAUDE_BIN": str(claude), "STUB_RECORD": str(record)})

    events = tmp_path / ".tdd" / "events.jsonl"
    lines = events.read_text().splitlines() if events.exists() else []
    graded = [l for l in lines if "guide/unit.md" in l and "0.04271" in l]
    assert len(graded) == 1, lines


@pytest.mark.process("grade-prose.sh launching a stub claude through supervise.sh")
def test_1874_a_grader_leaf_that_prints_an_all_pass_block_and_then_exits_1_makes_grade_prose_exit_2_with_no_stdout_and_no_event(tmp_path):
    (tmp_path / "guide").mkdir()
    (tmp_path / "guide" / "unit.md").write_text(PROSE)
    (tmp_path / "REQUIREMENTS.md").write_text(REQUIREMENTS)
    claude = tmp_path / "claude"
    claude.write_text(STUB + "exit 1\n")
    claude.chmod(0o755)
    record = tmp_path / "record.txt"

    done = subprocess.run([str(SCRIPTS / "grade-prose.sh"), "REQUIREMENTS.md", "guide/unit.md"], cwd=tmp_path,
                          capture_output=True, text=True,
                          env={"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "HOME": str(tmp_path),
                               "CLAUDE_BIN": str(claude), "STUB_RECORD": str(record)})

    events = tmp_path / ".tdd" / "events.jsonl"
    lines = events.read_text().splitlines() if events.exists() else []
    graded = [l for l in lines if "guide/unit.md" in l and '"verdict": "PASS"' in l]
    assert (done.returncode, done.stdout, graded) == (2, "", []), (done.stderr, lines)


@pytest.mark.process("grade-prose.sh launching a stub claude through supervise.sh")
def test_1874_a_grader_leaf_whose_reply_carries_a_429_error_alongside_an_all_pass_block_makes_grade_prose_exit_2_with_no_stdout_and_no_event(tmp_path):
    (tmp_path / "guide").mkdir()
    (tmp_path / "guide" / "unit.md").write_text(PROSE)
    (tmp_path / "REQUIREMENTS.md").write_text(REQUIREMENTS)
    claude = tmp_path / "claude"
    claude.write_text(STUB.replace(
        "printf '%s\\n' '{\"type\":\"result\"",
        "printf '%s\\n' '{\"type\":\"assistant\",\"error\":\"rate_limit\",\"message\":{\"content\":"
        "[{\"type\":\"text\",\"text\":\"API Error: 429 rate_limit_error\"}]}}'\n"
        "printf '%s\\n' '{\"type\":\"result\"", 1) + "exit 1\n")
    claude.chmod(0o755)
    record = tmp_path / "record.txt"

    done = subprocess.run([str(SCRIPTS / "grade-prose.sh"), "REQUIREMENTS.md", "guide/unit.md"], cwd=tmp_path,
                          capture_output=True, text=True,
                          env={"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "HOME": str(tmp_path),
                               "CLAUDE_BIN": str(claude), "STUB_RECORD": str(record)})

    events = tmp_path / ".tdd" / "events.jsonl"
    lines = events.read_text().splitlines() if events.exists() else []
    graded = [l for l in lines if "guide/unit.md" in l and '"verdict": "PASS"' in l]
    log = (tmp_path / ".tdd" / "grade-prose.log").read_text()
    assert ("API Error: 429" in log, "A2: PASS" in log) == (True, True), log
    assert (done.returncode, done.stdout, graded) == (2, "", []), (done.stderr, lines)


@pytest.mark.process("grade-prose.sh launching a real supervise.sh that refuses")
def test_1874_a_launch_supervise_refuses_with_a_stale_all_pass_log_on_disk_makes_grade_prose_exit_2_with_no_stdout_and_no_event(tmp_path):
    (tmp_path / "guide").mkdir()
    (tmp_path / "guide" / "unit.md").write_text(PROSE)
    (tmp_path / "REQUIREMENTS.md").write_text(REQUIREMENTS)
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "grade-prose.log").write_text(
        '{"type":"result","subtype":"success","is_error":false,"result":'
        '"BEGIN GRADES\\nA1: PASS - ok\\nA2: PASS - ok\\nVERDICT: PASS\\nEND GRADES"}\n')
    claude = tmp_path / "claude"
    claude.write_text(STUB)
    claude.chmod(0o755)
    record = tmp_path / "record.txt"

    done = subprocess.run([str(SCRIPTS / "grade-prose.sh"), "REQUIREMENTS.md", "guide/unit.md"], cwd=tmp_path,
                          capture_output=True, text=True,
                          env={"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "HOME": str(tmp_path),
                               "CLAUDE_BIN": str(claude), "STUB_RECORD": str(record), "VERI_HEARTBEAT": "abc"})

    events = tmp_path / ".tdd" / "events.jsonl"
    lines = events.read_text().splitlines() if events.exists() else []
    graded = [l for l in lines if "guide/unit.md" in l and '"verdict": "PASS"' in l]
    assert (done.returncode, done.stdout, graded) == (2, "", []), (done.stderr, lines)


@pytest.mark.process("grade-prose.sh launching a stub claude through supervise.sh")
def test_1874_a_reply_in_the_poc_shape_with_the_verdict_line_inside_the_grades_block_exits_0_when_all_pass_and_1_printing_the_failing_line_on_a_fail(tmp_path):
    (tmp_path / "guide").mkdir()
    (tmp_path / "guide" / "unit.md").write_text(PROSE)
    (tmp_path / "REQUIREMENTS.md").write_text(REQUIREMENTS)
    inside = STUB.replace("\\nEND GRADES\\nVERDICT: PASS", "\\nVERDICT: PASS\\nEND GRADES")
    shapes = {"all-pass": inside,
              "one-fail": inside.replace("A2: PASS - ok", "A2: FAIL - the widget hums quokka-loudly")
                                .replace("VERDICT: PASS", "VERDICT: REJECT")}
    outcomes = {}
    for name, stub in shapes.items():
        claude = tmp_path / ("claude-" + name)
        claude.write_text(stub)
        claude.chmod(0o755)
        done = subprocess.run([str(SCRIPTS / "grade-prose.sh"), "REQUIREMENTS.md", "guide/unit.md"], cwd=tmp_path,
                              capture_output=True, text=True,
                              env={"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "HOME": str(tmp_path),
                                   "CLAUDE_BIN": str(claude), "STUB_RECORD": str(tmp_path / "record.txt")})
        outcomes[name] = (done.returncode, "the widget hums quokka-loudly" in done.stdout)

    assert outcomes == {"all-pass": (0, False), "one-fail": (1, True)}, outcomes


@pytest.mark.process("grade-prose.sh launching a stub claude through supervise.sh")
def test_1874_a_reply_with_verdict_lines_after_end_grades_makes_grade_prose_exit_2_and_append_no_grading_event(tmp_path):
    (tmp_path / "guide").mkdir()
    (tmp_path / "guide" / "unit.md").write_text(PROSE)
    (tmp_path / "REQUIREMENTS.md").write_text(REQUIREMENTS)
    claude = tmp_path / "claude"
    claude.write_text(STUB.replace("END GRADES", "END GRADES\\nVERDICT: REJECT\\nVERDICT: PASS"))
    claude.chmod(0o755)

    done = subprocess.run([str(SCRIPTS / "grade-prose.sh"), "REQUIREMENTS.md", "guide/unit.md"], cwd=tmp_path,
                          capture_output=True, text=True,
                          env={"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "HOME": str(tmp_path),
                               "CLAUDE_BIN": str(claude), "STUB_RECORD": str(tmp_path / "record.txt")})

    events = tmp_path / ".tdd" / "events.jsonl"
    graded = [l for l in (events.read_text().splitlines() if events.exists() else []) if '"grading"' in l]
    assert (done.returncode, graded) == (2, []), (done.returncode, done.stdout, done.stderr, graded)


@pytest.mark.process("grade-prose.sh launching a stub claude through supervise.sh")
def test_1874_the_grader_leaf_is_launched_with_no_tools_the_stub_claude_receives_tools_with_an_empty_value(tmp_path):
    (tmp_path / "guide").mkdir()
    (tmp_path / "guide" / "unit.md").write_text(PROSE)
    (tmp_path / "REQUIREMENTS.md").write_text(REQUIREMENTS)
    claude = tmp_path / "claude"
    claude.write_text(STUB)
    claude.chmod(0o755)
    record = tmp_path / "record.txt"

    subprocess.run([str(SCRIPTS / "grade-prose.sh"), "REQUIREMENTS.md", "guide/unit.md"], cwd=tmp_path,
                   capture_output=True, text=True,
                   env={"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "HOME": str(tmp_path),
                        "CLAUDE_BIN": str(claude), "STUB_RECORD": str(record)})

    argv = (record.read_text() if record.exists() else "").split("\n")
    following = argv[argv.index("--tools") + 1] if "--tools" in argv else None
    assert following == "", ("--tools" in argv, following, argv[:30])


@pytest.mark.process("grade-prose.sh launching a stub claude through supervise.sh")
def test_1874_the_stub_claude_receives_grader_conf_model_when_veri_model_grader_is_set_in_the_environment(tmp_path):
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
                                             "VERI_MODEL_GRADER": "env-model-narwhal"})

    args = (record.read_text() if record.exists() else "").splitlines()
    given = args[args.index("--model") + 1] if "--model" in args else None
    assert committed and given == committed, (given, committed)


@pytest.mark.process("grade-prose.sh launching a stub claude through supervise.sh")
def test_a_full_pass_writes_one_graded_line_carrying_the_unit_its_signature_the_date_and_the_grading_events_id(tmp_path, monkeypatch):
    from veri import grade_prose

    (tmp_path / "skills" / "guide").mkdir(parents=True)
    (tmp_path / "skills" / "guide" / "unit.md").write_text(PROSE)
    (tmp_path / "REQUIREMENTS.md").write_text(REQUIREMENTS.replace("## guide/unit.md", "## skills/guide/unit.md"))
    claude = tmp_path / "claude"
    claude.write_text(STUB)
    claude.chmod(0o755)
    record = tmp_path / "record.txt"

    subprocess.run([str(SCRIPTS / "grade-prose.sh"), "REQUIREMENTS.md", "skills/guide/unit.md"], cwd=tmp_path,
                   capture_output=True, text=True,
                   env={"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "HOME": str(tmp_path),
                        "CLAUDE_BIN": str(claude), "STUB_RECORD": str(record)})

    events = tmp_path / ".tdd" / "events.jsonl"
    gradings = [json.loads(l) for l in (events.read_text().splitlines() if events.exists() else [])
                if '"grading"' in l]
    graded = tmp_path / "skills" / "guide" / "GRADED"
    lines = graded.read_text().splitlines() if graded.exists() else []
    fields = lines[0].split() if len(lines) == 1 else []
    monkeypatch.chdir(tmp_path)
    expected = grade_prose.signature("REQUIREMENTS.md", "skills/guide/unit.md")
    assert [len(gradings), len(fields) == 4 and fields[0], len(fields) == 4 and fields[1] == expected,
            len(fields) == 4 and bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", fields[2])),
            len(fields) == 4 and fields[3] == gradings[0].get("id", "") != ""] \
        == [1, "skills/guide/unit.md", True, True, True], lines


@pytest.mark.process("grade-prose.sh launching a stub claude through supervise.sh")
def test_a_pass_replaces_any_earlier_graded_line_for_the_same_unit_and_leaves_other_units_lines_as_they_were(tmp_path):
    (tmp_path / "skills" / "guide").mkdir(parents=True)
    (tmp_path / "skills" / "guide" / "unit.md").write_text(PROSE)
    (tmp_path / "REQUIREMENTS.md").write_text(REQUIREMENTS.replace("## guide/unit.md", "## skills/guide/unit.md"))
    other = "skills/guide/other.md " + "b" * 64 + " 2026-01-02 deadbeef"
    old = "skills/guide/unit.md " + "a" * 64 + " 2026-01-01 cafef00d"
    graded = tmp_path / "skills" / "guide" / "GRADED"
    graded.write_text(other + "\n" + old + "\n")
    claude = tmp_path / "claude"
    claude.write_text(STUB)
    claude.chmod(0o755)
    record = tmp_path / "record.txt"

    subprocess.run([str(SCRIPTS / "grade-prose.sh"), "REQUIREMENTS.md", "skills/guide/unit.md"], cwd=tmp_path,
                   capture_output=True, text=True,
                   env={"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "HOME": str(tmp_path),
                        "CLAUDE_BIN": str(claude), "STUB_RECORD": str(record)})

    lines = graded.read_text().splitlines()
    mine = [l for l in lines if l.startswith("skills/guide/unit.md ")]
    assert [lines.count(other), len(mine), old in lines, len(lines)] == [1, 1, False, 2], lines


@pytest.mark.process("grade-prose.sh launching a stub claude through supervise.sh")
def test_a_reject_and_an_exit_2_leave_graded_byte_identical(tmp_path):
    (tmp_path / "skills" / "guide").mkdir(parents=True)
    (tmp_path / "skills" / "guide" / "unit.md").write_text(PROSE)
    (tmp_path / "REQUIREMENTS.md").write_text(REQUIREMENTS.replace("## guide/unit.md", "## skills/guide/unit.md"))
    graded = tmp_path / "skills" / "guide" / "GRADED"
    before = "skills/guide/other.md " + "b" * 64 + " 2026-01-02 deadbeef\nskills/guide/unit.md " + "a" * 64 + " 2026-01-01 cafef00d\n"
    graded.write_text(before)
    record = tmp_path / "record.txt"
    replies = {"reject": STUB.replace("A2: PASS - ok", "A2: FAIL - hums").replace("VERDICT: PASS", "VERDICT: REJECT"),
               "no verdict": STUB.replace("BEGIN GRADES\\nA1: PASS - ok\\nA2: PASS - ok\\nVERDICT: PASS\\nEND GRADES", "looks fine")}
    seen = {}
    for name, body in replies.items():
        claude = tmp_path / "claude"
        claude.write_text(body)
        claude.chmod(0o755)
        done = subprocess.run([str(SCRIPTS / "grade-prose.sh"), "REQUIREMENTS.md", "skills/guide/unit.md"], cwd=tmp_path,
                              capture_output=True, text=True,
                              env={"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "HOME": str(tmp_path),
                                   "CLAUDE_BIN": str(claude), "STUB_RECORD": str(record)})
        seen[name] = (done.returncode, graded.read_text() == before)

    assert seen == {"reject": (1, True), "no verdict": (2, True)}, seen


@pytest.mark.process("grade-prose.sh --owed launching a stub claude through supervise.sh")
def test_grade_prose_owed_grades_exactly_the_non_orphan_units_prose_owed_prints_and_no_others(tmp_path):
    skill = tmp_path / "skills" / "guide"
    skill.mkdir(parents=True)
    for name in ("one", "two"):
        (skill / (name + ".md")).write_text(PROSE)
    (skill / "GRADED").write_text("skills/guide/gone.md %s 2026-01-01 abc\n" % ("0" * 64))
    (tmp_path / "REQUIREMENTS.md").write_text(
        REQUIREMENTS.replace("## guide/unit.md", "## skills/guide/one.md") + "\n"
        + REQUIREMENTS.replace("## guide/unit.md", "## skills/guide/two.md"))
    claude = tmp_path / "claude"
    claude.write_text(STUB.replace('{ printf \'%s\\n\' "$@"; cat; } > "$STUB_RECORD"',
                                   '{ printf \'%s\\n\' "$@"; cat; } >> "$STUB_RECORD"'))
    claude.chmod(0o755)
    record = tmp_path / "record.txt"

    subprocess.run([str(SCRIPTS / "grade-prose.sh"), "--owed"], cwd=tmp_path, capture_output=True,
                   env={"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "HOME": str(tmp_path),
                        "CLAUDE_BIN": str(claude), "STUB_RECORD": str(record)})

    received = record.read_text() if record.exists() else ""
    assert re.findall(r"^Unit: (\S+)$", received, re.M) == ["skills/guide/one.md", "skills/guide/two.md"], received


@pytest.mark.process("grade-prose.sh --owed launching a stub claude through supervise.sh")
def test_grade_prose_owed_grades_the_owed_unit_and_neither_the_unit_whose_signature_is_current_nor_the_orphan_1725(
        tmp_path, monkeypatch):
    from veri import grade_prose

    skill = tmp_path / "skills" / "guide"
    skill.mkdir(parents=True)
    for name in ("owed", "current"):
        (skill / (name + ".md")).write_text(PROSE)
    (tmp_path / "REQUIREMENTS.md").write_text(
        REQUIREMENTS.replace("## guide/unit.md", "## skills/guide/owed.md") + "\n"
        + REQUIREMENTS.replace("## guide/unit.md", "## skills/guide/current.md"))
    monkeypatch.chdir(tmp_path)
    current = grade_prose.signature("REQUIREMENTS.md", "skills/guide/current.md")
    (skill / "GRADED").write_text("skills/guide/current.md %s 2026-01-01 g1\nskills/guide/gone.md %s 2026-01-01 g2\n"
                                  % (current, current))
    claude = tmp_path / "claude"
    claude.write_text(STUB.replace('{ printf \'%s\\n\' "$@"; cat; } > "$STUB_RECORD"',
                                   '{ printf \'%s\\n\' "$@"; cat; } >> "$STUB_RECORD"'))
    claude.chmod(0o755)
    record = tmp_path / "record.txt"

    ran = subprocess.run([str(SCRIPTS / "grade-prose.sh"), "--owed"], cwd=tmp_path, capture_output=True, text=True,
                         env={"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "HOME": str(tmp_path),
                              "CLAUDE_BIN": str(claude), "STUB_RECORD": str(record)})

    received = record.read_text() if record.exists() else ""
    assert (ran.returncode, re.findall(r"^Unit: (\S+)$", received, re.M)) == (0, ["skills/guide/owed.md"]), ran.stderr


@pytest.mark.process("grade-prose.sh launching a stub claude through supervise.sh")
def test_a_graded_run_exits_0_and_prints_no_leaf_role_line_on_stderr_1887(tmp_path):
    (tmp_path / "guide").mkdir()
    (tmp_path / "guide" / "unit.md").write_text(PROSE)
    (tmp_path / "REQUIREMENTS.md").write_text(REQUIREMENTS)
    claude = tmp_path / "claude"
    claude.write_text("#!/bin/sh\ncat > /dev/null\n"
                      "printf '%s\\n' '{\"type\":\"result\",\"subtype\":\"success\",\"is_error\":false,"
                      "\"result\":\"BEGIN GRADES\\nA1: PASS - ok\\nA2: PASS - ok\\nVERDICT: PASS\\nEND GRADES\","
                      "\"duration_ms\":10,\"duration_api_ms\":8,\"num_turns\":1,\"total_cost_usd\":0.01,"
                      "\"usage\":{\"input_tokens\":1,\"output_tokens\":2,"
                      "\"cache_read_input_tokens\":3,\"cache_creation_input_tokens\":4}}'\n")
    claude.chmod(0o755)

    done = subprocess.run([str(SCRIPTS / "grade-prose.sh"), "REQUIREMENTS.md", "guide/unit.md"], cwd=tmp_path,
                          capture_output=True, text=True,
                          env={"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "HOME": str(tmp_path),
                               "CLAUDE_BIN": str(claude)})

    assert (done.returncode, "leaf-role" in done.stderr) == (0, False), (done.returncode, done.stderr)


@pytest.mark.process("the SKILL.md regrade block run in a git repo with a stub claude through supervise.sh")
def test_2037_the_draft_pr_regrade_block_run_as_written_on_a_branch_that_signed_one_unit_exits_0(tmp_path):
    skill = (SCRIPTS.parents[2] / "skills" / "tdd" / "SKILL.md").read_text()
    draft = skill[skill.index("regrade every unit the run signed"):]
    block = re.search(r"```\n(.*?)```", draft, re.S).group(1).replace("<default>", "main")
    env = {"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "HOME": str(tmp_path),
           "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}

    def git(*argv):
        subprocess.run(["git", *argv], cwd=tmp_path, env=env, check=True, capture_output=True)

    git("init", "-q", "-b", "main")
    git("commit", "-q", "--allow-empty", "-m", "base")
    git("update-ref", "refs/remotes/origin/main", "HEAD")
    git("checkout", "-q", "-b", "work")
    (tmp_path / "guide").mkdir()
    (tmp_path / "guide" / "unit.md").write_text(PROSE)
    (tmp_path / "guide" / "REQUIREMENTS.md").write_text(REQUIREMENTS.replace("## guide/unit.md", "## guide/unit.md", 1))
    (tmp_path / "guide" / "GRADED").write_text("guide/unit.md 0 2026-01-01 id\n")
    git("add", ".")
    git("commit", "-q", "-m", "sign one unit")
    claude = tmp_path / "claude"
    claude.write_text(STUB)
    claude.chmod(0o755)

    ran = subprocess.run(["bash", "-c", block], cwd=tmp_path, capture_output=True, text=True,
                         env={**env, "S": str(SCRIPTS), "CLAUDE_BIN": str(claude),
                              "STUB_RECORD": str(tmp_path / "record.txt")})

    record = tmp_path / "record.txt"
    graded = re.findall(r"^Unit: (\S+)$", record.read_text(), re.M) if record.exists() else []
    assert (ran.returncode, graded) == (0, ["guide/unit.md"]), ran.stdout + ran.stderr


REJECT_THEN_PASS_STUB = """#!/bin/sh
{ printf '%s\\n' "$@"; cat; } > "$STUB_DIR/in.$$"
grep '^Unit: ' "$STUB_DIR/in.$$" >> "$STUB_DIR/graded.txt"
if [ "$(wc -l < "$STUB_DIR/graded.txt")" -eq 1 ]; then
  printf '%s\\n' '{"type":"result","subtype":"success","is_error":false,"result":"BEGIN GRADES\\nA1: FAIL - no\\nA2: PASS - ok\\nVERDICT: REJECT\\nEND GRADES"}'
else
  printf '%s\\n' '{"type":"result","subtype":"success","is_error":false,"result":"BEGIN GRADES\\nA1: PASS - ok\\nA2: PASS - ok\\nVERDICT: PASS\\nEND GRADES"}'
fi
"""


@pytest.mark.process("the SKILL.md regrade block run in a git repo with a stub claude through supervise.sh")
def test_2037_the_draft_pr_regrade_block_run_as_written_on_two_signed_units_with_the_first_rejected_exits_non_zero_after_grading_both(tmp_path):
    skill = (SCRIPTS.parents[2] / "skills" / "tdd" / "SKILL.md").read_text()
    draft = skill[skill.index("regrade every unit the run signed"):]
    block = re.search(r"```\n(.*?)```", draft, re.S).group(1).replace("<default>", "main")
    env = {"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "HOME": str(tmp_path),
           "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}

    def git(*argv):
        subprocess.run(["git", *argv], cwd=tmp_path, env=env, check=True, capture_output=True)

    git("init", "-q", "-b", "main")
    git("commit", "-q", "--allow-empty", "-m", "base")
    git("update-ref", "refs/remotes/origin/main", "HEAD")
    git("checkout", "-q", "-b", "work")
    for directory, name in (("alpha", "one.md"), ("beta", "two.md")):
        (tmp_path / directory).mkdir()
        unit = f"{directory}/{name}"
        (tmp_path / unit).write_text(PROSE)
        (tmp_path / directory / "REQUIREMENTS.md").write_text(REQUIREMENTS.replace("guide/unit.md", unit))
        (tmp_path / directory / "GRADED").write_text(f"{unit} 0 2026-01-01 id\n")
    git("add", ".")
    git("commit", "-q", "-m", "sign two units")
    stub_dir = tmp_path / "stub"
    stub_dir.mkdir()
    claude = tmp_path / "claude"
    claude.write_text(REJECT_THEN_PASS_STUB)
    claude.chmod(0o755)

    ran = subprocess.run(["bash", "-c", block], cwd=tmp_path, capture_output=True, text=True,
                         env={**env, "S": str(SCRIPTS), "CLAUDE_BIN": str(claude), "STUB_DIR": str(stub_dir)})

    graded_file = stub_dir / "graded.txt"
    graded = re.findall(r"^Unit: (\S+)$", graded_file.read_text(), re.M) if graded_file.exists() else []
    assert (ran.returncode != 0, sorted(graded)) == (True, ["alpha/one.md", "beta/two.md"]), (
        ran.returncode, graded, ran.stdout + ran.stderr)
