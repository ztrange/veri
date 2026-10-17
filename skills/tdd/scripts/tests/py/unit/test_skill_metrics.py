"""Cases for what skills/tdd/SKILL.md tells the conductor to do with the run's metrics report, read as text."""
import importlib
import pathlib
import re

SKILL = pathlib.Path(__file__).resolve().parents[4] / "SKILL.md"

DRAFT_PR = "### 4. Draft PR"
BAILING = "## Bailing"

PR_READ = "pulls?head="
PR_EDIT = "gh api -X PATCH"
METRICS_COMMIT = 'git commit -m "metrics:'
RENDER = "metrics.sh <n> > .tdd/issue-<n>-metrics.md"

_UPPER = {c: c + 32 for c in range(ord("A"), ord("Z") + 1)}


def _lower(text):
    return text.translate(_UPPER)


def _section_lines(heading):
    section = importlib.import_module("skill_sections").section(SKILL, heading)
    return section.splitlines()[1:]


def _records(lines):
    out, rec = [], ""
    for line in lines:
        if re.match(r"[0-9]+\. ", line) or re.match(r"\s*- ", line):
            if rec:
                out.append(rec)
            rec = line
        elif not line.strip():
            if rec:
                out.append(rec)
            rec = ""
        elif not rec:
            rec = line
        else:
            rec = rec + " " + line
    if rec:
        out.append(rec)
    return [_lower(re.sub(r"\s+", " ", r)) for r in out]


def _first_record(records, *needles):
    return next((n for n, r in enumerate(records, 1) if all(s in r for s in needles)), None)


def _fenced(heading):
    all_lines = SKILL.read_text().splitlines()
    start = all_lines.index(heading) + 1
    out, fence = [], False
    for offset, line in enumerate(_section_lines(heading), 1):
        if re.match(r"\s*```", line):
            fence = not fence
        elif fence:
            out.append((start + offset, line))
    return out


def _first_fenced(needle):
    return next((n for n, text in _fenced(DRAFT_PR) if needle in text), None)


def _offset(text, needle):
    at = text.find(needle)
    return at if at >= 0 else None


def _pr_records():
    return _records(_section_lines(DRAFT_PR))


def _bail_records():
    return _records(_section_lines(BAILING))


def test_skill_md_commits_the_metrics_report_and_posts_its_metrics_block_on_the_pr_path_and_on_the_bail_path():
    problems = []
    pr_records = _pr_records()
    if not pr_records:
        problems.append("SKILL.md has no ### 4. Draft PR section to read")
    else:
        if _first_record(pr_records, "metrics.sh") is None:
            problems.append("SKILL.md's Draft PR step never runs metrics.sh")
        if _first_record(pr_records, "metrics:", "metrics.md") is None:
            problems.append("SKILL.md's Draft PR step has no instruction committing .tdd/issue-<n>-metrics.md in a metrics: commit")
        if _first_record(pr_records, "gh api -x patch") is None:
            problems.append("SKILL.md's Draft PR step never runs gh pr edit")
        if _first_record(pr_records, "✅ done", "📊 metrics") is None:
            problems.append("SKILL.md's final ✅ Done comment does not carry the ### 📊 Metrics block")
    bail_records = _bail_records()
    if not bail_records:
        problems.append("SKILL.md has no ## Bailing section to read")
    else:
        if _first_record(bail_records, "metrics.md", "commit") is None:
            problems.append("SKILL.md's Bailing section never commits .tdd/issue-<n>-metrics.md on the pushed branch")
        if _first_record(bail_records, "⛔ bailed", "📊 metrics") is None:
            problems.append("SKILL.md's ⛔ Bailed comment does not carry the ### 📊 Metrics block")
    assert not problems, "\n".join(problems)


def test_skill_md_draft_pr_step_writes_the_done_mark_carrying_the_pr_url_before_rendering_the_metrics_report_it_commits():
    problems = []
    pr_records = _pr_records()
    render_line = _first_record(pr_records, "metrics.sh", "> .tdd/issue-<n>-metrics.md")
    if render_line is None:
        problems.append("SKILL.md's Draft PR step never renders metrics.sh into .tdd/issue-<n>-metrics.md")
    done_line = _first_record(pr_records, "event.sh done", "pr=")
    if done_line is None:
        problems.append("SKILL.md's Draft PR step never writes event.sh done pr=<pr-url>")
    if render_line is not None and done_line is not None and render_line < done_line:
        problems.append("SKILL.md renders the committed metrics report BEFORE event.sh done")
    assert not problems, "\n".join(problems)


def test_skill_md_pastes_into_the_pr_body_and_the_done_comment_the_committed_report_rendered_after_event_sh_done():
    problems = []
    pr_records = _pr_records()
    pr_text = "\n".join(pr_records)

    done_at = _offset(pr_text, "event.sh done pr=")
    if done_at is None:
        problems.append("SKILL.md's Draft PR step never writes event.sh done pr=<pr-url>")
    render_at = _offset(pr_text, "metrics.sh <n> > .tdd/issue-<n>-metrics.md")
    if render_at is None:
        problems.append("SKILL.md's Draft PR step never renders metrics.sh <n> > .tdd/issue-<n>-metrics.md")
    if done_at is not None and render_at is not None and render_at < done_at:
        problems.append(f"SKILL.md renders the report at offset {render_at}, BEFORE event.sh done at offset {done_at}")

    body_at = _offset(pr_text, "contents of .tdd/issue-<n>-metrics.md")
    if body_at is None:
        problems.append("SKILL.md's Draft PR step never puts the contents of .tdd/issue-<n>-metrics.md into the PR body")
    else:
        body_cmd = "gh api " + pr_text[:body_at].rsplit("gh api ", 1)[-1]
        if "-f body=" not in body_cmd:
            problems.append("SKILL.md mentions the contents of .tdd/issue-<n>-metrics.md outside a gh api -f body=")
        if render_at is not None and body_at < render_at:
            problems.append(f"SKILL.md pastes the report into the PR body at offset {body_at}, BEFORE it is rendered at offset {render_at}")

    done_comment_line = _first_record(pr_records, "✅ done", "📊 metrics")
    if done_comment_line is None:
        problems.append("SKILL.md's Draft PR step has no ✅ Done comment carrying the 📊 Metrics block")
    else:
        done_comment = pr_records[done_comment_line - 1]
        comment_at = _offset(pr_text, done_comment)
        if render_at is not None and comment_at is not None and comment_at < render_at:
            problems.append(f"SKILL.md posts the ✅ Done comment's report at offset {comment_at}, BEFORE it is rendered at offset {render_at}")
        if "issue-<n>-metrics.md" not in done_comment and "file just committed" not in done_comment:
            problems.append("SKILL.md's ✅ Done comment does not paste the report from the committed file")
    assert not problems, "\n".join(problems)


def test_skill_md_draft_pr_command_block_reads_the_open_prs_url_before_the_metrics_commit_ordered_line_by_line():
    problems = []
    pr_line = _first_fenced(PR_READ)
    if pr_line is None:
        problems.append("SKILL.md's Draft PR command block never runs gh api …/pulls?head=")
    commit_line = _first_fenced(METRICS_COMMIT)
    if commit_line is None:
        problems.append('SKILL.md\'s Draft PR command block never runs git commit -m "metrics: …"')
    if pr_line is not None and commit_line is not None and commit_line < pr_line:
        problems.append(f"SKILL.md commits the metrics report at SKILL.md:{commit_line}, BEFORE gh api …/pulls?head= at SKILL.md:{pr_line}")
    assert not problems, "\n".join(problems)


def test_skill_md_draft_pr_command_block_runs_gh_pr_edit_after_the_metrics_commit_and_push_branch_ordered_line_by_line():
    problems = []
    edit_line = _first_fenced(PR_EDIT)
    if edit_line is None:
        problems.append("SKILL.md's Draft PR command block never runs gh pr edit")
    commit_line = _first_fenced(METRICS_COMMIT)
    if commit_line is None:
        problems.append('SKILL.md\'s Draft PR command block never runs git commit -m "metrics: …"')
    push_line = _first_fenced("push-branch.sh")
    if push_line is None:
        problems.append("SKILL.md's Draft PR command block never runs push-branch.sh")
    if edit_line is not None and commit_line is not None and edit_line < commit_line:
        problems.append(f"SKILL.md runs gh pr edit at SKILL.md:{edit_line}, BEFORE the metrics: commit at SKILL.md:{commit_line}")
    if edit_line is not None and push_line is not None and edit_line < push_line:
        problems.append(f"SKILL.md runs gh pr edit at SKILL.md:{edit_line}, BEFORE push-branch.sh at SKILL.md:{push_line}")
    assert not problems, "\n".join(problems)


def test_skill_md_draft_pr_command_block_runs_the_pulls_read_done_mark_metrics_commit_push_and_patch_in_that_order():
    problems = []
    prev_anchor = prev_line = None
    for anchor in (PR_READ, "event.sh done pr=", "metrics.sh <n>", METRICS_COMMIT, "push-branch.sh", PR_EDIT):
        line = _first_fenced(anchor)
        if line is None:
            problems.append(f"SKILL.md's Draft PR command block never runs {anchor}")
            prev_anchor = prev_line = None
            continue
        if prev_line is not None and line <= prev_line:
            problems.append(f"SKILL.md runs {anchor} at SKILL.md:{line}, not after {prev_anchor} at SKILL.md:{prev_line}")
        prev_anchor, prev_line = anchor, line
    assert not problems, "\n".join(problems)


def test_skill_md_draft_pr_gh_pr_edit_command_puts_the_committed_metrics_report_in_the_pr_body():
    edit_line = _first_fenced(PR_EDIT)
    assert edit_line is not None, "SKILL.md's Draft PR command block never runs gh pr edit"
    edit_cmd = SKILL.read_text().splitlines()[edit_line - 1]
    assert re.search(r"-f body=.*\.tdd/issue-<n>-metrics\.md", edit_cmd), (
        f"SKILL.md's gh pr edit at SKILL.md:{edit_line} does not put the contents of .tdd/issue-<n>-metrics.md in its -f body=: {edit_cmd[:120]}"
    )


def test_626_skill_md_bailing_section_writes_the_bail_mark_before_rendering_the_metrics_report_it_commits():
    problems = []
    bail_records = _bail_records()
    render_line = _first_record(bail_records, RENDER)
    if render_line is None:
        problems.append("SKILL.md's Bailing section never renders metrics.sh <n> > .tdd/issue-<n>-metrics.md")
    mark_line = _first_record(bail_records, "event.sh bail")
    if mark_line is None:
        problems.append("SKILL.md's Bailing section never writes event.sh bail")
    if render_line is not None and mark_line is not None and render_line < mark_line:
        problems.append(f"SKILL.md renders the committed metrics report in record {render_line}, BEFORE event.sh bail in record {mark_line}")
    assert not problems, "\n".join(problems)


def test_626_skill_md_bailing_section_marks_the_bail_with_its_cause_and_classification_before_rendering_the_metrics_report_it_commits():
    problems = []
    bail_records = _bail_records()
    render_line = _first_record(bail_records, RENDER)
    if render_line is None:
        problems.append("SKILL.md's Bailing section never renders metrics.sh <n> > .tdd/issue-<n>-metrics.md")
    mark_line = _first_record(bail_records, "event.sh bail", "cause=<cause>", 'classification="$classification"')
    if mark_line is None:
        problems.append('SKILL.md\'s Bailing section never writes event.sh bail carrying cause=<cause> and classification="$classification"')
    if render_line is not None and mark_line is not None and mark_line > render_line:
        problems.append(f"SKILL.md writes event.sh bail with its cause= and classification= only in record {mark_line}, AFTER rendering the committed metrics report in record {render_line}")
    assert not problems, "\n".join(problems)
