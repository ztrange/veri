"""In-process cases for CLAUDE.md as a record of its own rules."""
import re

from skill_sections import ROOT, plain

CLAUDE_MD = ROOT / "CLAUDE.md"
IDIOM_HEADING = "## Testing idiom"


def split_records(lines):
    records, rec = [], ""
    for line in lines:
        if re.match(r"([-*] |\| )", line):
            if rec != "":
                records.append(rec)
            rec = line
        elif re.match(r"\s*$", line):
            if rec != "":
                records.append(rec)
            rec = ""
        elif rec == "":
            rec = line
        else:
            rec = rec + " " + line
    if rec != "":
        records.append(rec)
    return [plain(r) for r in records]


def all_records():
    return split_records(CLAUDE_MD.read_text().splitlines())


def section_records(heading):
    inside, body = False, []
    for line in CLAUDE_MD.read_text().splitlines():
        if not inside:
            inside = line == heading
        elif line.startswith("## "):
            break
        else:
            body.append(line)
    return split_records(body)


def one_record_matches(records, regexes):
    return any(all(re.search(r, rec) for r in regexes) for rec in records)


def records_carry(records, problem, *regexes):
    return [] if one_record_matches(records, regexes) else [problem]


def idiom_records_carry(unread, problem, *regexes):
    records = section_records(IDIOM_HEADING)
    if not records:
        return [f"CLAUDE.md has no '{IDIOM_HEADING}' section to read, so {unread}"]
    return records_carry(records, problem, *regexes)


ROSTER = """make test is the baseline, and a red one stops a run before it starts;make test;baseline|stay green;refuse|refus
make docs publishes the page by hand only, never on a merge;make docs;by hand|disabled;publish|deploy
make install-hooks installs the tag hook once per clone and refuses to clobber a foreign one;install-hooks;reference-transaction;refus|clobber
make merge-gates runs before a merge and which gates a change owes, including what is exempt;merge-gates;before merging|merging any pr;nothing for;skills/;adr;makefile
docs-check is not part of make test, nor in CI, so documentation lag never blocks a run;docs-check;not.*part of;block|never
CONTEXT.md is where the glossary lives;context.md;glossar|terms
walkthrough.html is generated and never hand-edited;walkthrough;generat;never edit|by hand
the page build fails on a bad reference but only reports a line no commentary claims;fail;chunk|commentary;owed
exit code 1 is a clean negative — a real answer;clean negative|1 ;reject|leaf ran and failed
exit code 2 is no answer obtained;no answer;killed-stuck|unparseable|bad argument
exit code 3 is nothing to do, and not an error;nothing to do;not an error
1 and 2 are never collapsed — a process failure is not a system failure;never collapse|not collapse;process;system
a version is an annotated tag whose message is the capability, and nothing else keeps it;annotated;capability;changelog|version file
git tag is sorted with -v:refname, never plain sort;sort=-v:refname;lexical|v0.9
a backfilled tag needs GIT_COMMITTER_DATE;git_committer_date;backfill|retro
a regen commit built at the tag is not the fixpoint — build, commit, rebuild, amend;amend;unreleased;docs-check|fixpoint
every leaf is launched through supervise.sh and nothing bypasses it;supervise.sh;never|only|bypass
the verifier is blind by construction — the prompt builder takes no rationale;blind;build-verify-prompt.sh;rationale|leak
the committed ledger is the source of truth, and the refactor-pending mark is what a resumed run reads;ledger;source of truth;refactor pending
the three budgets are three axes and are never merged;veri_stuck_retries;revise_budget;veri_refactor_budget;never merged|one knob
the git questions a walkthrough build asks are a pinned budget;once per script;budget|pins;git
a tag changes the page without a commit, and the hook only notices;tag;hook;notice|never rebuild
a test injects rather than waiting on a real model or a real clock, which is why every tunable has a default;claude_bin;veri_heartbeat;:-default
a guard never watched to fail is not tested;guard|failure path;not tested|watched;break"""


def test_claude_md_still_states_every_rule_it_is_the_only_record_of_in_full_or_in_one_sentence_with_a_pointer():
    records = all_records()
    problems = []
    if not records:
        problems.append("CLAUDE.md could not be read, so no rule could be looked for in it")
    else:
        for row in ROSTER.splitlines():
            rule, *regexes = row.split(";")
            problems += records_carry(records, f"CLAUDE.md has no single record stating that {rule}", *regexes)
    assert problems == []


def test_claude_mds_budgets_invariant_names_veri_no_verdict_retries_as_a_fourth_axis_and_why_it_is_not_merged_with_veri_stuck_retries():
    assert records_carry(
        all_records(),
        "CLAUDE.md has no single record naming VERI_NO_VERDICT_RETRIES as a fourth budget axis beside VERI_STUCK_RETRIES, liveness against protocol compliance, never merged",
        "veri_no_verdict_retries", "veri_stuck_retries", "four",
        "liveness", "protocol|contract|compliance", "never merged|not merged|one knob",
    ) == []


def test_claude_mds_blind_verifier_invariant_names_the_refactor_base_sha_parameter_and_why_a_sha_cannot_leak_rationale():
    assert records_carry(
        all_records(),
        "CLAUDE.md has no single record naming <base-sha> as the refactor phase parameter of build-verify-prompt.sh in the blind-verifier invariant, and why a hex sha cannot leak rationale",
        "blind", r"build-verify-prompt\.sh", "base.sha", "refactor",
        "hex|0-9a-f", "rationale|leak",
    ) == []


def test_claude_mds_budgets_invariant_names_veri_step_growth_as_a_fifth_axis_plan_growth_never_merged_with_the_other_four():
    assert records_carry(
        all_records(),
        "CLAUDE.md has no single record naming VERI_STEP_GROWTH as a fifth budget axis beside the other four, plan growth, never merged",
        "veri_step_growth", "veri_refactor_budget", "five",
        "plan", "never merged|not merged|one knob",
    ) == []
