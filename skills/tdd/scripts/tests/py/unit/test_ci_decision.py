"""One case per row of wait-ci.sh's decision table: values in, a decision out, no fake of any kind."""
import dataclasses

import pytest
from veri.ci_decision import (
    Crash,
    Decision,
    Exit,
    Loop,
    Need,
    Observation,
    Options,
    Record,
    Remove,
    Sleep,
    decide,
    decimal,
    retry_sleep,
)
from veri.ci_marks import Marks

PR = "https://github.com/o/r/pull/1"
HEAD = "a" * 40
OTHER = "b" * 40
NOW = 10_000
DEADLINE_PATH = ".tdd/ci-deadline-" + HEAD
OPTS = Options(pr=PR, want="", explicit=False, on_pr="1", no_run_wait=600, queue_wait="3600", poll="10", span=540, total=600)
NO_MARKS = Marks(deadline=None, deadline_path=DEADLINE_PATH, queued=None, none=None)
FRESH = Loop()
CONFLICT = f"wait-ci.sh: {PR} conflicts with its base branch; no workflow will start until it is rebased\n"


def obs(state="pending", **fields):
    return Observation(state=state, **{"head": HEAD, "mergeable": True, **fields})


def decision(outcome, *effects, loop=FRESH):
    return Decision(outcome, tuple(effects), loop)


def pending_loop(**fields):
    return dataclasses.replace(FRESH, **{"slice_end": NOW + 540, "deadline": str(NOW + 600), "key": HEAD, **fields})


def run(observation, marks=NO_MARKS, loop=FRESH, now=NOW, **options):
    return decide(observation, marks, now, loop, dataclasses.replace(OPTS, **options))


ROWS = {
    "green is exit 0 and clears the none mark":
        (run(obs("green")), decision(Exit(0), Remove("none", HEAD))),
    "green on another head than the one wanted keeps waiting":
        (run(obs("green"), want=OTHER),
         decision(Sleep("10"), Remove("none", HEAD), Record("head", OTHER, str(NOW)), loop=Loop(slice_end=NOW + 540))),
    "red is exit 1 naming the failed checks":
        (run(obs("red", failed="a,b")), decision(Exit(1, "a,b\n"), Remove("none", HEAD))),
    "red with no names prints nothing":
        (run(obs("red")), decision(Exit(1), Remove("none", HEAD))),
    "red on another head than the one wanted keeps waiting":
        (run(obs("red", failed="a"), want=OTHER),
         decision(Sleep("10"), Remove("none", HEAD), Record("head", OTHER, str(NOW)), loop=Loop(slice_end=NOW + 540))),
    "no checks on a conflicting pull request is exit 2":
        (run(obs("none", mergeable=False)), decision(Exit(2, "", CONFLICT))),
    "only skipped checks on a conflicting pull request is exit 2":
        (run(obs("skipped", mergeable=False)), decision(Exit(2, "", CONFLICT))),
    "pending checks on a conflicting pull request are waited on":
        (run(obs("pending", mergeable=False)).outcome, Sleep("10")),
    "no checks with VERI_CI_ON_PR=0 is exit 0":
        (run(obs("none"), explicit=True, on_pr="0"),
         decision(Exit(0, "", f"wait-ci.sh: {PR} has no checks and VERI_CI_ON_PR=0 says none will come\n"))),
    "no checks with VERI_CI_ON_PR=0 on another head is still waited on":
        (run(obs("none", mergeable=None), explicit=True, on_pr="0", want=OTHER).outcome, Sleep("10")),
    "no checks and no workflow read yet asks for the probe":
        (run(obs("none")), decision(Need("workflow"))),
    "no checks and no pull_request workflow is exit 0":
        (run(obs("none", no_workflow=True)),
         decision(Exit(0, "", f"wait-ci.sh: {PR} has no checks and no workflow triggers on pull_request; no check will come\n"))),
    "green and red are answered before the clock is asked for":
        (run(obs("green"), now=None).outcome, Exit(0)),
    "red is answered before the clock is asked for":
        (run(obs("red", failed="x"), now=None).outcome, Exit(1, "x\n")),
    "every other wait asks for the clock before it reads a mark":
        (run(obs("pending"), now=None), decision(Need("now"))),
    "an early exit is answered before the clock is asked for":
        (run(obs("none", mergeable=False), now=None).outcome.code, 2),
    "an explicit VERI_CI_ON_PR=1 never asks for the probe":
        (run(obs("none", mergeable=None), explicit=True).outcome, Sleep("10")),
    "a first none sighting is recorded and waited on with a fresh deadline":
        (run(obs("none", no_workflow=False)),
         decision(Sleep("10"), Record("none", HEAD, str(NOW)), Record("deadline", HEAD, str(NOW + 600)),
                  loop=Loop(slice_end=NOW + 540, deadline=str(NOW + 600), key=HEAD, first_none=NOW, none_head=HEAD))),
    "a none sighting older than the no-run wait is exit 2":
        (run(obs("none", no_workflow=False), dataclasses.replace(NO_MARKS, none=NOW - 600)),
         decision(Exit(2, "", f"wait-ci.sh: no CI run for {HEAD}\n"), loop=Loop(first_none=NOW - 600, none_head=HEAD))),
    "a none sighting just younger than the no-run wait is waited on":
        (run(obs("none", no_workflow=False), dataclasses.replace(NO_MARKS, none=NOW - 599)).outcome, Sleep("10")),
    "a no-run wait of zero records the sighting, then exits 2":
        (run(obs("none", no_workflow=False), no_run_wait=0),
         decision(Exit(2, "", f"wait-ci.sh: no CI run for {HEAD}\n"), Record("none", HEAD, str(NOW)),
                  loop=Loop(first_none=NOW, none_head=HEAD))),
    "a none sighting already seen on this head is not read from the mark again":
        (run(obs("none", no_workflow=False), dataclasses.replace(NO_MARKS, none=NOW - 9999),
             pending_loop(first_none=NOW - 5, none_head=HEAD)).outcome, Sleep("10")),
    "a none sighting on a new head restarts the count":
        (run(obs("none", no_workflow=False), loop=pending_loop(first_none=NOW - 9999, none_head=OTHER)).loop.first_none,
         NOW),
    "no checks on a pull request whose mergeability is unknown start no count":
        (run(obs("none", mergeable=None, no_workflow=False)),
         decision(Sleep("10"), Record("deadline", HEAD, str(NOW + 600)),
                  loop=Loop(slice_end=NOW + 540, deadline=str(NOW + 600), key=HEAD))),
    "only skipped checks are pending, and clear the none mark":
        (run(obs("skipped")),
         decision(Sleep("10"), Remove("none", HEAD), Record("deadline", HEAD, str(NOW + 600)),
                  loop=Loop(slice_end=NOW + 540, deadline=str(NOW + 600), key=HEAD))),
    "a first queued sighting is recorded and slept on, with no deadline":
        (run(obs(queued=True)),
         decision(Sleep("10"), Remove("none", HEAD), Record("queued", HEAD, str(NOW)), loop=Loop(slice_end=NOW + 540))),
    "queued longer than the queue wait is exit 2":
        (run(obs(queued=True), dataclasses.replace(NO_MARKS, queued=NOW - 3601)),
         decision(Exit(2, "", f"wait-ci.sh: checks of {PR} never started: queued since {NOW - 3601}\n"),
                  Remove("none", HEAD), loop=Loop(slice_end=NOW + 540))),
    "queued exactly as long as the queue wait is waited on":
        (run(obs(queued=True), dataclasses.replace(NO_MARKS, queued=NOW - 3600)).outcome, Sleep("10")),
    "queued names the wanted sha for its mark":
        (run(obs(queued=True), want=HEAD).effects, (Remove("none", HEAD), Record("queued", HEAD, str(NOW)))),
    "queued on another head than the one wanted records no queued mark":
        (run(obs(queued=True), want=OTHER).effects, (Remove("none", HEAD), Record("head", OTHER, str(NOW)))),
    "queued at the end of the slice is exit 3":
        (run(obs(queued=True), loop=Loop(slice_end=NOW)).outcome, Exit(3)),
    "a mismatched head at the end of the slice is exit 3":
        (run(obs(), want=OTHER, span=0).outcome, Exit(3)),
    "a bad queue wait is a crash after the sighting is recorded":
        (run(obs(queued=True), queue_wait="soon").effects[-1], Record("queued", HEAD, str(NOW))),
    "pending with no deadline mark records one":
        (run(obs()),
         decision(Sleep("10"), Remove("none", HEAD), Record("deadline", HEAD, str(NOW + 600)),
                  loop=Loop(slice_end=NOW + 540, deadline=str(NOW + 600), key=HEAD))),
    "pending on a draft with no deadline mark is exit 2":
        (run(obs(draft=True)),
         decision(Exit(2, "", f"wait-ci.sh: {PR} is a draft; mark it ready before waiting on its checks\n"),
                  Remove("none", HEAD), loop=Loop(slice_end=NOW + 540))),
    "pending on a draft inherits a recorded deadline":
        (run(obs(draft=True), dataclasses.replace(NO_MARKS, deadline=str(NOW + 100) + "\n")),
         decision(Sleep("10"), Remove("none", HEAD),
                  loop=Loop(slice_end=NOW + 540, deadline=str(NOW + 100), key=HEAD, inherited=True))),
    "an inherited deadline is read as a whole number":
        (run(obs(), dataclasses.replace(NO_MARKS, deadline="00%d\n" % (NOW + 100))).loop.deadline, str(NOW + 100)),
    "an unreadable deadline file is exit 2 naming it":
        (run(obs(), dataclasses.replace(NO_MARKS, deadline="soon")),
         decision(Exit(2, "", f"wait-ci.sh: deadline file {DEADLINE_PATH} is unreadable or not a non-negative whole number\n"),
                  Remove("none", HEAD), loop=Loop(slice_end=NOW + 540))),
    "an empty deadline file is exit 2":
        (run(obs(), dataclasses.replace(NO_MARKS, deadline="")).outcome.code, 2),
    "an inherited deadline that has passed is exit 2":
        (run(obs(), dataclasses.replace(NO_MARKS, deadline=str(NOW))),
         decision(Exit(2, "", f"wait-ci.sh: checks of {PR} still pending past the deadline recorded for {HEAD}\n"),
                  Remove("none", HEAD),
                  loop=Loop(slice_end=NOW + 540, deadline=str(NOW), key=HEAD, inherited=True))),
    "a deadline made this call that has passed is exit 3":
        (run(obs(), total=0),
         decision(Exit(3), Remove("none", HEAD), Record("deadline", HEAD, str(NOW)),
                  loop=Loop(slice_end=NOW + 540, deadline=str(NOW), key=HEAD))),
    "a later poll keeps the deadline of the first and ignores the mark":
        (run(obs(), dataclasses.replace(NO_MARKS, deadline="1"), pending_loop(), now=NOW + 5).outcome, Sleep("10")),
    "a later poll past the inherited deadline is exit 2 naming the first key":
        (run(obs(), loop=pending_loop(inherited=True, key=OTHER), now=NOW + 600).outcome,
         Exit(2, "", f"wait-ci.sh: checks of {PR} still pending past the deadline recorded for {OTHER}\n")),
    "pending at the end of the slice is exit 3":
        (run(obs(), loop=pending_loop(), now=NOW + 540).outcome, Exit(3)),
    "the sleep is the poll as given":
        (run(obs(), poll="0.5").outcome, Sleep("0.5")),
}


@pytest.mark.parametrize("name", ROWS)
def test_decide_row(name):
    got, expected = ROWS[name]
    assert got == expected


def test_a_bad_queue_wait_is_a_crash_with_the_value_error():
    outcome = run(obs(queued=True), queue_wait="soon").outcome

    assert isinstance(outcome, Crash) and isinstance(outcome.error, ValueError)


def test_a_mismatched_head_first_seen_records_a_head_mark_and_one_seen_differing_for_the_head_wait_is_exit_2_naming_both_shas_issue_3978():
    first = run(obs(), want=OTHER)
    later = run(obs(), dataclasses.replace(NO_MARKS, head=NOW - 600), want=OTHER, head_wait=600)
    younger = run(obs(), dataclasses.replace(NO_MARKS, head=NOW - 599), want=OTHER, head_wait=600)

    assert (first.outcome, Record("head", OTHER, str(NOW)) in first.effects, later.outcome, younger.outcome) == (
        Sleep("10"), True,
        Exit(2, "", f"wait-ci.sh: {PR} still reports head {HEAD}, not the expected {OTHER}, 600 s after it was first seen differing\n"),
        Sleep("10"))


@pytest.mark.parametrize("observation, options", [
    (obs("none"), {"explicit": True, "on_pr": "0"}),
    (obs("none", no_workflow=True), {}),
    (obs("none", no_workflow=True, head=OTHER), {}),
], ids=["no checks with VERI_CI_ON_PR=0", "no checks and no pull_request workflow",
        "no checks and no pull_request workflow on another head"])
def test_an_early_exit_0_on_the_expected_head_removes_its_head_mark_issue_3978(observation, options):
    decided = run(observation, dataclasses.replace(NO_MARKS, head=NOW - 100), want=HEAD, **options)

    assert (decided.outcome.code, Remove("head", HEAD) in decided.effects) == (0, True)


def test_decide_leaves_the_observation_marks_and_loop_it_was_given_unchanged():
    observation, loop = obs(queued=True), Loop(slice_end=NOW + 1)

    run(observation, NO_MARKS, loop)

    assert (observation, NO_MARKS, loop) == (obs(queued=True), Marks(None, DEADLINE_PATH, None, None), Loop(slice_end=NOW + 1))


@pytest.mark.parametrize("poll, unread, backoff, expected", [
    ("10", 1, "1", "10"), ("10", 2, "1", "20"), ("10", 3, "1", "40"), ("10", 4, "1", "60"), ("10", 9, "1", "60"),
    ("0.5", 2, "1", "1"), ("soon", 2, "1", "soon"), ("10", 5, "0", "10"),
])
def test_retry_sleep_doubles_from_the_poll_to_a_cap_of_sixty_unless_backoff_is_off(poll, unread, backoff, expected):
    assert retry_sleep(poll, unread, backoff) == expected


@pytest.mark.parametrize("text, expected", [("0", "0"), ("0012", "12"), ("", None), ("-1", None), ("1.5", None), ("1 ", None)])
def test_decimal_reads_a_non_negative_whole_number_or_none(text, expected):
    assert decimal(text) == expected
