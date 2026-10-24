"""Cases for what skills/tdd/SKILL.md tells the conductor about readying the draft PR, and where it pushes the branch."""
import importlib
import pathlib
import re

SKILL = pathlib.Path(__file__).resolve().parents[4] / "SKILL.md"

DRAFT_PR = "### 4. Draft PR"
RESUME = "## Resume"
BAILING = "## Bailing"
BAIL = SKILL.with_name("BAIL.md")
RESUME_MD = SKILL.with_name("RESUME.md")
GUARDRAILS = "## Guardrails"
ISSUE = "### 1. Read the issue, enter the issue's worktree, capture the spec (or resume)"

_UPPER = {c: c + 32 for c in range(ord("A"), ord("Z") + 1)}


def _lower(text):
    return text.translate(_UPPER)


def _lines(heading):
    section = importlib.import_module("skill_sections").section(BAIL if heading == BAILING else RESUME_MD if heading == RESUME else SKILL, heading)
    lines = section.splitlines()[1:]
    return lines


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


def _commands(lines):
    out, buf, cont = [], "", False
    for line in lines:
        line = line.lstrip()
        buf = buf + " " + line if cont else line
        if buf.endswith("\\"):
            buf, cont = buf[:-1], True
            continue
        cont = False
        out.append(buf)
    if cont:
        out.append(buf)
    return [_lower(c) for c in out]


def _word(word):
    return rf"(?<!\w){re.escape(word)}(?!\w)"


def first_record(records, *patterns):
    return next((r for r in records if all(re.search(p, r) for p in patterns)), "")


def any_line(lines, pattern):
    return any(re.search(pattern, line) for line in lines)


DONE_MARK = r"veri_issue=[^ ]* veri_actor=conductor [$]s/event[.]sh done"
METRICS_COMMIT = r'git commit -m "metrics:'
ROLLUP_READ = r"gh api [^#]*/check-runs"
WAIT_CI_RUN = r"[^#]*[$]s/wait-ci[.]sh "
READY_RUN = r"[^#]*gh_pr_ready"
BODY_EDIT = r"gh api -x patch .*-f body="
PUSH_RUN = r"[^#]*([$]s/push-branch[.]sh|git push)"
LOG_FAILED_READ = r"[^#]*gh run view [^#]*--log-failed"
CI_REPAIR_MARK = "⟦ci-repair⟧"


def unmarked(records):
    return [r.translate({ord("*"): None, ord("`"): None}) for r in records]


def line_of(commands, pattern):
    return next((n for n, c in enumerate(commands, 1) if re.match(pattern, c)), None)


def commands_of(heading):
    return _commands(_lines(heading))


def draft_pr():
    return _records(_lines(DRAFT_PR))


def draft_pr_read():
    records = draft_pr()
    assert records, "SKILL.md has no ### 4. Draft PR section to read"
    return records


def draft_pr_commands():
    draft_pr_read()
    return commands_of(DRAFT_PR)


def test_draft_prs_step_readies_the_pr_against_the_already_pushed_branch_with_no_push_of_its_own():
    pushes = first_record(draft_pr_read(), re.escape("git push"))
    assert not pushes, f"Draft PR step still pushes the branch itself: {pushes[:120]}"


def test_draft_prs_step_puts_refactor_owed_render_output_in_the_pr_body_and_omits_the_section_on_exit_3():
    records = draft_pr()
    render = first_record(records, re.escape("refactor-owed.sh render"))
    assert render, "Draft PR step never runs refactor-owed.sh render"
    problems = []
    if not re.search(r"issue-[^ ]*refactor-owed\.md", render):
        problems.append(f"runs refactor-owed.sh render without naming the run's refactor-owed file: {render[:120]}")
    if "body" not in render:
        problems.append(f"renders the owed section without putting it in the PR body: {render[:120]}")
    if not first_record(records, re.escape("refactor-owed"), r"exits? 3", r"omit|left out|leaves it out|no section|nothing"):
        problems.append("never says an exit 3 from refactor-owed.sh render leaves the section out")
    assert not problems, problems


def test_draft_prs_step_copies_the_ledgers_owed_steps_bullets_into_the_pr_body_under_owed_steps():
    owed = [r for r in draft_pr() if "owed steps" in r]
    assert owed, "Draft PR step never mentions the ledger's ## Owed steps section"
    problems = []
    if not any_line(owed, re.escape(".tdd/issue-<n>.md")):
        problems.append("speaks of ## Owed steps without naming the run's .tdd/issue-<n>.md ledger")
    if not any_line(owed, re.escape("body")):
        problems.append("never puts the ## Owed steps bullets in the PR body")
    assert not problems, problems


def test_draft_prs_step_creates_no_pr_it_retitles_and_rewrites_the_open_one_and_marks_it_ready_for_review():
    commands = _commands(_lines(DRAFT_PR))
    problems = []
    if not any_line(commands, r"^gh api -x patch .*-f title="):
        problems.append("never edits the PR with a title")
    if not any_line(commands, r"^gh api -x patch .*-f body="):
        problems.append("never edits the PR with a body")
    if not any_line(commands, r"^[^#]*gh_pr_ready"):
        problems.append("never runs gh_pr_ready")
    creates = next((c for c in commands if re.search(r"^gh api repos/[{]owner[}]/[{]repo[}]/pulls -f", c)), "")
    if creates:
        problems.append(f"still creates a PR: {creates[:120]}")
    assert not problems, problems


def test_resume_reuses_the_open_pr_already_on_its_branch_and_opens_no_second_one():
    records = _records(_lines(RESUME))
    assert records, "SKILL.md has no ## Resume section to read"
    problems = []
    if not any_line(commands_of(RESUME), r"^gh api [^#]*pulls[?]head="):
        problems.append("Resume section never reads the open PR its branch already carries")
    creates = first_record(records, re.escape("pr-creating `gh api`"))
    if creates and not re.search(r"no open pr|no pr|none|no such pr", creates):
        problems.append(f"Resume section opens a PR without conditioning it on there being no open PR to reuse: {creates[:120]}")
    assert not problems, problems


def test_bailing_section_leaves_the_draft_pr_open_carrying_the_bail_diagnostic_and_opens_no_pr():
    records = _records(_lines(BAILING))
    assert records, "SKILL.md has no ## Bailing section to read"
    commands = commands_of(BAILING)
    problems = []
    if not any_line(commands, rf"^gh api [^#]*/issues/<pr-number>/comments|^{BODY_EDIT}"):
        problems.append("Bailing section neither comments on nor edits the body of the draft PR")
    closes = next((c for c in commands if re.search(r"^gh pr close", c)), "")
    if closes:
        problems.append(f"Bailing section closes the PR: {closes[:120]}")
    opens_none = first_record(records, re.escape("open no pr"))
    if opens_none:
        problems.append(f"Bailing section still tells the run to open no PR: {opens_none[:120]}")
    assert not problems, problems


def test_worktree_step_no_longer_says_the_draft_pr_is_opened_once_every_step_is_green():
    records = _records(_lines(ISSUE))
    assert records, "SKILL.md has no ### 1. Read the issue section to read"
    stale = first_record(records, re.escape("every step is green"))
    assert not stale, f"worktree step still says the draft PR is opened once every step is green: {stale[:120]}"


def test_draft_prs_step_after_gh_pr_ready_waits_on_wait_ci_and_reads_the_rollup_fail_closed():
    records = draft_pr_read()
    commands = commands_of(DRAFT_PR)
    ready = line_of(commands, READY_RUN)
    watch = line_of(commands, WAIT_CI_RUN)
    rollup = line_of(commands, ROLLUP_READ)
    problems = []
    if not (ready and watch and watch > ready):
        problems.append("runs no $S/wait-ci.sh after gh pr ready")
    if not (watch and rollup and rollup > watch):
        problems.append("reads no statusCheckRollup after its $S/wait-ci.sh")
    plain = unmarked(records)
    if not first_record(plain, re.escape("rollup"), _word("empty"), r"never[a-z ]* pass"):
        problems.append("no instruction says an empty rollup is never a pass")
    if not first_record(plain, "conclusion", "success", "neutral", "skipped", "fail"):
        problems.append("no instruction counts a conclusion other than SUCCESS, NEUTRAL or SKIPPED as failed")
    assert not problems, problems


def test_draft_prs_step_never_counts_a_pending_check_as_green_and_bails_on_one_still_pending_with_a_cause_classify_bail_classifies(capsys):
    records = draft_pr_read()
    classify_bail = importlib.import_module("veri.classify_bail")
    pending = r"pending check|check[a-z ]* pending"
    problems = []
    if not first_record(unmarked(records), pending, _word("never"), "green|pass"):
        problems.append("no instruction says a pending check never counts as green")
    bail = first_record(records, pending, "bound|timeout|time out|runs out", _word("bail"))
    if not bail:
        problems.append("no instruction bounds the CI wait and bails on a check still pending when the bound runs out")
    else:
        classified = ""
        for cause in (span.replace("`", "") for span in re.findall(r"`[^`]*`", bail)):
            if cause and classify_bail.main([cause]) == 0:
                classified = cause
        capsys.readouterr()
        if not classified:
            problems.append(f"bails on a check still pending past its bound with no cause classify-bail.sh classifies: {bail[:120]}")
    assert not problems, problems


def test_draft_prs_step_bounds_the_command_that_waits_on_the_readied_prs_checks_itself_and_runs_no_gh_pr_checks_after_gh_pr_ready():
    draft_pr_read()
    commands = commands_of(DRAFT_PR)
    ready = line_of(commands, READY_RUN)
    waits = line_of(commands, WAIT_CI_RUN)
    problems = []
    if not ready or not waits or waits <= ready:
        problems.append("runs no $S/wait-ci.sh after gh pr ready, so there is no CI wait to bound")
    else:
        matched = re.match(rf"^{WAIT_CI_RUN} *[^ ]+", commands[waits - 1])
        rest = commands[waits - 1][matched.end():].split() if matched else []
        bound = rest[0] if rest else ""
        if re.fullmatch(r"[0-9]+", bound) and int(bound) >= 600:
            problems.append(f"gives wait-ci.sh a slice of {bound} seconds, longer than one Bash call lives")
    checks = next((c for c in commands[ready or 0:] if re.search(r"^[^#]*gh pr checks", c)), "")
    if checks:
        problems.append(f"still waits with gh pr checks after gh pr ready: {checks[:120]}")
    assert not problems, problems


def test_draft_prs_step_waits_on_the_readied_prs_checks_and_reads_their_rollup_before_the_done_mark_and_the_metrics_commit():
    draft_pr_read()
    commands = commands_of(DRAFT_PR)
    problems = []
    for ci in (WAIT_CI_RUN, ROLLUP_READ):
        ci_at = line_of(commands, ci)
        if ci_at is None:
            problems.append(f"runs no {ci}, so its order against the done mark could not be checked")
            continue
        for recorded in (DONE_MARK, METRICS_COMMIT):
            at = line_of(commands, recorded)
            if at is None:
                problems.append(f"runs no {recorded}, so the CI read's order against it could not be checked")
            elif at <= ci_at:
                problems.append(f"runs {ci} (command line {ci_at}) after {recorded} (command line {at})")
    assert not problems, problems


def test_draft_prs_command_block_bails_with_cause_ci_timeout_on_wait_ci_shs_exit_2_before_the_done_mark():
    records = draft_pr_read()
    commands = commands_of(DRAFT_PR)
    waits = line_of(commands, WAIT_CI_RUN)
    done_at = line_of(commands, DONE_MARK)
    timeout = line_of(commands, "[^#]*ci-timeout")
    problems = []
    if waits is None or done_at is None:
        problems.append("runs no $S/wait-ci.sh or no done mark, so where it bails on a pending check could not be checked")
    elif not (timeout is not None and waits <= timeout < done_at):
        problems.append("no command line bails with cause ci-timeout between $S/wait-ci.sh and the done mark")
    if not first_record(unmarked(records), re.escape("wait-ci.sh"), _word("2"), re.escape("ci-timeout")):
        problems.append("no instruction says wait-ci.sh's exit 2 bails with cause ci-timeout")
    assert not problems, problems


def test_draft_prs_step_answers_a_failed_ci_check_with_a_repair_step_quoting_the_gh_run_view_log_failed_fail_line_committed_resuming_the_cycle_loop():
    records = draft_pr_read()
    commands = commands_of(DRAFT_PR)
    rollup = line_of(commands, ROLLUP_READ)
    done_at = line_of(commands, DONE_MARK)
    log = line_of(commands, LOG_FAILED_READ)
    problems = []
    if rollup is None or done_at is None:
        problems.append("reads no statusCheckRollup or runs no done mark, so where it repairs a failed check could not be checked")
    elif log is None or log <= rollup or log >= done_at:
        problems.append("no command line runs gh run view --log-failed between the rollup read and the done mark, so a failed check's log is never read")
    else:
        added = next(
            (n for n, c in enumerate(commands, 1) if log < n < done_at and re.match(r"^[$]s/add-ledger-step[.]sh [.]tdd/issue-<n>[.]md ", c)),
            None,
        )
        if added is None:
            problems.append("no command line appends a repair step with add-ledger-step.sh between the --log-failed read and the done mark")
        elif not any(added < n < done_at and c.startswith("git commit ") for n, c in enumerate(commands, 1)):
            problems.append("no command line commits the ledger after appending the repair step and before the done mark")
        record = first_record(unmarked(records), re.escape("log-failed"), re.escape("repair step"))
        if not record:
            problems.append("no record says what the repair step a failed check appends carries from --log-failed")
        else:
            if "fail -" not in record:
                problems.append(f"never says the CI repair step quotes the failing suite's FAIL - line: {record[:120]}")
            if not re.search("step 3|cycle loop", record):
                problems.append(f"never says the run returns to the cycle loop after appending the CI repair step: {record[:120]}")
    assert not problems, problems


def test_draft_prs_step_bails_on_a_second_red_ci_result_after_a_ci_repair_step_with_a_cause_classify_bail_maps_to_system_or_process():
    records = draft_pr_read()
    classify_bail = importlib.import_module("veri.classify_bail")
    commands = commands_of(DRAFT_PR)
    log = line_of(commands, LOG_FAILED_READ)
    done_at = line_of(commands, DONE_MARK)
    problems = []
    if log is None or done_at is None:
        problems.append("reads no --log-failed or runs no done mark, so where it bails on a second red CI result could not be checked")
    else:
        cause = None
        for n, c in enumerate(commands, 1):
            matched = re.match(r"^[^#]*[$]s/event[.]sh bail cause=", c)
            if log < n < done_at and matched:
                fields = c[matched.end():].split()
                first = fields[0] if fields else ""
                if first != "ci-timeout":
                    cause = first
                    break
        if not cause:
            problems.append("no command line bails (event.sh bail cause=...) between the --log-failed read and the done mark, so a second red CI result stops silently")
        elif classify_bail.CATEGORIES.get(cause) not in ("system", "process"):
            problems.append(f"bails on a second red CI result with cause {cause}, which classify-bail.sh maps to no system or process label")
    record = first_record(unmarked(records), re.escape("second red"), r"red ci|ci (check|result)")
    if not record:
        problems.append("no record says what a second red CI result after a repair step does")
    elif "bail" not in record:
        problems.append(f"never says a second red CI result bails: {record[:120]}")
    assert not problems, problems


def test_draft_prs_step_waits_on_ci_by_calling_wait_ci_sh_again_on_its_exit_3_with_no_wait_loop_inside_one_bash_call_and_no_pending_test_that_reads_status_alone():
    records = draft_pr_read()
    commands = commands_of(DRAFT_PR)
    ready = line_of(commands, READY_RUN)
    wait_ci = line_of(commands, WAIT_CI_RUN)
    done_at = line_of(commands, DONE_MARK)
    problems = []
    if not (ready and wait_ci and done_at and ready < wait_ci < done_at):
        problems.append("no command line runs $S/wait-ci.sh between gh pr ready and the done mark")
    if not first_record(unmarked(records), re.escape("wait-ci.sh"), _word("3"), "again"):
        problems.append("no instruction says to call wait-ci.sh again on its exit 3")
    loop = first_record(commands, r"^(while|until) .*; *do( |$)|^sleep [0-9]|^gh pr checks .*--watch")
    if loop:
        problems.append(f"command block waits inside one Bash call: {loop[:120]}")
    status_only = first_record(commands, r"[.]status *==")
    if status_only and "__typename" not in status_only:
        problems.append(f"command block tests a check pending by .status alone, so a legacy StatusContext row is never pending: {status_only[:120]}")
    assert not problems, problems


def test_draft_prs_step_stops_at_a_ci_timeout_or_ci_red_bail_with_no_done_mark_and_no_metrics_commit_after_it_in_its_command_block_and_goes_to_bailing():
    records = draft_pr_read()
    commands = commands_of(DRAFT_PR)
    problems = []
    followed = []
    block, fenced, bails = 0, False, {}
    for c in commands:
        if c.startswith("```"):
            block += 1
            fenced = not fenced
            continue
        if not fenced:
            continue
        if re.match(r"^[^#]*[$]s/event[.]sh bail cause=ci-(timeout|red)", c):
            bails[block] = bails.get(block, "") + " " + re.search(r"cause=ci-(timeout|red)", c).group()[6:]
            continue
        if bails.get(block) and (re.match(DONE_MARK, c) or re.match(METRICS_COMMIT, c)):
            followed.append(f"after{bails[block]}: {c}")
    if not any("event.sh bail cause=ci-" in c for c in commands):
        problems.append("runs no event.sh bail cause=ci-timeout or cause=ci-red, so whether a CI bail stops the step could not be checked")
    for line in followed:
        problems.append(f"command block records the run finished after a CI bail - {line[:160]}")
    if not first_record(unmarked(records), r"ci-timeout|ci-red", re.escape("bail.md")):
        problems.append("no instruction sends a ci-timeout or ci-red bail to BAIL.md")
    assert not problems, problems


def test_draft_prs_step_appends_its_ci_repair_step_with_a_ci_repair_text_and_recognises_a_second_red_by_that_mark_not_by_the_repair_steps_prose():
    commands = draft_pr_commands()
    problems = []
    appended = first_record(commands, r"^[^#]*[$]s/add-ledger-step[.]sh ", re.escape("ci failure"))
    if not appended:
        problems.append("no command line appends a CI repair step through add-ledger-step.sh")
    elif CI_REPAIR_MARK not in appended:
        problems.append(f"appends its CI repair step without the {CI_REPAIR_MARK} mark: {appended[:160]}")
    red = first_record(commands, r"^[^#]*[$]s/event[.]sh bail cause=ci-red")
    if not red:
        problems.append("no command line bails with cause ci-red, so how it recognises a second red could not be checked")
    else:
        if CI_REPAIR_MARK not in red and "ledger-steps.sh has-mark ci-repair" not in red:
            problems.append(f"recognises a second red CI result without the {CI_REPAIR_MARK} mark or ledger-steps.sh has-mark ci-repair: {red[:160]}")
        if "fix the ci failure" in red:
            problems.append(f"recognises a second red CI result by the repair step's prose: {red[:160]}")
    assert not problems, problems


def test_draft_prs_step_leaves_no_ci_run_on_the_readied_pr_that_nothing_reads_every_push_after_the_ci_read_is_followed_by_a_wait_ci_sh_call():
    commands = draft_pr_commands()
    read_at = line_of(commands, WAIT_CI_RUN)
    problems = []
    if read_at is None:
        problems.append("runs no $S/wait-ci.sh, so whether a later push has its CI run read could not be checked")
    else:
        pushed = ""
        for c in commands[read_at:]:
            if re.match(PUSH_RUN, c):
                pushed = c
                continue
            if pushed and re.match(WAIT_CI_RUN, c):
                pushed = ""
        if pushed:
            problems.append(f"pushes after the CI read with no wait-ci.sh after it, leaving that push's CI run unread: {pushed[:120]}")
    assert not problems, problems


def test_draft_prs_step_passes_every_wait_ci_sh_call_the_sha_it_just_pushed_from_git_rev_parse_head_as_the_head_it_waits_for():
    commands = draft_pr_commands()
    head = r'"?[$][(]git rev-parse head[)]"?'
    sha, unpinned = set(), []
    for c in commands:
        if re.match(PUSH_RUN, c):
            sha = set()
        if re.match(rf"^[a-z_][a-z0-9_]*={head}", c):
            sha.add(c.split("=")[0])
        if re.match(WAIT_CI_RUN, c):
            call = re.sub(r"#.*", "", c, count=1)
            call = re.sub(r";.*", "", call, count=1)
            call = re.sub(head, "@head@", call)
            words = call.split()
            arg = words[4] if len(words) >= 5 else ""
            var = re.sub(r'["${}]', "", arg)
            if arg != "@head@" and not (re.match(r'^"?[$]', arg) and var in sha):
                unpinned.append(c)
    problems = []
    if line_of(commands, WAIT_CI_RUN) is None:
        problems.append("runs no $S/wait-ci.sh, so which head its CI waits are given could not be checked")
    for line in unpinned:
        problems.append(f"calls wait-ci.sh with no head sha from git rev-parse HEAD after its last push: {line[:120]}")
    assert not problems, problems


def test_draft_prs_step_bails_on_the_metrics_pushs_ci_wait_with_a_command_in_its_block_ci_timeout_on_exit_2():
    commands = draft_pr_commands()
    metrics_at = line_of(commands, METRICS_COMMIT)
    problems = []
    if metrics_at is None:
        problems.append("makes no metrics: commit, so whether its push's CI wait bails could not be checked")
    else:
        bails, waited = [], False
        for c in commands[metrics_at:]:
            if c.startswith("```"):
                if waited:
                    break
                continue
            if re.match(WAIT_CI_RUN, c):
                waited = True
                continue
            matched = re.search(r"[$]s/event[.]sh bail cause=ci-(red|timeout)", c) if waited else None
            if matched:
                bails.append(matched.group()[23:] + " " + c[:matched.start()])
        keyed = [b for b in bails if b.split(" ")[0] == "ci-timeout" and re.search("[^0-9]2[^0-9]", " " + b + " ")]
        if not keyed:
            problems.append("no command line bails with cause ci-timeout on the metrics: push's wait-ci.sh exit 2, in the block after that wait")
    assert not problems, problems


def test_1431_draft_prs_step_says_a_red_ci_on_the_metrics_cost_report_push_appends_one_ci_repair_step_with_the_step_added_event_and_returns_to_the_cycle_loop_bailing_ci_red_only_when_the_ledger_already_holds_a_ci_repair_step():
    records = draft_pr_read()
    plain = unmarked(records)
    said = [m.group() for m in (re.search(r"the metrics: push .*", r) for r in plain) if m]
    problems = []
    if not said:
        problems.append("no instruction describes the metrics: push's CI wait, so what its red does could not be checked")
    else:
        repairs = first_record(
            said,
            r"exit 1|red",
            re.escape(CI_REPAIR_MARK),
            re.escape("step-added"),
            re.escape("cycle loop"),
            r"bails?[^.]*ci-red[^.]*only[^.]*already[^.]*⟦ci-repair⟧|only[^.]*already[^.]*⟦ci-repair⟧[^.]*bails?[^.]*ci-red",
        )
        if not repairs:
            problems.append(f"does not say a red CI on the metrics: push appends one ⟦ci-repair⟧ step with the step-added event and returns to the cycle loop, bailing ci-red only when the ledger already holds a ⟦ci-repair⟧ step: {said[0][:160]}")
        reversed_ = first_record(said, re.escape("not a repair step"))
        if reversed_:
            problems.append(f"still says the metrics: push's red is not a repair step: {reversed_[:160]}")
    assert not problems, problems


SUITE_REPAIR_MARK = "⟦suite-repair⟧"


def test_1431_draft_prs_step_metrics_push_block_bails_ci_red_on_a_red_ci_only_when_the_ledger_already_holds_a_ci_repair_step_then_itself_appends_the_ci_repair_step_and_records_its_step_added_event():
    commands = draft_pr_commands()
    metrics_at = line_of(commands, METRICS_COMMIT)
    problems = []
    if metrics_at is None:
        problems.append("Draft PR step makes no metrics: commit, so what its push's command block does on a red CI could not be checked")
    else:
        after_wait, waited = [], False
        for c in commands[metrics_at:]:
            if c.startswith("```"):
                if waited:
                    break
                continue
            if re.match(WAIT_CI_RUN, c):
                waited = True
                continue
            if waited:
                after_wait.append(c)
        guard_at = next(
            (
                n for n, c in enumerate(after_wait, 1)
                if re.search(r"[$]s/event[.]sh bail cause=ci-red", c)
                and re.search(r"! (grep -f .⟦ci-repair⟧.|[$]s/ledger-steps[.]sh has-mark ci-repair) [^|]*[|][|] [^|]*[$]s/event[.]sh bail cause=ci-red", c)
            ),
            None,
        )
        if guard_at is None:
            problems.append("no command line after the metrics: push's wait-ci.sh bails ci-red behind a ! grep -F '⟦ci-repair⟧' or ! $S/ledger-steps.sh has-mark ci-repair guard")
        else:
            later = after_wait[guard_at:]
            if not any(re.search(r"[$]s/event[.]sh step-added", c) for c in later):
                problems.append("no command line after the metrics: push's ci-red guard records a step-added event")
            if not any(re.search(r"[$]s/add-ledger-step[.]sh", c) and CI_REPAIR_MARK in c for c in later):
                problems.append("no command line after the metrics: push's ci-red guard runs add-ledger-step.sh with a ⟦ci-repair⟧ step")
            added, committed = False, False
            for c in later:
                if re.search(r"[$]s/add-ledger-step[.]sh", c) and CI_REPAIR_MARK in c:
                    added = True
                    continue
                if added and re.search(r"git add [.]tdd/issue-<n>[.]md", c) and re.search("git commit ", c):
                    committed = True
                    break
            if not committed:
                problems.append("no command line after the metrics: push's add-ledger-step.sh commits .tdd/issue-<n>.md")
    assert not problems, problems


def test_skill_md_reaches_the_default_branch_the_issue_and_the_pr_through_the_helper_or_gh_api_never_gh_repo_issue_pr():
    text = SKILL.read_text()
    problems = []
    for n, line in enumerate(text.splitlines(), 1):
        if re.search(r"\bgh (repo view|issue (view|comment)|pr (create|view|edit|ready|comment))\b", line):
            problems.append(f"SKILL.md:{n}:{line}")
    for route in ("gh_pr_ready", "lib/github.sh", "gh api ", "default_branch"):
        if route not in text:
            problems.append(f"SKILL.md never names {route}")
    assert not problems, problems


def test_draft_prs_step_calls_wait_ci_sh_with_no_fixed_total_and_states_the_bounds_rule_twice_the_mean_of_the_last_5_ci_runs_capped_at_10_minutes_540_s_fallback():
    commands = draft_pr_commands()
    records = draft_pr_read()
    problems = []
    if line_of(commands, WAIT_CI_RUN) is None:
        problems.append("Draft PR step runs no $S/wait-ci.sh, so how its CI wait is bounded could not be checked")
    for c in commands:
        if re.match(WAIT_CI_RUN, c):
            call = re.sub(r"#.*", "", c, count=1)
            call = re.sub(r";.*", "", call, count=1)
            words = call.split()
            if len(words) >= 4 and re.fullmatch(r"[0-9]+", words[3]):
                problems.append(f"calls wait-ci.sh with a fixed total-seconds: {c[:120]}")
    rule = first_record(
        unmarked(records),
        re.escape("wait-ci.sh"),
        r"(twice|2 ?[x×]) the mean",
        r"(last|most recent) (5|five)",
        r"(10 minutes|600 s)",
        re.escape("540"),
    )
    if not rule:
        problems.append("no instruction states wait-ci.sh's bound as twice the mean of the last 5 completed CI runs, capped at 10 minutes, falling back to 540 s")
    assert not problems, problems


def test_draft_prs_step_keys_its_ci_red_bail_on_ci_repair_only_and_states_a_suite_repair_step_leaves_the_run_its_one_ci_repair_attempt():
    commands = draft_pr_commands()
    records = draft_pr_read()
    keyed = first_record(commands, r"^[^#]*[$]s/event[.]sh bail cause=ci-red", re.escape(".tdd/issue-<n>.md"))
    problems = []
    if not keyed:
        problems.append("no command line bails with cause ci-red keyed on .tdd/issue-<n>.md")
    else:
        if CI_REPAIR_MARK not in keyed and "ledger-steps.sh has-mark ci-repair" not in keyed:
            problems.append(f"keys its ci-red bail without the {CI_REPAIR_MARK} mark or ledger-steps.sh has-mark ci-repair: {keyed[:160]}")
        if SUITE_REPAIR_MARK in keyed or "has-mark suite-repair" in keyed:
            problems.append(f"keys its ci-red bail on {SUITE_REPAIR_MARK} too: {keyed[:160]}")
    stated = first_record(records, re.escape(SUITE_REPAIR_MARK), re.escape(CI_REPAIR_MARK), r"one ci repair attempt")
    if not stated:
        problems.append("no instruction states that a ledger holding a ⟦suite-repair⟧ step and no ⟦ci-repair⟧ step still gets its one CI repair attempt")
    assert not problems, problems


def test_draft_prs_step_readies_the_pr_with_gh_pr_ready_pr_number_git_rev_parse_head_so_the_ready_for_review_ci_run_starts_on_the_head_just_pushed():
    readies = [c for c in draft_pr_commands() if re.search(r"(^|&& |; )gh_pr_ready( |$)", c)]
    problems = []
    if not readies:
        problems.append("Draft PR step never runs gh_pr_ready, so which head it readies the PR on could not be checked")
    for line in readies:
        if not re.search(r'gh_pr_ready <pr-number> "?[$][(]git rev-parse head[)]"?', line):
            problems.append(f"readies the PR without the head sha it just pushed: {line[:120]}")
    assert not problems, problems


def test_bailing_cause_token_list_names_rebased_tip_red_and_classifies_it_as_a_process_failure():
    token = first_record(_records(_lines(BAILING)), r"^ *- `rebased-tip-red`")
    assert token, "Bailing cause-token list has no rebased-tip-red entry"
    assert "**process** failure" in token, f"names rebased-tip-red without classifying it as a **process** failure: {token[:160]}"


def _opening_the_pr_invariant():
    return first_record(_records(_lines(GUARDRAILS)), re.escape("before you open the pr"))


def test_guardrails_invariant_about_opening_the_pr_says_neither_exactly_once_nor_the_only_full_suite_gate():
    invariant = _opening_the_pr_invariant()
    assert invariant, "Guardrails has no invariant about opening the PR to read"
    problems = [
        f'Guardrails invariant still says "{phrase}": {invariant[:160]}'
        for phrase in ("exactly once", "the only full-suite gate")
        if phrase in invariant
    ]
    assert not problems, problems


def test_guardrails_invariant_about_opening_the_pr_names_the_branchs_own_full_run_again_after_each_suite_repair_step_and_the_extra_run_on_the_rebased_tip_when_sub_step_1_rebased_the_branch():
    invariant = _opening_the_pr_invariant()
    assert invariant, "Guardrails has no invariant about opening the PR to read"
    problems = []
    if not first_record([invariant], r"own full(-suite)? (run|gate)"):
        problems.append(f"invariant never names the branch's own full run: {invariant[:160]}")
    if not first_record([invariant], re.escape(SUITE_REPAIR_MARK)):
        problems.append(f"invariant never says the branch's own full run runs again after each {SUITE_REPAIR_MARK} step: {invariant[:160]}")
    if not first_record([invariant], re.escape("rebased tip"), _word("rebased the branch")):
        problems.append(f"invariant never names the extra run on the rebased tip when sub-step 1 rebased the branch: {invariant[:160]}")
    assert not problems, problems


def test_draft_prs_step_says_a_conductor_never_re_runs_a_failed_ci_job_a_red_check_goes_to_the_repair_step_or_the_ci_red_bail_and_re_running_a_flake_is_the_operators_decision():
    rule = first_record(draft_pr_read(), re.escape("gh run rerun"), r"never re-?runs?")
    assert rule, "Draft PR step never says a conductor does not re-run a failed CI job with gh run rerun"
    problems = []
    if not (first_record([rule], re.escape("repair step")) and first_record([rule], re.escape("ci-red"))):
        problems.append(f"rule does not name the repair step and the ci-red bail as the only answer to a red check: {rule[:160]}")
    if not first_record([rule], re.escape("operator")):
        problems.append(f"rule does not leave re-running a known flake to the operator: {rule[:160]}")
    assert not problems, problems


def test_ci_red_bail_names_each_failed_ci_check_every_ci_red_bail_mark_in_the_draft_pr_step_carries_the_failed_checks_names_read_from_the_heads_check_runs_and_bailings_bailed_comment_names_them():
    draft_pr_read()
    bails = [line for line in _lines(DRAFT_PR) if "cause=ci-red" in line]
    problems = []
    if not bails:
        problems.append("Draft PR step runs no ci-red bail at all")
    for bail in bails:
        fields = [f for f in re.findall(r" [a-z_]+=", bail) if f not in (" cause=", " classification=")]
        if not (fields and 'failed="$(cat .tdd/wait-ci.out)"' in bail):
            problems.append(f"ci-red bail mark carries no field naming the failed checks read from the wait's stdout: {bail[:200]}")
    comment = first_record(_records(_lines(BAILING)), re.escape("### ⛔ bailed"), re.escape("ci-red"))
    if not (comment and first_record([comment], re.escape("check"))):
        problems.append("### ⛔ Bailed comment never says that a ci-red bail names each CI check that failed")
    assert not problems, problems


def test_1613_draft_prs_step_decides_whether_the_ledger_already_holds_a_ci_repair_step_with_ledger_steps_sh_has_mark_ci_repair_never_a_whole_ledger_grep_f_of_the_ci_repair_mark():
    bails = [c for c in draft_pr_commands() if "cause=ci-red" in c or "no_repair=$?" in c]
    problems = []
    if not bails:
        problems.append("Draft PR step has no command line bailing with cause ci-red")
    for line in bails:
        if "ledger-steps.sh has-mark ci-repair" not in line:
            problems.append(f"a ci-red bail line never asks ledger-steps.sh has-mark ci-repair: {line[:160]}")
        if "grep -f '\u27e6ci-repair\u27e7'" in line:
            problems.append(f"a ci-red bail line still greps the whole ledger for {CI_REPAIR_MARK}: {line[:160]}")
    prose = "\n".join(unmarked(draft_pr()))
    if "greps for \u27e6ci-repair\u27e7" in prose:
        problems.append("Draft PR step still says the ci-red bail greps for \u27e6ci-repair\u27e7")
    if "keys on \u27e6ci-repair\u27e7 only" not in prose:
        problems.append("Draft PR step no longer says the ci-red bail keys on \u27e6ci-repair\u27e7 only")
    assert not problems, problems


def test_1904_both_ci_red_bail_lines_take_failed_from_the_stdout_of_the_wait_ci_sh_wait_they_just_ran_and_neither_spells_a_gh_api_check_runs_query():
    draft_pr_read()
    lines = _lines(DRAFT_PR)
    bails = [i for i, line in enumerate(lines) if "cause=ci-red" in line and "event.sh bail" in line]
    problems = []
    if len(bails) != 2:
        problems.append(f"Draft PR step has {len(bails)} ci-red bail lines, not 2")
    for i in bails:
        bail = lines[i]
        if 'failed="$(cat .tdd/wait-ci.out)"' not in bail:
            problems.append(f"ci-red bail does not take failed= from the wait's stdout file: {bail[:200]}")
        if "check-runs" in bail or "gh api" in bail:
            problems.append(f"ci-red bail spells a gh api check-runs query: {bail[:200]}")
        waits = [j for j in range(i) if "wait-ci.sh" in lines[j] and "> .tdd/wait-ci.out" in lines[j]]
        if not waits:
            problems.append(f"no wait-ci.sh run writing its stdout to .tdd/wait-ci.out precedes the bail: {bail[:200]}")
    assert not problems, problems
