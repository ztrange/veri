"""Cases for what skills/tdd/SKILL.md tells the conductor to do with the run's metrics report, read as text.

Contract under test:
  SKILL.md's `### 4. Draft PR` step runs, in this order, `gh api …/pulls?head=` for the URL
  of the PR the plan commit already opened, `event.sh done pr=<pr-url>`, `metrics.sh`, a
  `metrics:` commit of `.tdd/issue-<n>-metrics.md`, `push-branch.sh`, and `gh api -X PATCH`,
  which carries the `### 📊 Metrics` block into the PR body; the same block goes into the
  final `✅ Done` comment; SKILL.md's `## Bailing` section commits the same file on the
  pushed branch and puts the block on the `⛔ Bailed` comment.
"""
import ast
import importlib
import pathlib
import re

SKILL = pathlib.Path(__file__).resolve().parents[4] / "SKILL.md"

DRAFT_PR = "### 4. Draft PR"
BAILING = "## Bailing"
BAIL = SKILL.with_name("BAIL.md")

PR_READ = "pulls?head="
PR_EDIT = "gh api -X PATCH"
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


def _file_line(n):
    return SKILL.read_text().splitlines()[n - 1]


def _clip(text, n):
    return text.encode()[:n].decode(errors="ignore")


def _render_status(line):
    m = re.search(r"([A-Za-z_][A-Za-z0-9_]*)=\$\?", line)
    return m.group(1) if m else None


def _mentions(status, text, tail=r"[^A-Za-z0-9_]"):
    return re.search(r"\$\{?" + status + "(" + tail + "|$)", text) is not None


def test_skill_metrics_pytest_file_header_comment_states_the_draft_pr_order_pulls_read_done_mark_metrics_sh_metrics_commit_push_and_patch():
    problems = []
    lines = (__doc__ or "").splitlines()
    start = next((i for i, line in enumerate(lines) if line.startswith("Contract under test")), None)
    if start is None:
        problems.append("test_skill_metrics.py has no Contract under test paragraph in its header to read")
    else:
        end = next((i for i in range(start, len(lines)) if not lines[i].strip()), len(lines))
        contract = "".join(line.strip() + " " for line in lines[start:end])
        prev_anchor = prev_at = None
        for anchor in (PR_READ, "event.sh done", "metrics.sh", "metrics:", "push-branch.sh", PR_EDIT):
            at = _offset(contract, anchor)
            if at is None:
                problems.append(f"test_skill_metrics.py's Contract under test never names {anchor}")
                continue
            if prev_at is not None and at <= prev_at:
                problems.append(f"test_skill_metrics.py's Contract under test names {anchor} at offset {at}, not after {prev_anchor} at offset {prev_at}")
            prev_anchor, prev_at = anchor, at
    assert not problems, "\n".join(problems)


_COMMIT_NEEDLES = ("metrics:", "METRICS_COMMIT", "git commit")
_PR_NEEDLES = ("gh pr create", "PR_READ", "pulls?head=")


def _record_needles(call):
    if not (isinstance(call, ast.Call) and isinstance(call.func, ast.Name) and call.func.id == "_first_record"):
        return None
    return [a.value if isinstance(a, ast.Constant) else ast.unparse(a) for a in call.args[1:]]


def _record_level_commit_before_pr_compares(src):
    found = []
    for fn in ast.walk(ast.parse(src)):
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        needles = {}
        for node in ast.walk(fn):
            if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
                got = _record_needles(node.value)
                if got is not None:
                    needles[node.targets[0].id] = " ".join(str(n) for n in got)
        for node in ast.walk(fn):
            if not isinstance(node, ast.Compare) or not any(isinstance(op, (ast.Gt, ast.GtE, ast.Lt, ast.LtE)) for op in node.ops):
                continue
            sides = [needles.get(o.id) if isinstance(o, ast.Name) else (" ".join(str(n) for n in _record_needles(o) or []) or None)
                     for o in [node.left, *node.comparators]]
            sides = [t for t in sides if t]
            if any(c in t for t in sides for c in _COMMIT_NEEDLES) and any(r in t for t in sides for r in _PR_NEEDLES):
                found.append(node.lineno)
    return found


def test_skill_metrics_pytest_file_carries_no_record_level_commit_before_pr_comparison_which_records_folding_makes_dead():
    problems = []
    src = pathlib.Path(__file__).read_text()
    dead_comment = "".join(["lands ", "BEFORE", " the PR is opened"])
    for lineno in _record_level_commit_before_pr_compares(src):
        problems.append(f"test_skill_metrics.py:{lineno} compares the metrics commit's record number against the PR's with an ordering operator, but the records fold both into the same record, so the check cannot fail")
    if dead_comment in src:
        problems.append("test_skill_metrics.py still carries the comment claiming a record-level probe catches a metrics commit made after the PR is opened")
    assert not problems, "\n".join(problems)


def test_skill_metrics_pytest_file_carries_no_record_level_gh_pr_create_and_metrics_block_presence_probe_which_records_folding_makes_dead():
    src = pathlib.Path(__file__).read_text()
    probe = "".join(["_first_record(pr_records, ", '"gh pr create", ', '"📊 metrics")'])
    assert probe not in src, (
        "test_skill_metrics.py still asks whether the record holding gh pr create also holds the 📊 metrics block, "
        "but the records fold the whole Draft PR sub-step into one record, so the probe cannot fail"
    )


def test_566_skill_md_draft_pr_step_makes_the_metrics_commit_only_on_a_metrics_sh_exit_of_0_and_otherwise_puts_the_failed_render_and_its_exit_code_in_the_pr_body():
    problems = []
    status = None
    render_line = _first_fenced(RENDER)
    if render_line is None:
        problems.append("SKILL.md's Draft PR command block never renders metrics.sh <n> > .tdd/issue-<n>-metrics.md")
    else:
        render_cmd = _file_line(render_line)
        status = _render_status(render_cmd)
        if status is None:
            problems.append(f"SKILL.md renders metrics.sh at SKILL.md:{render_line} without capturing its exit status, so nothing can keep a failed render out of the metrics: commit: {_clip(render_cmd, 120)}")

    commit_line = _first_fenced(METRICS_COMMIT)
    if commit_line is None:
        problems.append('SKILL.md\'s Draft PR command block never runs git commit -m "metrics: …"')
    elif status is not None:
        open_if = False
        for n in range(render_line + 1, commit_line):
            line = _file_line(n)
            if re.search(r"^\s*if\s.*\$\{?" + status + r"([^A-Za-z0-9_]|$)", line):
                open_if = True
            if re.search(r"^\s*fi(\s|;|$)", line):
                open_if = False
        commit_cmd = _file_line(commit_line)
        if not (_mentions(status, commit_cmd) or open_if):
            problems.append(f"SKILL.md runs the metrics: commit at SKILL.md:{commit_line} whatever ${status}, metrics.sh's exit status, says, so a failed render's partial report is committed: {_clip(commit_cmd, 120)}")

    edit_line = _first_fenced(PR_EDIT)
    if edit_line is None:
        problems.append("SKILL.md's Draft PR command block never runs gh api -X PATCH, so no PR body can name a failed render")
    else:
        edit_cmd = _lower(_file_line(edit_line))
        if not re.search(r"-f body=.*metrics\.sh.*exit", edit_cmd):
            problems.append(f"SKILL.md's gh api -X PATCH at SKILL.md:{edit_line} puts no line naming a failed metrics.sh render and its exit code in the PR body, so a failed render leaves the body quoting a report that was never committed: {_clip(edit_cmd, 120)}")
    assert not problems, "\n".join(problems)


def test_566_skill_md_draft_pr_step_on_a_non_zero_metrics_sh_exit_puts_the_failed_render_and_its_exit_code_in_the_done_comment_in_place_of_the_metrics_block():
    problems = []
    status = None
    render_line = _first_fenced(RENDER)
    if render_line is None:
        problems.append("SKILL.md's Draft PR command block never renders metrics.sh <n> > .tdd/issue-<n>-metrics.md")
    else:
        status = _render_status(_file_line(render_line))
        if status is None:
            problems.append(f"SKILL.md renders metrics.sh at SKILL.md:{render_line} without capturing its exit status, so no ✅ Done comment can name it")
        else:
            status = _lower(status)

    pr_records = _pr_records()
    done_line = _first_record(pr_records, "✅ done", "📊 metrics")
    if done_line is None:
        problems.append("SKILL.md's Draft PR step has no ✅ Done comment carrying the 📊 Metrics block")
    elif status is not None:
        done_record = pr_records[done_line - 1]
        if not ("metrics.sh" in done_record and _mentions(status, done_record, r"[^a-z0-9_]")):
            problems.append(f"SKILL.md's ✅ Done comment carries no line naming a failed metrics.sh render and its exit code (${status}), so a failed render leaves the comment pasting a report that was never committed: {_clip(done_record, 160)}")
    assert not problems, "\n".join(problems)


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


def test_566_skill_md_draft_pr_step_on_a_non_zero_metrics_sh_exit_neither_bails_nor_stops_it_goes_on_to_push_branch_sh_and_gh_api_patch():
    problems = []
    status = None
    render_line = _first_fenced(RENDER)
    if render_line is None:
        problems.append("SKILL.md's Draft PR command block never renders metrics.sh <n> > .tdd/issue-<n>-metrics.md")
    else:
        status = _render_status(_file_line(render_line))
        if status is None:
            problems.append(f"SKILL.md renders metrics.sh at SKILL.md:{render_line} without capturing its exit status")
    push_line = _first_fenced("push-branch.sh")
    if push_line is None:
        problems.append("SKILL.md's Draft PR command block never runs push-branch.sh")
    edit_line = _first_fenced(PR_EDIT)
    if edit_line is None:
        problems.append("SKILL.md's Draft PR command block never runs gh api -X PATCH")

    if status is not None and push_line is not None and edit_line is not None:
        gated_ifs = 0
        for n, text in _fenced(DRAFT_PR):
            if not (render_line < n <= edit_line):
                continue
            mentions = _mentions(status, text)
            if re.search(r"^\s*if\s", text):
                if mentions or gated_ifs > 0:
                    gated_ifs += 1
            elif re.search(r"^\s*fi(\s|;|$)", text) and gated_ifs > 0:
                gated_ifs -= 1
            if mentions and re.search(r"(event\.sh\s+bail|(^|[^A-Za-z0-9_-])(exit|return)([^A-Za-z0-9_-]|$))", text):
                problems.append(f"SKILL.md stops or bails on ${status}, metrics.sh's exit status, at SKILL.md:{n}, so a failed render ends the Draft PR step instead of reaching its push and PR body rewrite: {_clip(text, 120)}")
            if n in (push_line, edit_line):
                if gated_ifs != 0:
                    problems.append(f"SKILL.md runs SKILL.md:{n} inside an if on ${status}, so a non-zero metrics.sh exit skips it: {_clip(text, 120)}")
                if not re.search(r"^\s*(\$S/push-branch\.sh|gh\s+api\s+-X\s+PATCH)", text):
                    problems.append(f"SKILL.md guards SKILL.md:{n} behind a condition, so a non-zero metrics.sh exit may skip it: {_clip(text, 120)}")
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
