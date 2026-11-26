"""Characterization of veri/metrics.py: one rich journal that exercises every section of the report, whose
whole rendered page is pinned byte for byte, so a refactor of how the numbers are computed or laid out shows."""
import importlib
import json

import pytest


@pytest.fixture
def metrics():
    return importlib.import_module("veri.metrics")


def _event(ts, actor, phase, step, event, attempt="", **fields):
    return {"ts": ts, "awake": ts - 1000, "issue": "108", "actor": actor, "phase": phase, "step": step,
            "event": event, "attempt": str(attempt), **fields}


def _usage(model, turns, dollars, tokens, api_ms):
    return dict(zip(["input_tokens", "output_tokens", "cache_read_input_tokens", "cache_creation_input_tokens"],
                    map(str, tokens), strict=True),
                duration_ms="0", duration_api_ms=str(api_ms), num_turns=str(turns), total_cost_usd=dollars,
                model=model)


def _leaf(step, ts, actor, phase, attempt, secs, name, status="0", usage=None, verdict=None, retries=0):
    events = [_event(ts, actor, phase, step, "launch", attempt, name=name)]
    events += [_event(ts + i + 1, actor, phase, step, "retry", attempt, cause="no heartbeat")
               for i in range(retries)]
    events.append(_event(ts + secs, actor, phase, step, "exit", attempt, status=status, secs=str(secs)))
    if usage is not None:
        events.append(_event(ts + secs, actor, phase, step, "usage", attempt, **usage))
    if verdict is not None:
        events.append(_event(ts + secs, actor, phase, step, "verdict", attempt, verdict=verdict))
    return events


def rich_events():
    opus, sonnet = "claude-opus-5-5", "claude-sonnet-4"
    e = _event
    events = [e(1000, "conductor", "", "", "resume"),
              e(1005, "conductor", "", "", "suite-flake", files="a_test.py,b_test.py")]
    # step "one": red rejected then revised, green, a refactor pass revised once, a split and a crossing.
    events += [e(1010, "conductor", "", "one", "step-start")]
    events += _leaf("one", 1020, "developer", "red", 1, 90, "develop-red", usage=_usage(sonnet, 5, "0.40", (100, 200, 300, 400), 70000), retries=2)
    events += _leaf("one", 1120, "verifier", "red", 1, 20, "verify-red", usage=_usage(sonnet, 2, "0.10", (10, 20, 30, 40), 15000), verdict="REJECT")
    events += [e(1141, "conductor", "red", "one", "revise", 1, budget="3")]
    events += _leaf("one", 1150, "developer", "red", 2, 60, "revise-red", status="2", usage=_usage(opus, 4, "0.30", (50, 60, 70, 80), 50000))
    events += _leaf("one", 1250, "developer", "red", 3, 60, "revise-red", usage=_usage(opus, 4, "0.35", (50, 60, 70, 80), 51000))
    events += _leaf("one", 1320, "verifier", "red", 3, 20, "verify-red", usage=_usage(sonnet, 2, "0.10", (10, 20, 30, 40), 15000), verdict="PASS")
    events += [e(1345, "conductor", "", "one", "relaunch", 1, cause="no-verdict")]
    events += _leaf("one", 1350, "developer", "green", 1, 100, "develop-green", usage=_usage(sonnet, 9, "0.70", (200, 300, 400, 500), 80000))
    events += _leaf("one", 1460, "verifier", "green", 1, 20, "verify-green", usage=_usage(sonnet, 3, "0.20", (20, 30, 40, 50), 10000), verdict="PASS")
    events += _leaf("one", 1490, "developer", "refactor", 1, 70, "develop-refactor", usage=_usage(sonnet, 6, "0.55", (60, 70, 80, 90), 30000))
    events += _leaf("one", 1565, "verifier", "refactor", 1, 20, "verify-refactor", usage=_usage(sonnet, 2, "0.12", (10, 20, 30, 40), 9000), verdict="REJECT")
    events += [e(1590, "conductor", "refactor", "one", "revise", 1, budget="2")]
    events += [e(1595, "conductor", "refactor", "one", "refactor", 1, transforms="2", budget="5", stopped="candidates-done", **{"pass": "1"})]
    events += _leaf("one", 1600, "developer", "refactor", 2, 50, "revise-refactor", usage=_usage(opus, 5, "0.60", (60, 70, 80, 90), 25000))
    events += _leaf("one", 1655, "verifier", "refactor", 2, 20, "verify-refactor", usage=_usage(sonnet, 2, "0.12", (10, 20, 30, 40), 9000), verdict="PASS")
    events += [e(1680, "conductor", "refactor", "one", "refactor", 2, transforms="1", budget="5", stopped="budget-spent", **{"pass": "2"})]
    events += [e(1685, "conductor", "", "one", "step-over-budget", spent="9"),
               e(1686, "conductor", "", "one", "step-split", at="red"),
               e(1690, "conductor", "", "one", "test-run", tier="fast", seconds="12"),
               e(1691, "conductor", "", "one", "test-run", tier="fast", seconds="13"),
               e(1692, "conductor", "", "one", "test-run", tier="full", seconds="140"),
               e(1693, "conductor", "", "one", "test-run", tier="", seconds="7"),
               e(1694, "conductor", "", "one", "test-run", tier="full", seconds=""),
               e(1700, "conductor", "", "one", "step-done")]
    # step "two": a wasted attempt (never recovered), an adjudication, a verifier switched off.
    events += [e(1710, "conductor", "", "two", "step-start")]
    events += _leaf("two", 1720, "developer", "red", 1, 30, "develop-red", usage=_usage(sonnet, 3, "0.25", (5, 6, 7, 8), 4000))
    events += _leaf("two", 1760, "verifier", "red", 1, 15, "verify-red", usage=_usage(sonnet, 1, "0.05", (1, 2, 3, 4), 1000), verdict="REJECT")
    events += [e(1780, "conductor", "", "two", "adjudicated", cause="x", outcome="retry", reason="r"),
               e(1781, "conductor", "", "two", "adjudicated", cause="x", outcome="bail", reason="r"),
               e(1782, "conductor", "refactor", "two", "verify-refactor-skipped", reason="switched-off")]
    # step "three": a pin; step "four": a pin-satisfied verdict; "five": cover/transform only; "six": reroute repair.
    events += [e(1800, "conductor", "", "three", "step-start")]
    events += _leaf("three", 1805, "verifier", "pin", 1, 10, "verdict-pin", usage=_usage(sonnet, 1, "0.08", (1, 1, 1, 1), 500), verdict="PASS")
    events += [e(1820, "conductor", "pin", "three", "pin"), e(1830, "conductor", "", "three", "step-done")]
    events += [e(1840, "conductor", "", "five", "step-start")]
    events += _leaf("five", 1845, "developer", "cover", 1, 10, "develop-cover", usage=_usage(sonnet, 1, "0.02", (1, 1, 1, 1), 500))
    events += [e(1860, "conductor", "", "five", "step-done")]
    events += [e(1870, "conductor", "", "six", "step-start"),
               e(1871, "conductor", "red", "six", "reroute", kind="repair", budget="4"),
               e(1900, "conductor", "", "six", "step-done")]
    events += [e(5000, "conductor", "", "", "structural-pass", transforms="1", budget="3", stopped="budget-spent"),
               e(5100, "conductor", "", "", "done", pr="https://github.com/ztrange/veri/pull/999")]
    return events


def build_rich_root(root):
    tdd = root / ".tdd"
    tdd.mkdir()
    (tdd / "events.jsonl").write_text("".join(json.dumps(event) + "\n" for event in rich_events()))
    (tdd / "issue-108.md").write_text("# Plan\n- [x] one\n- [x] two\n- [ ] three\n- [x] full-suite\n")
    (tdd / "issue-108-conductor-model").write_text("opus\n")
    (tdd / "issue-108-skip-verify").write_text("refactor,green\n")

    def turn(msg, output_tokens, body=None, model="claude-opus-5-5", cache_read=100000):
        content = [{"type": "text", "text": "working"}]
        if body is not None:
            content.append({"type": "tool_use", "name": "Bash", "input": {"command": "gh issue comment 108 --body '%s'" % body}})
        return {"type": "assistant", "message": {"id": msg, "model": model, "content": content,
                                                 "usage": {"input_tokens": 10, "output_tokens": output_tokens * 1000,
                                                           "cache_read_input_tokens": cache_read,
                                                           "cache_creation_input_tokens": 50}}}

    records = [{"type": "system", "subtype": "init"},
               turn("m1", 100, "🟢 Green: step 1"), turn("m2", 40, "🔎 verify-green: PASS"), turn("m3", 7),
               turn("m4", 30, "✅ Step done: one", model="claude-sonnet-4"),
               {"type": "result", "total_cost_usd": 1.0, "num_turns": 4, "usage": {"output_tokens": 177000}},
               {"type": "system", "subtype": "init"},
               turn("m5", 60, "⛔ Bailed: stuck", cache_read=400000), turn("m6", 11, "🛠️ Refactor: pass", cache_read=900000)]
    (tdd / "conductor-108.log").write_text("".join(json.dumps(r) + "\n" for r in records))

    transcripts = root / "transcripts"
    transcripts.mkdir()
    for name, prompt in (("dev.jsonl", "/vdev 3154"),):
        lines = [{"type": "user", "message": {"role": "user", "content": prompt}}]
        for number in range(3):
            lines.append({"type": "assistant", "timestamp": "1970-01-01T00:30:00+00:00" if number else "1970-01-01T00:00:01+00:00",
                          "message": {"id": "%s_%d" % (name, number), "model": "claude-opus-4",
                                      "usage": {"input_tokens": 1000, "cache_read_input_tokens": 50000 * (number + 1),
                                                "cache_creation_input_tokens": 10, "output_tokens": 500}}})
        (transcripts / name).write_text("".join(json.dumps(line) + "\n" for line in lines))
    return transcripts


def rich_report(root, monkeypatch, metrics):
    transcripts = build_rich_root(root)
    monkeypatch.chdir(root)
    monkeypatch.setenv("VERI_SESSION_TRANSCRIPTS", str(transcripts))
    monkeypatch.setenv("VERI_MODEL", "opus")
    monkeypatch.setenv("VERI_MODEL_DEVELOPER", "sonnet")
    monkeypatch.setenv("VERI_LABEL", "lane-x")
    return metrics.report("108", ".tdd/events.jsonl", ".tdd/issue-108.md")


EXPECTED = """### 📊 Metrics — issue 108

Wall time for the issue: 4100 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 4 of 4 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/999.
Lane: lane-x
Suite flakes: a_test.py, b_test.py.
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $2.68 over 6 turns, in 2 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 100060 tokens, largest 100060 tokens
Conductor context: first turn 400060 tokens, largest 900060 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.02 | 100060 |
| 2 | $0.02 | 100060 |
| 3 | $0.02 | 100060 |
| 4 | unpriced | 100060 |
| 5 | $0.08 | 400060 |
| 6 | $0.18 | 900060 |

#### Conductor comments, by family

| family | turns | output tokens | dollars |
| --- | ---: | ---: | ---: |
| ✅ Step done | 1 | 44250 | $0.00 |
| ✅ Done | 0 | 0 | $0.00 |
| 🔴 Red | 0 | 0 | $0.00 |
| 🟢 Green | 1 | 44250 | $0.89 |
| 🛠️ Refactor | 1 | 11000 | $0.22 |
| 🔎 verify-green | 1 | 44250 | $0.89 |
| 🔎 verify-refactor | 0 | 0 | $0.00 |
| 🔎 verify-<phase> (revised) | 0 | 0 | $0.00 |
| 🗺️ Plan | 0 | 0 | $0.00 |
| 🗺️ verify-plan | 0 | 0 | $0.00 |
| ▶️ Resuming | 0 | 0 | $0.00 |
| ⛔ Bailed | 1 | 60000 | $1.20 |
| ⏹️ Stopped | 0 | 0 | $0.00 |
| Total | 5 | 203750 | $3.19 |

#### Conductor by phase (estimated: each turn placed by its timestamp)

| phase | turns | $ |
| --- | ---: | ---: |
| untimed | 6 | unknown |

Models requested: VERI_MODEL opus, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER unset, VERI_MODEL_REVISE unset, VERI_MODEL_REVISE_GREEN unset, VERI_EFFORT_VERIFIER unset; models that answered: claude-opus-5-5, claude-sonnet-4.
⚠️ Unverified phases: refactor,green
Verifiers switched off: refactor 1
Dev session: 2 turns, 250000 cache tokens read, $0.48

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 7 | 1 | 2 | 1 | 295 | 206 | 21 | 226 | 368 | 510 | 652 | 1.55 |
| green | 2 | 1 | 0 | 0 | 120 | 90 | 12 | 220 | 330 | 440 | 550 | 0.90 |
| refactor | 4 | 1 | 1 | 0 | 160 | 73 | 15 | 140 | 180 | 220 | 260 | 1.39 |
| pin | 1 | 1 | 0 | 0 | 10 | 0 | 1 | 1 | 1 | 1 | 1 | 0.08 |
| cover | 1 | 0 | 0 | 0 | 10 | 0 | 1 | 1 | 1 | 1 | 1 | 0.02 |

#### REJECT outcomes

| phase | REJECT | caught | flipped | overturned | unresolved | pending | untracked |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 2 | 0 | 0 | 0 | 0 | 1 | 1 |
| refactor | 1 | 0 | 0 | 0 | 0 | 0 | 1 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| developer | claude-sonnet-4 | 5 | 0 | 0 | 0 | 300 | 184 | 24 | 366 | 577 | 788 | 999 | 1.92 |
| verifier | claude-sonnet-4 | 7 | 4 | 3 | 0 | 125 | 59 | 13 | 62 | 113 | 164 | 215 | 0.77 |
| developer | claude-opus-5-5 | 3 | 0 | 0 | 1 | 170 | 126 | 13 | 160 | 190 | 220 | 250 | 1.25 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| red | 110 | 0.50 | 45 | 0.30 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 90 | 0.67 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| cover | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| one | 11 | 3 | 2 | 1 | 2 | 1 | 364 | 44 | 580 | 870 | 1160 | 1450 | 3.54 | 690 | red 1/3, refactor 1/2 | 1/5 | budget-spent | 9 | red | full |
| two | 2 | 0 | 1 | 0 | 0 | 0 | 5 | 4 | 6 | 8 | 10 | 12 | 0.30 | unknown | unknown | unknown | unknown |  |  | full |
| three | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | 1 | 1 | 1 | 0.08 | 30 | unknown | unknown | unknown |  |  | pin |
| five | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | 1 | 1 | 1 | 0.02 | 20 | n/a | n/a | n/a |  |  | full |

Adjudications: retry 1, bail 1, route 0, unparsed 0

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER, VERI_MODEL_REVISE and VERI_MODEL_REVISE_GREEN.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| one | 1 | 2/5 | candidates-done | PASS | 1 | 160 | 1.39 |
| one | 2 | 1/5 | budget-spent |  | 0 | 0 | 0.00 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 1/3 | budget-spent |

Inconsistent mark: stopped=budget-spent, but transforms=1 is below budget=3

#### Refactor totals

| step | passes | transforms | landed nothing | stopped |
| --- | ---: | ---: | ---: | --- |
| one | 2 | 3 | 0 | budget-spent 1, candidates-done 1 |
| issue | 3 | 4 | 0 | budget-spent 2, candidates-done 1 |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s |
| --- | ---: | ---: |
| fast | 12 | 13 |
| full | 140 |  |
| unknown | 7 |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 50 | 588 | 880 | 1172 | 1464 | 6.62 (estimate) |

Not counted: the CI wait after readying and `pr-finish.sh`, which run after this report is committed.

Green rejects by route: none
"""


def test_the_rich_journal_renders_the_whole_page_byte_for_byte(tmp_path, monkeypatch, metrics):
    assert rich_report(tmp_path, monkeypatch, metrics) == EXPECTED
