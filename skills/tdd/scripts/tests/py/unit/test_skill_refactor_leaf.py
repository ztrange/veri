"""Cases for the shape of the refactor phase skills/tdd/SKILL.md prescribes, read as text."""
import pathlib
import re

from skill_sections import has, plain_bytes as plain

SKILL = pathlib.Path(__file__).resolve().parents[4] / "SKILL.md"
ROOT = pathlib.Path(__file__).resolve().parents[6]
CONTEXT = ROOT / "CONTEXT.md"
CLAUDE = ROOT / "CLAUDE.md"

ONE_LEAF = r"(one|a single) (refactor |developer |transform )?leaf"
AMENDMENT = r"amend|ledger (step|line)|add-ledger-step|grow"


def either_order(first, second, between):
    return f"(({first}){between}({second})|({second}){between}({first}))"


def records_of(path):
    records = []
    rec = None

    def flush():
        if rec:
            records.append(plain(re.sub(rb"\s+", b" ", rec)))

    for line in pathlib.Path(path).read_bytes().split(b"\n"):
        if re.match(rb"[0-9]+\. ", line) or re.match(rb"\s*- ", line):
            flush()
            rec = line
        elif not line.strip():
            flush()
            rec = None
        elif not rec:
            rec = line
        else:
            rec += b" " + line
    flush()
    return records


def record(path, *patterns):
    return next((r for r in records_of(path) if all(re.search(p.encode(), r) for p in patterns)), b"")


def adr_pointer(text):
    return any(int(re.search(rb"[0-9]+$", ref).group()) != 10 for ref in re.findall(rb"adr[- ]?[0-9]+", text))


def test_context_md_s_cycle_entry_and_claude_md_s_budget_invariant_describe_one_refactor_leaf_per_step_and_point_at_the_adr_that_records_it():
    cycle = record(CONTEXT, r"^cycle:")
    invariant = record(CLAUDE, r"veri_stuck_retries", r"revise_budget", r"veri_refactor_budget")

    assert cycle, "CONTEXT.md has no Cycle glossary entry to read"
    assert has(cycle, ONE_LEAF), "the Cycle entry never says the refactor step is one leaf"
    stale_cycle = re.search(rb"per leaf|until none remain|per leaf invocation", cycle)
    assert stale_cycle is None, f"the Cycle entry still says {stale_cycle and stale_cycle.group()!r}"

    assert invariant, "CLAUDE.md has no invariant naming all three budgets to read"
    assert has(invariant, ONE_LEAF), "the budget invariant never says one leaf spends the step's refactor budget"
    stale_invariant = re.search(rb"asked for one always finds one|one transform per leaf|a transform per leaf", invariant)
    assert stale_invariant is None, f"the budget invariant still explains the budget by {stale_invariant and stale_invariant.group()!r}"

    assert adr_pointer(cycle + b" " + invariant), "neither entry names an ADR other than the superseded 0010"


def whole_document():
    return plain(SKILL.read_bytes()).replace(b"\n", b" ")


def test_skill_md_grows_the_plan_from_the_refactor_leaf_s_flags_classes_alone_reading_no_new_step_or_candidates_line_of_the_leaf_s_into_it():
    whole = whole_document()
    leaf_new_step = re.search(either_order("leaf's", "new_step", "[^.]{0,30}").encode(), whole)
    assert leaf_new_step is None, f"still reads a NEW_STEP: line from the refactor leaf: {leaf_new_step and leaf_new_step.group()!r}"
    candidate_growth = re.search(either_order("candidates:", f"({AMENDMENT})", "[^.]{0,80}").encode(), whole)
    assert candidate_growth is None, f"grows the plan from the leaf's CANDIDATES: lines: {candidate_growth and candidate_growth.group()!r}"
