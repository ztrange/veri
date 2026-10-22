"""Cases for what skills/tdd/SKILL.md tells the conductor about the commit of the skill a run is executing."""
import importlib
import pathlib
import re

SKILL = pathlib.Path(__file__).resolve().parents[4] / "SKILL.md"
README = pathlib.Path(__file__).resolve().parents[6] / "README.md"
CLAUDE = pathlib.Path(__file__).resolve().parents[6] / "CLAUDE.md"

PLAN = "### 2. Scope & plan → the ledger"
SCRIPTS = "## The scripts (this skill's `scripts/` directory)"
LAUNCH = "## Launching the conductor"


def _lines(heading, doc=SKILL):
    section = importlib.import_module("skill_sections").section(doc, heading)
    lines = section.splitlines()[1:]
    for i, line in enumerate(lines):
        if line.startswith("#"):
            return lines[:i]
    return lines


def _items(lines):
    records, rec = [], ""
    for line in lines:
        if re.match(r"[0-9]+\. ", line):
            if rec:
                records.append(rec)
            rec = line
        elif not line.strip():
            if rec:
                records.append(rec)
            rec = ""
        elif rec:
            rec = rec + " " + line
    if rec:
        records.append(rec)
    return [r.lower() for r in records]


def _paragraphs(lines):
    records, rec, in_item = [], "", False
    for line in lines:
        if not line.strip():
            if rec:
                records.append(rec)
            rec, in_item = "", False
        elif re.match(r"([0-9]+\.|[-*]) ", line):
            in_item = True
        elif in_item:
            continue
        else:
            rec = line if not rec else rec + " " + line
    if rec:
        records.append(rec)
    return [r.lower() for r in records]


def _records(lines):
    records, rec = [], ""
    for line in lines:
        if re.match(r"([0-9]+\.|[-*]) ", line):
            if rec:
                records.append(rec)
            rec = line
        elif not line.strip():
            if rec:
                records.append(rec)
            rec = ""
        else:
            rec = line if not rec else rec + " " + line
    if rec:
        records.append(rec)
    return [r.replace("*", "").replace("`", "").lower() for r in records]


def claim(paras, what, *patterns):
    if any(all(re.search(p, para) for p in patterns) for para in paras):
        return None
    return f"SKILL.md prose: no paragraph {what}"


def test_skill_md_s_plan_comment_names_the_skill_commit_the_run_started_on():
    plan_item = "\n".join(i for i in _items(_lines(PLAN)) if re.search("plan.*comment", i))
    problems = []
    if not plan_item:
        problems.append("SKILL.md's 'Scope & plan' section has no numbered item posting the plan comment")
    else:
        for word in ("skill", "commit"):
            if word not in plan_item:
                problems.append(f"SKILL.md's plan-comment item never says '{word}': {plan_item[:120]}")
    assert problems == []


def test_skill_md_says_what_a_change_to_the_skill_means_for_a_running_conductor_and_that_the_event_log_records_each_leaf_s_commit():
    paras = _paragraphs(_lines(SCRIPTS))
    assert paras != []
    problems = [
        claim(paras, "says the installed skill can change under a running conductor",
              "chang|move|update", "conductor|mid-run|running|under a run"),
        claim(paras, "names the event log as what records which commit each leaf used",
              r"event log|events\.jsonl", "commit"),
    ]
    assert [p for p in problems if p] == []


def test_skill_md_documents_the_skill_snapshot_veri_new_skill_and_issue_n_skill_commit_and_claude_md_cross_references_them():
    problems = []
    for doc in (SKILL, README, CLAUDE):
        text = doc.read_text().replace("*", "").replace("`", "").lower()
        if not text:
            problems.append(f"{doc} could not be read")
            continue
        for term in ("skill snapshot", "veri_new_skill", r"issue-[^\s/]+-skill-commit"):
            if not re.search(term, text):
                problems.append(f"{doc} never mentions /{term}/")
    assert problems == []


def test_skill_md_s_s_paragraph_no_longer_says_nothing_pins_it_and_says_the_skill_snapshot_pins_the_commit_a_run_executes_under():
    paras = _paragraphs(_lines(SCRIPTS))
    assert paras != []
    stale = [p for p in paras if "nothing here pins it" in p]
    problems = [
        f"still says 'nothing here pins it': {stale[0][:120]}" if stale else None,
        claim(paras, "about $S says the skill snapshot pins the commit a run executes under",
              r"\$s", "pin", "veri_skill_commit", r"issue-[^\s/]+-skill-commit"),
    ]
    assert [p for p in problems if p] == []


def test_866_skill_md_s_skill_snapshot_says_the_record_survives_only_a_run_past_preflight_decided_after_the_conductor_exits_by_a_registered_worktree_or_a_local_branch_not_the_exit_code():
    records = _records(_lines(LAUNCH, README))
    patterns = ["skill-commit|record", "preflight", "regist[a-z]* .*worktree|worktree .*regist",
                r"\.tdd/wt/", "tdd/<n>-", "branch", "exit (code|status)", "not|never|whatever"]
    assert any(all(re.search(p, r) for p in patterns) for r in records), \
        "no paragraph or bullet says the skill-commit record survives only a run past preflight"


def test_865_skill_md_s_skill_snapshot_resolves_the_default_branch_from_the_remote_when_origin_head_is_absent_refuses_with_exit_2_when_it_cannot_and_runs_unpinned_only_with_no_resolvable_commit_at_all():
    lines = _lines(LAUNCH, README)
    start = next((i for i, line in enumerate(lines) if line.startswith("**The skill snapshot")), None)
    assert start is not None, "no '**The skill snapshot' paragraph"
    paras = _records(lines[start:])
    problems = [
        claim(paras, "says that with refs/remotes/origin/HEAD absent the launch resolves the default branch from the remote",
              "refs/remotes/origin/head", "absent|missing|no refs/remotes/origin/head", "ls-remote|from the remote|remote itself"),
        claim(paras, "says that when the remote default cannot be resolved the launch exits 2",
              "refs/remotes/origin/head", "exit 2", "cannot|can not|fails"),
        claim(paras, "says the launch runs unpinned when no commit can be resolved at all",
              "unpinned", "no (skill )?commit", "at all"),
    ]
    assert [p for p in problems if p] == []


def test_1785_launching_the_conductor_lives_in_readme_after_install_and_not_in_skill_md():
    moved = ["**Three launch modes", "**The skill snapshot:", "**The record survives only a run"]
    skill = SKILL.read_text()
    readme = README.read_text()
    section = readme.partition("\n## Launching the conductor")[2].split("\n## ")[0]
    assert [t for t in [LAUNCH] + moved if t in skill] == [], "SKILL.md still carries text that moved to README.md"
    assert "\n## Install" in readme and readme.index("\n## Install") < readme.index("\n" + LAUNCH), \
        "README.md has no '## Launching the conductor' after '## Install'"
    assert [t for t in moved if t not in section] == [], "README.md's section lacks moved text"


def test_1785_skill_md_points_the_pinned_snapshot_and_the_leaf_launchable_exit_2_at_readme():
    scripts = " ".join(" ".join(_lines(SCRIPTS)).replace("`", "").replace("*", "").split())
    pin = scripts[scripts.index("not the clone's current tip"):][:400]
    ref = re.compile(r"README\.md\W+(s )?Launching the conductor")
    problems = []
    if not ref.search(pin):
        problems.append("The scripts' pinned $S paragraph does not name README.md's Launching the conductor")
    if "below" in pin.split("Every launch")[0]:
        problems.append("The scripts' pinned $S paragraph still points below")
    assert problems == []
