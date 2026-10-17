"""Cases for where the /tdd-candidates skill ships, what it calls itself, and what it says its job is."""
import re

from conftest import ROOT

SKILL_DIR = "skills/tdd-candidates"
WANT_NAME = "tdd-candidates"
SKILL_MD = f"{SKILL_DIR}/SKILL.md"
NOT_FILED = "(not|never|nothing)[^.]{0,20}files?"
PAGED_LOOKUP = "gh api --paginate[^.]{0,80}/issues"


def read_bytes_as_text(path):
    return (ROOT / path).read_bytes().decode("latin-1")


def ascii_lower(text):
    return text.translate({code: code + 32 for code in range(ord("A"), ord("Z") + 1)})


def frontmatter_name(path):
    lines = read_bytes_as_text(path).splitlines()
    if not lines or lines[0] != "---":
        return ""
    for line in lines[1:]:
        if line == "---":
            return ""
        if line.startswith("name:"):
            return line[len("name:"):].lstrip(" \t")
    return ""


def body_text(path):
    out, inside, body = [], False, False
    for number, line in enumerate(read_bytes_as_text(path).splitlines(), 1):
        if number == 1 and line == "---":
            inside = True
        elif inside and line == "---":
            inside, body = False, True
        elif body:
            out.append(line)
    text = "".join(line + "\n" for line in out)
    return ascii_lower(text.replace("*", "").replace("`", "")).replace("\n", " ")


def says(problems, text, pattern, message):
    if not re.search(pattern, text):
        problems.append(message)


def says_near(problems, text, first, second, window, message):
    says(problems, text, f"{first}[^.]{{0,{window}}}{second}|{second}[^.]{{0,{window}}}{first}", message)


def has_skill_md(problems):
    if (ROOT / SKILL_MD).is_file():
        return True
    problems.append(f"want a SKILL.md at {SKILL_MD}, found none")
    return False


def skill_text():
    return body_text(SKILL_MD) if (ROOT / SKILL_MD).is_file() else ""


def test_skill_md_is_the_tdd_candidates_skill_and_says_it_shapes_and_files_candidates_without_surveying_ranking_or_judging_them():
    problems = []
    text = skill_text()
    if not (ROOT / SKILL_DIR).is_dir():
        problems.append(f"want a directory at {SKILL_DIR}, found none")
    if has_skill_md(problems):
        got = frontmatter_name(SKILL_MD)
        if got != WANT_NAME:
            problems.append(f"{SKILL_MD} frontmatter: want name '{WANT_NAME}', got {got!r}")
        if not text.replace(" ", ""):
            problems.append(f"{SKILL_MD} has no body after its frontmatter — its scope could not be read")
        else:
            says(problems, text, r"shapes?[^.]{0,80}files?[^.]{0,80}candidates?|candidates?[^.]{0,80}shapes?[^.]{0,80}files?",
                 f"{SKILL_MD} never says it shapes and files candidates")
            says(problems, text, r"(not|never|no)[^.]{0,40}survey", f"{SKILL_MD} never says it does not survey")
            says(problems, text, r"(not|never|no)[^.]{0,60}rank", f"{SKILL_MD} never says it does not rank")
            says(problems, text, r"(not|never|no)[^.]{0,80}judge", f"{SKILL_MD} never says it does not judge")
    assert not problems, "\n".join(problems)


def test_skill_md_files_one_issue_per_module_from_conversation_candidates_criteria_as_predicates_with_a_runnable_check():
    problems = []
    text = skill_text()
    if has_skill_md(problems):
        says_near(problems, text, "candidates?", "conversation", 120,
                  f"{SKILL_MD} never says it takes the candidates from the conversation")
        says(problems, text, r"gh issue create", f"{SKILL_MD} never says how an issue is filed (gh issue create)")
        says(problems, text, r"one (github )?issue per module", f"{SKILL_MD} never says it files one issue per module")
        says(problems, text, r"(not|never)[^.]{0,40}(one )?(issue )?per smell",
             f"{SKILL_MD} never says it does not file one issue per smell")
        says_near(problems, text, "acceptance criteri(on|a)", "predicates?", 120,
                  f"{SKILL_MD} never says the acceptance criteria are phrased as predicates")
        says(problems, text, r"structural predicates?", f"{SKILL_MD} never says the predicates are structural")
        says_near(problems, text, "runnable check", "where one exists", 80,
                  f"{SKILL_MD} never says each predicate carries a runnable check where one exists")
    assert not problems, "\n".join(problems)


def test_skill_md_reads_the_candidates_from_the_analysis_html_report_path_and_files_the_same_issues():
    problems = []
    text = skill_text()
    if has_skill_md(problems):
        says_near(problems, text, "path", "html report", 80,
                  f"{SKILL_MD} never says it accepts the path to the analysis's HTML report")
        says(problems, text, r"reads?[^.]{0,60}candidates?[^.]{0,60}(report|file)|candidates?[^.]{0,40}from (the|that) (html )?(report|file)",
             f"{SKILL_MD} never says it reads the candidates from that file")
        says(problems, text, r"same issues?",
             f"{SKILL_MD} never says it files the same issues it would have filed from the conversation")
    assert not problems, "\n".join(problems)


def test_skill_md_ends_every_issue_with_a_final_test_command_line_and_lists_only_real_blockers_under_blocked_by():
    problems = []
    text = skill_text()
    if has_skill_md(problems):
        says(problems, text, r"(ends?|final|last)[^.]{0,80}test command:|test command:[^.]{0,80}(final|last) line",
             f"{SKILL_MD} never says each issue ends with a final Test command: line")
        says(problems, text, r"## blocked by", f"{SKILL_MD} never says the issue carries a ## Blocked by section")
        says(problems, text, r"only real blockers?|real blockers? only",
             f"{SKILL_MD} never says it lists only real blockers there")
    assert not problems, "\n".join(problems)


def test_skill_md_files_nothing_for_a_candidate_with_no_checkable_predicate_and_says_which_it_skipped_and_why():
    problems = []
    text = skill_text()
    if has_skill_md(problems):
        says(problems, text, r"(no|without)[^.]{0,40}checkable predicates?",
             f"{SKILL_MD} never names a candidate with no checkable predicate")
        says_near(problems, text, "checkable predicates?", NOT_FILED, 120,
                  f"{SKILL_MD} never says a candidate with no checkable predicate is not filed")
        says(problems, text, r"(names?|says?|which)[^.]{0,80}skipped|skipped[^.]{0,80}(by name|which)",
             f"{SKILL_MD} never says it names which candidate it skipped")
        says_near(problems, text, "skipped", "(why|reason)", 120, f"{SKILL_MD} never says why a candidate was skipped")
    assert not problems, "\n".join(problems)


def test_skill_md_looks_for_an_issue_it_already_filed_for_a_candidate_and_files_no_duplicate_on_a_re_run():
    problems = []
    text = skill_text()
    if has_skill_md(problems):
        says_near(problems, text, "(re-?runs?|again|second (run|pass))", "duplicates?", 120,
                  f"{SKILL_MD} never says a re-run files no duplicate")
        says_near(problems, text, "(already filed|already exists?|existing issue)", NOT_FILED, 120,
                  f"{SKILL_MD} never says a candidate whose issue already exists is not filed again")
    assert not problems, "\n".join(problems)


def test_skill_md_recognises_an_already_filed_candidate_by_a_marker_in_the_issue_body_not_by_its_title():
    problems = []
    text = skill_text()
    if has_skill_md(problems):
        says_near(problems, text, "(marker|identifier)", "body", 120,
                  f"{SKILL_MD} never says each filed issue carries an identity marker in its body")
        says_near(problems, text, "(search|look|find|match)[a-z]*", "(marker|identifier)", 120,
                  f"{SKILL_MD} never says the re-run looks for that marker")
        says_near(problems, text, "(not|never)[^.]{0,40}(depend|rely|rest)[a-z]*", "title", 80,
                  f"{SKILL_MD} never says the already-filed check does not depend on the issue title")
    assert not problems, "\n".join(problems)


def test_skill_md_finds_an_already_filed_marker_however_many_issues_the_repository_holds():
    problems = []
    text = skill_text()
    if has_skill_md(problems):
        capped = re.search(r"--limit[ \t\n\r\f\v=]+[0-9]+", text)
        if capped:
            problems.append(f"{SKILL_MD} caps the already-filed lookup at a fixed count: {capped.group(0)}")
        says(problems, text, PAGED_LOOKUP,
             f"{SKILL_MD} never lists the existing issues page by page, uncapped (gh api --paginate over the issues endpoint)")
        says(problems, text, r"(however many|no matter how many|regardless of how many)[^.]{0,40}issues?",
             f"{SKILL_MD} never says the lookup finds the marker however many issues the repository holds")
    assert not problems, "\n".join(problems)
