"""How skills/tdd/SKILL.md's preflight checks launchability, budgets, GitHub, the worktree baseline and the conductor.pid lock, read as text."""
import pathlib
import re
import subprocess

import pytest

import skill_sections

SKILL = pathlib.Path(__file__).resolve().parents[2].parent / "SKILL.md"

PREFLIGHT = "### 0. Preflight — baseline checks (bail before any cycle)"
STEP1 = "### 1. Read the issue, enter the issue's worktree, capture the spec (or resume)"
PLAN = "### 2. Scope & plan → the ledger"
RESUME = "## Resume"

FAST_CALL = "detect-test-command.sh --tier fast"
FULL_CALL = "detect-test-command.sh --tier all"
ENTER_CALL = 'cd "$wt"'
WORKTREE_CALL = "issue-worktree.sh"
PID_WRITE = "> .tdd/conductor.pid"
PID_VALUE = '"$PPID"'
DETACH_START = "detach-command.sh start"
ITEM_RE = r"^[0-9]+\."


def all_lines():
    return SKILL.read_text().splitlines()


def lines_of(heading):
    return skill_sections.section(SKILL.with_name("RESUME.md") if heading == RESUME else SKILL, heading).splitlines()


def first(lines, want):
    return next((i for i, line in enumerate(lines) if want in line), None)


def first_all(lines, *wants, start=0):
    return next((i for i in range(start, len(lines)) if all(w in lines[i] for w in wants)), None)


def worktree_entry(lines):
    at = first_all(lines, WORKTREE_CALL, ENTER_CALL)
    assert at is not None, "no line runs issue-worktree.sh and then cd \"$wt\""
    return at


def baseline_start(lines, enter_at):
    at = next((i for i in range(enter_at + 1, len(lines))
               if FAST_CALL in lines[i] or DETACH_START in lines[i]), None)
    assert at is not None, "no baseline start after the worktree is entered"
    return at


def item_around(lines, at):
    begin = max((i for i in range(at + 1) if re.match(ITEM_RE, lines[i])), default=0)
    end = next((i for i in range(at + 1, len(lines)) if re.match(ITEM_RE, lines[i])), len(lines))
    return lines[begin:end]


def paragraph_around(lines, at):
    begin = at
    while begin > 0 and lines[begin - 1].strip() and not re.match(ITEM_RE, lines[begin]):
        begin -= 1
    end = at + 1
    while end < len(lines) and lines[end].strip() and not re.match(ITEM_RE, lines[end]):
        end += 1
    return lines[begin:end]


def sentences(lines):
    return re.sub(r"[.] ", ".\n", re.sub(r"  +", " ", " ".join(lines))).split("\n")


def test_skill_md_s_preflight_runs_leaf_launchable_sh_before_the_baseline_suite():
    lines = lines_of(PREFLIGHT)
    launch_at = first(lines, "leaf-launchable.sh")
    baseline_at = first(lines, "detect-test-command.sh")
    assert launch_at is not None, "preflight never names leaf-launchable.sh"
    assert baseline_at is not None, "preflight has no item naming detect-test-command.sh"
    assert launch_at <= baseline_at, "leaf-launchable.sh is called after the baseline"


def test_skill_md_s_preflight_refuses_to_start_on_a_bad_VERI_STEP_GROWTH():
    lines = lines_of(PREFLIGHT)
    at = first(lines, "VERI_STEP_GROWTH")
    assert at is not None, "preflight never names VERI_STEP_GROWTH"
    assert re.search(r"exits? 2", "\n".join(item_around(lines, at)), re.I), "its item spells no exit 2"


def test_skill_md_s_preflight_calls_step_budget_sh_beside_refactor_budget_sh_0_and_stops_on_its_exit_2():
    lines = lines_of(PREFLIGHT)
    at = first(lines, "step-budget.sh")
    assert at is not None, "preflight never names step-budget.sh"
    assert any("refactor-budget.sh 0" in line for line in item_around(lines, at))
    assert re.search(r"exits? 2", "\n".join(paragraph_around(lines, at)), re.I)


def test_skill_md_s_preflight_checks_GitHub_with_gh_api_user_and_stops_the_run_on_its_non_zero_exit():
    lines = lines_of(PREFLIGHT)
    auth_at = first(lines, "claude auth status")
    assert auth_at is not None, "preflight never names claude auth status"
    assert any("gh api user" in line for line in item_around(lines, auth_at))
    para = "\n".join(paragraph_around(lines, first(lines, "gh api user"))).lower()
    assert "non-zero" in para and "preflight" in para


def test_skill_md_runs_the_fast_tier_baseline_inside_the_issue_s_worktree_after_issue_worktree_sh_cut_the_branch():
    lines = all_lines()
    enter_at = worktree_entry(lines)
    fast_at = first(lines, FAST_CALL)
    assert fast_at is not None, "SKILL.md never names the fast-tier baseline"
    assert fast_at >= enter_at, "the baseline runs before the worktree is entered"


def test_skill_md_stops_the_run_on_a_red_baseline_in_the_worktree_as_a_preflight_failure_whatever_state_the_caller_s_checkout_is_in():
    pre = lines_of(PREFLIGHT)
    fast_in = first(pre, FAST_CALL)
    assert fast_in is not None, "preflight never names the fast-tier baseline"
    whole = all_lines()
    plan_at = whole.index(PLAN)
    pre_start = whole.index(PREFLIGHT)
    assert pre_start + fast_in < plan_at, "the baseline runs after the plan section"
    stops = [s for s in sentences(item_around(pre, fast_in)) if "red baseline" in s.lower()]
    assert any("preflight" in s.lower() and "caller's checkout" in s for s in stops), stops


def test_skill_md_takes_the_full_tier_measurement_in_the_worktree_on_the_fast_tier_baseline_s_commit_and_sizes_leaf_timeout_sh_full_only_after_it():
    lines = lines_of(PREFLIGHT)
    fast_in, full_in = first(lines, FAST_CALL), first(lines, FULL_CALL)
    timeout_in = first_all(lines, "leaf-timeout.sh", "--full")
    assert fast_in is not None and full_in is not None, (fast_in, full_in)
    assert full_in >= fast_in, "the full tier is measured before the fast-tier baseline"
    moves = [line for line in lines[fast_in:full_in + 1]
             if re.search(r"(^|[^A-Za-z0-9_-])cd |git (checkout|switch|pull|fetch|reset|rebase)|issue-worktree\.sh", line)]
    assert moves == []
    assert timeout_in is not None, "no leaf-timeout.sh call with --full"
    assert timeout_in >= full_in, "the timeout is sized before the full-tier measurement"


def test_skill_md_says_a_resumed_run_s_baseline_runs_on_the_branch_head_in_its_existing_worktree_before_any_cycle():
    text = re.sub(r"  +", " ", " ".join(lines_of(RESUME)))
    says = [s for s in re.split(r"[.] ", text)
            if all(w in s.lower() for w in ("baseline", "branch head", "worktree", "cycle"))]
    assert says, "no sentence in Resume says the baseline runs on the branch head in its worktree before any cycle"


def test_skill_md_takes_the_worktree_s_dot_tdd_conductor_pid_lock_in_preflight_step_3_after_cd_wt_and_before_the_fast_tier_baseline():
    lines = all_lines()
    enter_at = worktree_entry(lines)
    pid_at = first_all(lines, PID_WRITE, PID_VALUE)
    assert pid_at is not None, "no line writes \"$PPID\" to .tdd/conductor.pid"
    base_at = baseline_start(lines, enter_at)
    assert pid_at >= enter_at, "the lock is written before the worktree is entered"
    assert pid_at <= base_at, "the lock is written after the baseline starts"


def test_skill_md_s_worktree_guard_prose_says_the_lock_is_taken_in_preflight_step_3_before_the_baseline_and_never_in_step_1_2():
    lines = all_lines()
    guard_at = first(lines, "**worktree guard**")
    assert guard_at is not None, "SKILL.md never names the worktree guard"
    says = [s for s in sentences(paragraph_around(lines, guard_at))
            if all(w in s.lower() for w in ("lock", "preflight step 3", "before the baseline"))]
    assert says, "the guard paragraph has no sentence naming the lock, 'preflight step 3' and 'before the baseline'"
    step1 = lines_of(STEP1)
    slug_at = first(step1, "**Derive the slug")
    assert slug_at is not None, "step 1 has no 'Derive the slug' item"
    here = [s for s in sentences(item_around(step1, slug_at))
            if re.search(r"(^|[^a-z])(takes?|took|taken|writes?|wrote|written|overwrites?)([^a-z]|$)", s, re.I)
            and re.search(r"(^|[^a-z])here([^a-z]|$)", s, re.I)]
    assert here == []
    elsewhere = [s for s in sentences(lines)
                 if re.search(r"step 1\.2 (takes|writes|locks)|(taken|written|took|wrote) in step 1\.2", s, re.I)]
    assert elsewhere == []


DRAFT = "### 4. Draft PR"
REBASE_CALL = "rebase-onto-default.sh"
LEASE_PUSH = "push-branch.sh --force-with-lease=<branch>:<pre-rebase-sha>"
RESET_HEAD = "git reset --hard HEAD"
PRE_SHA = "<pre-rebase-sha>"
NEGATION = r"(^|[^A-Za-z])(not|never|no)([^A-Za-z]|$)"


def rebase_span():
    lines = all_lines()
    enter_at = worktree_entry(lines)
    base_at = baseline_start(lines, enter_at)
    return sentences(lines[enter_at:base_at + 1])


def resume_step3():
    whole = all_lines()
    enter_at = worktree_entry(whole)
    base_at = baseline_start(whole, enter_at)
    pre = lines_of(PREFLIGHT)
    offset = whole.index(PREFLIGHT)
    at = enter_at - offset
    assert 0 <= at < len(pre), "the worktree is entered outside preflight"
    begin = max((i for i in range(at + 1) if re.match(ITEM_RE, pre[i])), default=0)
    end = next((i for i in range(at + 1, len(pre)) if re.match(ITEM_RE, pre[i])), len(pre))
    return whole, enter_at, base_at, offset + begin, offset + end


def line_of(lines, want, start, end):
    return next((i for i in range(start, end) if want in lines[i]), None)


def test_1297_skill_md_has_a_resumed_run_one_whose_worktree_and_ledger_already_exist_run_rebase_onto_default_sh_before_its_preflight_baseline_and_a_new_branch_s_run_not_rebase_there():
    between = rebase_span()
    assert [s for s in between if REBASE_CALL in s and "resum" in s.lower() and "ledger" in s.lower()], \
        "no sentence says a resumed run, whose worktree and ledger already exist, runs rebase-onto-default.sh"
    assert [s for s in between if "new branch" in s.lower() and "rebase" in s.lower()
            and re.search(NEGATION, s, re.I)], "no sentence says a new branch's run does not rebase there"


def test_1297_skill_md_says_the_resume_rebase_onto_default_sh_s_exit_3_goes_on_unchanged_its_exit_1_goes_on_from_the_old_base_and_leaves_the_conflict_to_the_draft_pr_step_and_its_exit_2_bails_no_verdict():
    between = rebase_span()
    assert [s for s in between if re.search(r"exits? 3", s, re.I) and "unchanged" in s.lower()], \
        "no sentence says the resume rebase's exit 3 goes on unchanged"
    assert [s for s in between if re.search(r"exits? 1", s, re.I) and "old base" in s.lower()
            and "draft pr" in s.lower()], "no sentence says exit 1 goes on from the old base and leaves the conflict to the Draft PR step"
    assert [s for s in between if re.search(r"exits? 2", s, re.I) and "bail" in s.lower()
            and "no-verdict" in s], "no sentence says exit 2 bails no-verdict"


def test_1297_skill_md_publishes_a_resume_rebase_that_moved_the_branch_once_the_baseline_is_green_with_the_lease_push_never_a_bare_force():
    whole, enter_at, base_at, begin, end = resume_step3()
    push_at = line_of(whole, LEASE_PUSH, enter_at, end)
    assert push_at is not None, "preflight step 3 never names the lease push"
    assert push_at > base_at, "the rebased tip is published before the fast-tier baseline starts"
    step3 = sentences(whole[begin:end])
    assert [s for s in step3 if LEASE_PUSH in s and "green" in s.lower()], "the lease push sentence does not say green"
    assert [s for s in step3 if "bare force" in s.lower() and re.search(NEGATION, s, re.I)], \
        "no sentence says the resume rebase is never published with a bare force"


def test_1297_skill_md_resets_a_red_baseline_on_the_resume_rebased_tip_to_pre_rebase_sha_before_the_run_bails():
    whole, enter_at, base_at, begin, end = resume_step3()
    assert [s for s in sentences(whole[begin:end]) if re.search(r"\bred\b", s, re.I) and "reset" in s.lower()
            and PRE_SHA in s and "bail" in s.lower()], \
        "no sentence says a red baseline on the rebased tip resets to <pre-rebase-sha> before the run bails"


def test_1297_skill_md_marks_a_resume_rebase_that_moved_the_branch_in_the_run_log_as_its_own_event_carrying_the_pre_rebase_and_rebased_shas_named_apart_from_the_draft_pr_step_s_rebase():
    whole, enter_at, base_at, begin, end = resume_step3()
    rebase_at = line_of(whole, REBASE_CALL, enter_at, end)
    marks = [m.group(0) for line in whole[rebase_at if rebase_at is not None else enter_at:end]
             for m in re.finditer(r"event\.sh [a-z][a-z-]*( [^`]*)?", line)]
    mark = next((m for m in marks if PRE_SHA in m), None)
    assert mark is not None, "no event.sh mark after the rebase call carries <pre-rebase-sha>"
    name = mark.split()[1]
    assert re.search(r"rebased|rev-parse HEAD", mark[len(f"event.sh {name}"):]), \
        f"the event.sh {name} mark does not carry the rebased sha: {mark}"
    draft = lines_of(DRAFT)
    assert not [line for line in draft if re.search(rf"event\.sh {name}( |$|`)", line)], \
        f"the Draft PR section also writes event.sh {name}"


def test_1297_skill_md_captures_and_resets_a_dirty_resume_worktree_before_the_resume_rebase_onto_default_sh_and_says_pre_rebase_sha_is_its_first_stdout_line_before_first_using_it():
    whole, enter_at, base_at, begin, end = resume_step3()
    rebase_at = line_of(whole, REBASE_CALL, enter_at, end)
    capture_at = next((i for i in range(enter_at, end)
                       if re.search(r'="\$\(git status --porcelain\)"', whole[i])), None)
    reset_at = line_of(whole, RESET_HEAD, enter_at, end)
    assert capture_at is not None and reset_at is not None, \
        "preflight step 3 does not capture git status --porcelain into a variable and then run git reset --hard HEAD"
    if rebase_at is not None:
        assert capture_at < reset_at < rebase_at, (capture_at, reset_at, rebase_at)
    first_use = next((s for s in sentences(whole[enter_at:end]) if PRE_SHA in s), "")
    assert REBASE_CALL in first_use and re.search(r"first (stdout )?line", first_use, re.I), \
        f"step 3 first uses <pre-rebase-sha> without saying it is the rebase's first stdout line: {first_use}"


BARE_FORCE_GOVERNED = r"(^|[^A-Za-z])(not|never|no)(\s+[A-Za-z]+){0,3}\s+bare force"
LEAF_MODEL_CALL = "$S/leaf-model.sh develop-red"
STATUS_CAPTURE = re.compile(r'="\$\(git status --porcelain\)"')
FENCE = re.compile(r"^\s*```")
SCRIPTS = SKILL.parent / "scripts"


def test_1297_skill_md_s_preflight_step_3_says_never_a_bare_force_with_the_negation_on_the_bare_force_itself_not_on_another_word_of_the_sentence():
    whole, enter_at, base_at, begin, end = resume_step3()
    step3 = sentences(whole[begin:end])
    assert [s for s in step3 if re.search(BARE_FORCE_GOVERNED, s, re.I)], \
        "no sentence of preflight step 3 has a not, never or no governing 'bare force'"


def test_1485_skill_md_s_preflight_step_6_reads_an_empty_or_whitespace_only_model_variable_as_unset_and_stops_only_on_a_value_with_internal_whitespace():
    lines = lines_of(PREFLIGHT)
    at = first(lines, LEAF_MODEL_CALL)
    assert at is not None, "preflight never calls leaf-model.sh develop-red"
    item = sentences(item_around(lines, at))
    assert [s for s in item if re.search("empty", s, re.I) and re.search("whitespace-only", s, re.I)
            and re.search("unset", s, re.I)], "no sentence of the leaf-model item says an empty or whitespace-only variable is treated as unset"
    assert [s for s in item if re.search("internal whitespace", s, re.I) and re.search(r"exit 2|stops?", s, re.I)], \
        "no sentence of the leaf-model item says a value with internal whitespace is what stops the run"


def discard_block():
    whole, enter_at, base_at, begin, end = resume_step3()
    capture_at = next((i for i in range(enter_at, end) if STATUS_CAPTURE.search(whole[i])), None)
    assert capture_at is not None, "preflight step 3 has no line capturing git status --porcelain"
    body = []
    for line in whole[:capture_at]:
        body = [] if FENCE.match(line) else body + [line]
    for line in whole[capture_at:]:
        if FENCE.match(line):
            break
        body.append(line)
    return "\n".join(body) + "\n"


def git(cwd, *args):
    subprocess.run(["git", "-C", str(cwd), *args], check=True, capture_output=True)


def new_repo(path, *args):
    subprocess.run(["git", "init", "-q", "-b", "main", *args, str(path)], cwd=path.parent, check=True, capture_output=True)
    if "--bare" not in args:
        git(path, "config", "user.name", "Test")
        git(path, "config", "user.email", "test@example.com")


def commit_all(path, message):
    git(path, "add", "-A")
    git(path, "commit", "-q", "-m", message)


def run_discard(wt, tail=""):
    return subprocess.run(["bash", "-c", discard_block() + tail], cwd=wt, capture_output=True, text=True)


def discard_stray(wt, tmp_path):
    stray_out = tmp_path / "stray.out"
    run_discard(wt, f'printf \'%s\\n\' "$stray" > "{stray_out}"\n')
    return stray_out.read_text() if stray_out.exists() else ""


@pytest.mark.process("git: a bash-run discard block in a clone, then rebase-onto-default.sh over the default branch's new file")
def test_1420_skill_md_s_preflight_discard_removes_a_killed_leaf_s_untracked_file_at_a_path_the_default_branch_has_since_added_so_the_resume_rebase_onto_default_sh_exits_0_not_2(tmp_path):
    origin, seed, wt = tmp_path / "origin.git", tmp_path / "seed", tmp_path / "wt"
    new_repo(origin, "--bare")
    new_repo(seed)
    (seed / "file.txt").write_text("base\n")
    commit_all(seed, "initial")
    git(seed, "push", "-q", str(origin), "main")
    subprocess.run(["git", "clone", "-q", str(origin), str(wt)], cwd=tmp_path, check=True, capture_output=True)
    git(wt, "config", "user.name", "veri")
    git(wt, "config", "user.email", "veri@example.test")
    git(wt, "checkout", "-q", "-b", "tdd/1-a-run")
    (wt / "work.txt").write_text("the run's work\n")
    commit_all(wt, "feat: a step's green commit (#1)")
    (seed / "other.txt").write_text("another run's work\n")
    commit_all(seed, "feat: another run merged (#2)")
    git(seed, "push", "-q", str(origin), "main")
    git(wt, "fetch", "-q", "origin")
    (wt / "other.txt").write_text("a killed leaf's half-written file\n")
    run_discard(wt)
    rebase = subprocess.run(["bash", str(SCRIPTS / REBASE_CALL)], cwd=wt, capture_output=True, text=True)
    assert rebase.returncode == 0, f"{REBASE_CALL} after the discard block, exit: want 0, got {rebase.returncode} - stderr: {rebase.stderr}"


@pytest.mark.process("git: a bash-run discard block in a repository holding an untracked file")
def test_1420_skill_md_s_preflight_discard_captures_a_killed_leaf_s_untracked_file_in_stray_before_removing_it_so_the_resuming_comment_names_it(tmp_path):
    wt = tmp_path / "wt"
    new_repo(wt)
    (wt / "file.txt").write_text("base\n")
    commit_all(wt, "initial")
    (wt / "other.txt").write_text("a killed leaf's half-written file\n")
    got = discard_stray(wt, tmp_path)
    assert "?? other.txt" in got.splitlines(), f"$stray does not list the untracked file: want a line '?? other.txt', got: {got}"


@pytest.mark.process("git: a bash-run discard block in a repository whose .gitignore names .tdd/")
def test_1420_skill_md_s_preflight_discard_never_removes_a_file_gitignore_ignores_so_a_tdd_leaf_log_survives_it(tmp_path):
    wt = tmp_path / "wt"
    new_repo(wt)
    (wt / ".gitignore").write_text(".tdd/\n")
    commit_all(wt, "initial")
    (wt / ".tdd").mkdir()
    (wt / ".tdd" / "issue-1-leaf.log").write_text("a leaf's log\n")
    run_discard(wt)
    assert (wt / ".tdd" / "issue-1-leaf.log").is_file(), "the discard block removed the ignored run-state file .tdd/issue-1-leaf.log"


@pytest.mark.process("git: a bash-run discard block under the repository's own .tdd ignore patterns")
def test_1420_skill_md_s_preflight_discard_never_loses_an_untracked_tdd_run_state_file_the_real_gitignore_un_ignores_the_refactor_owed_file_survives_uncaptured(tmp_path):
    wt = tmp_path / "wt"
    new_repo(wt)
    (wt / ".gitignore").write_text(".tdd/*\n!.tdd/issue-*.md\n.tdd/issue-*-spec.md\n")
    (wt / ".tdd").mkdir()
    (wt / ".tdd" / "issue-1.md").write_text("- [x] step one\n")
    commit_all(wt, "initial")
    (wt / ".tdd" / "issue-1-refactor-owed.md").write_text("a refactor the run owes\n")
    got = discard_stray(wt, tmp_path)
    assert (wt / ".tdd" / "issue-1-refactor-owed.md").is_file(), "the discard block removed the untracked run-state file .tdd/issue-1-refactor-owed.md"
    assert "issue-1-refactor-owed.md" not in got, f"$stray captures the run-state file as a stray: {got}"
