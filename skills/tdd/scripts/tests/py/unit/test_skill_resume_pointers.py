"""Case for the pointers skills/tdd/SKILL.md carries to RESUME.md, read as text."""
import pathlib
import re

SKILL = pathlib.Path(__file__).resolve().parents[4] / "SKILL.md"
TDD = SKILL.parent
CORE = [TDD / name for name in ("SKILL.md", "SCRIPTS.md", "BAIL.md", "STOPPING.md", "RECONCILE.md")]
NAMING_FILES = CORE + [TDD / "scripts" / "solvable-issues.sh"]

POINTER = "<base directory>/RESUME.md"
NAMES_RESUME = re.compile(r"\bResume\b(?!\.\*\*| check)")


def _lines(path):
    return path.read_text().split("\n")


def _reads_it(lines, pattern):
    """Index of the line matching pattern whose own text or previous line says `Read`."""
    hits = [n for n, line in enumerate(lines) if re.search(pattern, line)]
    assert hits, f"no line matches {pattern!r} in SKILL.md"
    return [n for n in hits if POINTER in lines[n] and "`Read`" in lines[n - 1] + " " + lines[n]]


def test_resume_pointers_name_resume_md_in_the_base_directory():
    lines = _lines(SKILL)
    assert _reads_it(lines, r"RESUME\.md` sub-step 2"), \
        "Draft PR sub-step 1 carries no `Read` pointer naming " + POINTER

    for path in CORE:
        for n, line in enumerate(_lines(path), 1):
            if "RESUME.md" in line:
                assert "VERI_SKILL_CLONE" not in line and "~/.claude/skills" not in line, \
                    f"{path.name}:{n} points RESUME.md outside the base directory"

    for path in NAMING_FILES:
        for n, line in enumerate(_lines(path), 1):
            if NAMES_RESUME.search(line):
                assert "RESUME.md" in line, f"{path.name}:{n} names Resume without naming RESUME.md"


def test_resume_section_lives_in_resume_md_and_skill_md_carries_none_of_its_lines():
    moved = [r"\$S/event\.sh resume`", r"left=\$\(\( \$\{VERI_REFACTOR_BUDGET:-5\} - count \)\)",
             r"add-ledger-step\.sh --planned --criterion"]
    skill = _lines(SKILL)
    resume = _lines(TDD / "RESUME.md")
    assert "## Resume" not in skill, "SKILL.md still carries the ## Resume heading"
    assert "## Resume" in resume, "RESUME.md carries no ## Resume heading"
    left = [p for p in moved if any(re.search(p, line) for line in skill)]
    assert not left, f"SKILL.md still carries the moved lines {left}"
    missing = [p for p in moved if not any(re.search(p, line) for line in resume)]
    assert not missing, f"RESUME.md lacks the moved lines {missing}"


def test_1967_preflight_step_3_resumed_run_block_is_one_resume_clean_sh_call_and_its_exit_2_bails_as_a_system_failure():
    text = SKILL.read_text()
    start = text.index("A resumed run — one whose worktree")
    end = text.index("Then the resumed run, its uncommitted", start)
    prose = text[start:end]
    fences = re.findall(r"```\n(.*?)```", prose, re.S)
    assert len(fences) == 1, f"the resumed-run block holds {len(fences)} code fences, want 1"
    code = [line.strip() for line in fences[0].splitlines() if line.strip()]
    assert len(code) == 1 and "$S/resume-clean.sh" in code[0], f"the block is not one $S/resume-clean.sh call: {code}"
    for syntax in ("[[", "<<<", "<("):
        assert syntax not in prose, f"the resumed-run block still holds bash-only {syntax!r}"
    assert re.search(r"exit 2.*?bails as a \*\*system\*\* failure", " ".join(prose.split())), \
        "the resumed-run block does not bail its exit 2 as a system failure"


def test_resume_md_runs_record_existing_before_the_first_ledger_commit_issue_2213():
    text = " ".join((TDD / "RESUME.md").read_text().split())
    assert re.search(
        r"step lines beyond its plan commit and there is no `\.tdd/issue-<n>-added\.md`, "
        r"run `\$S/ledger-growth\.sh record-existing \.tdd/issue-<n>\.md` once, "
        r"before the resume's first ledger commit, "
        r"and stage `\.tdd/issue-<n>-added\.md` in that same commit with the ledger",
        text), "RESUME.md does not instruct ledger-growth.sh record-existing before the first ledger commit"
    record = text.index("ledger-growth.sh record-existing")
    assert record < text.index("2. **Use the reset preflight already made"), \
        "RESUME.md asks for record-existing after sub-step 2, whose refactor clear can be the resume's first ledger commit"
