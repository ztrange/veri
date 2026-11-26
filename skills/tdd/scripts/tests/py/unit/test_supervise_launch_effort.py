"""The `launch` event records a verifier's effort (PRD 024.8): an `effort` key only when VERI_EFFORT_VERIFIER is set."""
import pytest
from veri import event_table, supervise

CMD = ["/s/run-leaf.sh", ".tdd/verify-green.prompt", "--effort", "low"]


@pytest.mark.parametrize("name, effort, expected", [
    ("verify-green", None, ["name=verify-green", "cmd=/s/run-leaf.sh .tdd/verify-green.prompt --effort low", "model=sonnet"]),
    ("verify-green", "", ["name=verify-green", "cmd=/s/run-leaf.sh .tdd/verify-green.prompt --effort low", "model=sonnet"]),
    ("verify-green", "low", ["name=verify-green", "cmd=/s/run-leaf.sh .tdd/verify-green.prompt --effort low",
                             "model=sonnet", "effort=low"]),
    ("develop-green", "low", ["name=develop-green", "cmd=/s/run-leaf.sh .tdd/verify-green.prompt --effort low",
                              "model=sonnet"]),
])
def test_4013_a_verifier_launch_event_carries_effort_only_when_veri_effort_verifier_is_set(
        name, effort, expected, monkeypatch):
    if effort is not None:
        monkeypatch.setenv("VERI_EFFORT_VERIFIER", effort)

    fields = supervise.launch_fields(name, CMD, "sonnet")

    assert fields == expected
    assert all(event_table.valid("launch", key, value) for key, value in (f.split("=", 1) for f in fields))
