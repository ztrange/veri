"""In-process cases for veri/preflight_refused.py, the module preflight-refused.sh is a shim over."""
import importlib
import json

USAGE = "usage: preflight-refused.sh <issue-number> <check>\n"


def test_2481_a_preflight_refusal_writes_one_event_naming_the_check_from_either_checkout(tmp_path, run_cli):
    preflight_refused = importlib.import_module("veri.preflight_refused")
    main = tmp_path / "main"
    (main / ".git").mkdir(parents=True)
    run = main / ".tdd" / "wt" / "7"
    (run / ".tdd").mkdir(parents=True)
    (run / ".git").write_text("gitdir: elsewhere\n")
    log = run / ".tdd" / "events.jsonl"

    first = run_cli(preflight_refused, ["7", "full-tier baseline red"], cwd=main)
    second = run_cli(preflight_refused, ["7", "fast-tier baseline red"], cwd=run)
    events = [json.loads(text) for text in log.read_text().splitlines()]

    assert (first[0], second[0]) == (0, 0)
    assert [(e["event"], e["check"], e["cause"], e["classification"]) for e in events] == [
        ("preflight-refused", "full-tier baseline red", "preflight-refused", "system"),
        ("preflight-refused", "fast-tier baseline red", "preflight-refused", "system"),
    ]
    for argv in ([], ["7"], ["7", ""]):
        assert run_cli(preflight_refused, argv, cwd=main) == (2, "", USAGE)
    assert len(log.read_text().splitlines()) == 2
