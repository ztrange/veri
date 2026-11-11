"""A verify-pin rejection saying the mutation stays green is routed to pin-reject-route.sh, not revised (#3300)."""
import importlib

import pytest


@pytest.fixture(autouse=True)
def runs_issue_number(monkeypatch):
    monkeypatch.setenv("VERI_ISSUE", "3300")


def test_revise_red_for_a_verify_pin_reason_saying_stays_green_builds_no_prompt_and_names_pin_reject_route_3300(
        tmp_path, capsysbinary):
    build_develop_prompt = importlib.import_module("veri.build_develop_prompt")
    spec = tmp_path / "spec.md"
    spec.write_bytes(b"# spec\n")
    reason = tmp_path / "verify-pin.reason"
    reason.write_bytes(b"VERDICT: REJECT\nREASON: the real before-state stays green\n")

    code = build_develop_prompt.main(["revise", "red", str(spec), "9", "make unit", str(reason)])

    out, err = capsysbinary.readouterr()
    assert (code, out, b"pin-reject-route.sh" in err) == (2, b"", True)


def test_revise_red_for_a_stays_green_reason_not_named_verify_pin_reason_still_builds_the_prompt_3300(
        tmp_path, capsysbinary):
    build_develop_prompt = importlib.import_module("veri.build_develop_prompt")
    spec = tmp_path / "spec.md"
    spec.write_bytes(b"# spec\n")
    reason = tmp_path / "verify.reason"
    reason.write_bytes(b"VERDICT: REJECT\nREASON: the mutation `< 2` to `< 1` stays green\n")

    code = build_develop_prompt.main(["revise", "red", str(spec), "9", "make unit", str(reason)])

    out, err = capsysbinary.readouterr()
    assert (code, bool(out), b"pin-reject-route.sh" in err) == (0, True, False)


def test_revise_red_for_a_verify_pin_reason_not_saying_stays_green_still_builds_the_prompt_3300(
        tmp_path, capsysbinary):
    build_develop_prompt = importlib.import_module("veri.build_develop_prompt")
    spec = tmp_path / "spec.md"
    spec.write_bytes(b"# spec\n")
    reason = tmp_path / "verify-pin.reason"
    reason.write_bytes(b"VERDICT: REJECT\nREASON: the case asserts on the wording of the prompt\n")

    code = build_develop_prompt.main(["revise", "red", str(spec), "9", "make unit", str(reason)])

    out, err = capsysbinary.readouterr()
    assert (code, bool(out), b"pin-reject-route.sh" in err) == (0, True, False)


def test_revise_green_for_a_verify_pin_reason_saying_stays_green_still_builds_the_prompt_3300(
        tmp_path, capsysbinary):
    build_develop_prompt = importlib.import_module("veri.build_develop_prompt")
    spec = tmp_path / "spec.md"
    spec.write_bytes(b"# spec\n")
    reason = tmp_path / "verify-pin.reason"
    reason.write_bytes(b"VERDICT: REJECT\nREASON: the real before-state stays green\n")

    code = build_develop_prompt.main(["revise", "green", str(spec), "9", "make unit", str(reason)])

    out, err = capsysbinary.readouterr()
    assert (code, bool(out), b"pin-reject-route.sh" in err) == (0, True, False)


def test_revise_red_for_a_verify_pin_reason_reporting_a_surviving_mutant_builds_the_prompt_3458(
        tmp_path, capsysbinary):
    build_develop_prompt = importlib.import_module("veri.build_develop_prompt")
    spec = tmp_path / "spec.md"
    spec.write_bytes(b"# spec\n")
    reason = tmp_path / "verify-pin.reason"
    reason.write_bytes(b"VERDICT: REJECT\nREASON: the mutation (a-z to a-y) stays green\n")

    code = build_develop_prompt.main(["revise", "red", str(spec), "9", "make unit", str(reason)])

    out, err = capsysbinary.readouterr()
    assert (code, bool(out), b"pin-reject-route.sh" in err) == (0, True, False)


def test_revise_red_for_a_verify_pin_reason_red_on_the_before_state_with_a_surviving_mutant_builds_the_prompt_3458(
        tmp_path, capsysbinary):
    build_develop_prompt = importlib.import_module("veri.build_develop_prompt")
    spec = tmp_path / "spec.md"
    spec.write_bytes(b"# spec\n")
    reason = tmp_path / "verify-pin.reason"
    reason.write_bytes(b"VERDICT: REJECT\nREASON: the target is red on the before-state, "
                       b"but the mutation (a-z to a-y) stays green\n")

    code = build_develop_prompt.main(["revise", "red", str(spec), "9", "make unit", str(reason)])

    out, err = capsysbinary.readouterr()
    assert (code, bool(out), b"pin-reject-route.sh" in err) == (0, True, False)


def test_revise_red_for_a_verify_pin_reason_naming_a_green_before_state_without_stays_green_still_builds_the_prompt_3458(
        tmp_path, capsysbinary):
    build_develop_prompt = importlib.import_module("veri.build_develop_prompt")
    spec = tmp_path / "spec.md"
    spec.write_bytes(b"# spec\n")
    reason = tmp_path / "verify-pin.reason"
    reason.write_bytes(b"VERDICT: REJECT\nREASON: the case is green on the before-state\n")

    code = build_develop_prompt.main(["revise", "red", str(spec), "9", "make unit", str(reason)])

    out, err = capsysbinary.readouterr()
    assert (code, bool(out), b"pin-reject-route.sh" in err) == (2, False, True)
