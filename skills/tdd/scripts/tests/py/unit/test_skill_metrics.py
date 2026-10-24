"""Cases for what skills/tdd/SKILL.md tells the conductor to do with the run's metrics report, read as text.

Contract under test:
  SKILL.md's `## Bailing` section commits `.tdd/issue-<n>-metrics.md` on the pushed branch
  and puts the `### 📊 Metrics` block on the `⛔ Bailed` comment.
"""
import importlib
import pathlib
import re

SKILL = pathlib.Path(__file__).resolve().parents[4] / "SKILL.md"

BAILING = "## Bailing"
BAIL = SKILL.with_name("BAIL.md")

METRICS_COMMIT = 'git commit -m "metrics:'
RENDER = "metrics.sh <n> > .tdd/issue-<n>-metrics.md"

_UPPER = {c: c + 32 for c in range(ord("A"), ord("Z") + 1)}


def _lower(text):
    return text.translate(_UPPER)


def _section_lines(heading):
    section = importlib.import_module("skill_sections").section(BAIL if heading == BAILING else SKILL, heading)
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


def _bail_records():
    return _records(_section_lines(BAILING))


def test_skill_md_commits_the_metrics_report_and_posts_its_metrics_block_on_the_bail_path():
    problems = []
    bail_records = _bail_records()
    if not bail_records:
        problems.append("SKILL.md has no ## Bailing section to read")
    else:
        if _first_record(bail_records, "metrics.md", "commit") is None:
            problems.append("SKILL.md's Bailing section never commits .tdd/issue-<n>-metrics.md on the pushed branch")
        if _first_record(bail_records, "⛔ bailed", "📊 metrics") is None:
            problems.append("SKILL.md's ⛔ Bailed comment does not carry the ### 📊 Metrics block")
    assert not problems, "\n".join(problems)


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


def _clip(text, n):
    return text.encode()[:n].decode(errors="ignore")


def _mentions(status, text, tail=r"[^A-Za-z0-9_]"):
    return re.search(r"\$\{?" + status + "(" + tail + "|$)", text) is not None


def test_566_skill_md_bailing_sub_step_4_makes_the_metrics_commit_only_on_a_metrics_sh_exit_of_0_and_otherwise_the_bailed_comment_carries_the_failed_render_and_its_exit_code():
    problems = []
    status = None
    bail_records = _bail_records()
    render_line = _first_record(bail_records, RENDER)
    if render_line is None:
        problems.append("SKILL.md's Bailing section never renders metrics.sh <n> > .tdd/issue-<n>-metrics.md")
    else:
        bail_render = bail_records[render_line - 1]
        m = re.search(r"([a-z_][a-z0-9_]*)=\$\?", bail_render)
        if m:
            status = m.group(1)
            after_capture = bail_render.split(status + "=$?", 1)[1]
            before_commit = after_capture.split(METRICS_COMMIT, 1)[0]
            if not (METRICS_COMMIT in after_capture and re.search(r"\$\{?\"?" + status + r"([^a-z0-9_]|$)", before_commit)):
                problems.append(f"SKILL.md's Bailing section makes the metrics: commit in record {render_line} whatever ${status}, metrics.sh's exit status, says, so a failed render's partial report is committed: {_clip(bail_render, 160)}")
        else:
            problems.append(f"SKILL.md renders metrics.sh in Bailing record {render_line} without capturing its exit status, so nothing can keep a failed render out of the metrics: commit: {_clip(bail_render, 160)}")

    bailed_line = _first_record(bail_records, "⛔ bailed", "📊 metrics")
    if bailed_line is None:
        problems.append("SKILL.md's Bailing section has no ⛔ Bailed comment carrying the 📊 Metrics block")
    elif status is not None:
        bailed_record = bail_records[bailed_line - 1]
        if not ("metrics.sh" in bailed_record and _mentions(status, bailed_record, r"[^a-z0-9_]")):
            problems.append(f"SKILL.md's ⛔ Bailed comment carries no line naming a failed metrics.sh render and its exit code (${status}) in place of the 📊 Metrics block: {_clip(bailed_record, 160)}")
    assert not problems, "\n".join(problems)


def test_566_skill_md_bailing_sub_step_4_on_a_non_zero_metrics_sh_exit_does_not_stop_the_bail_it_goes_on_to_sub_step_5_push_and_sub_step_6_bailed_comment():
    problems = []
    status = None
    bail_records = _bail_records()
    render_line = _first_record(bail_records, RENDER)
    if render_line is None:
        problems.append("SKILL.md's Bailing section never renders metrics.sh <n> > .tdd/issue-<n>-metrics.md")
    else:
        render = bail_records[render_line - 1]
        m = re.search(r"([a-z_][a-z0-9_]*)=\$\?", render)
        if m:
            status = m.group(1)
            if not re.search(r"^4\.", render):
                problems.append(f"SKILL.md renders metrics.sh in Bailing record {render_line}, which is not sub-step 4: {_clip(render, 120)}")
            after_capture = render.split(status + "=$?", 1)[1]
            if re.search(r"(event\.sh\s+bail|(^|[^a-z0-9_-])(exit|return|stop|stops|skip|skips|abort|aborts)([^a-z0-9_-]|$))", after_capture):
                problems.append(f"SKILL.md's Bailing sub-step 4 stops or skips on ${status}, metrics.sh's exit status, so a failed render ends the bail before its push and comment: {_clip(after_capture, 160)}")
        else:
            problems.append(f"SKILL.md renders metrics.sh in Bailing record {render_line} without capturing its exit status")

    if status is not None:
        push_line = _first_record(bail_records, "git push")
        if push_line is None:
            problems.append("SKILL.md's Bailing section never pushes the branch")
        else:
            push = bail_records[push_line - 1]
            if not (re.search(r"^5\.", push) and push_line > render_line):
                problems.append(f"SKILL.md's Bailing push is not sub-step 5, after the metrics render in record {render_line}: {_clip(push, 120)}")
            if _mentions(status, push, r"[^a-z0-9_]"):
                problems.append(f"SKILL.md's Bailing sub-step 5 push is conditioned on ${status}, so a non-zero metrics.sh exit may skip it: {_clip(push, 160)}")
        bailed_line = _first_record(bail_records, "⛔ bailed", "📊 metrics")
        if bailed_line is None:
            problems.append("SKILL.md's Bailing section has no ⛔ Bailed comment carrying the 📊 Metrics block")
        else:
            bailed = bail_records[bailed_line - 1]
            if not (re.search(r"^6\.", bailed) and bailed_line > render_line):
                problems.append(f"SKILL.md's ⛔ Bailed comment is not sub-step 6, after the metrics render in record {render_line}: {_clip(bailed, 120)}")
            if re.search(r"(^|[^a-z0-9_-])(stop|stops|skip|skips|omit|abort|aborts)([^a-z0-9_-]|$)", bailed):
                problems.append(f"SKILL.md's ⛔ Bailed comment in sub-step 6 is skipped or stopped on a failed render: {_clip(bailed, 160)}")
    assert not problems, "\n".join(problems)
