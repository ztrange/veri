"""Every numbered item of "What to do" in a repair revise-green prompt carries an instruction."""
import importlib
import re

import pytest


@pytest.mark.parametrize("marker", ["⟦suite-repair⟧", "⟦ci-repair⟧"])
def test_a_repair_revise_green_prompt_has_no_empty_numbered_item_in_what_to_do(
        tmp_path, capsysbinary, marker):
    build_develop_prompt = importlib.import_module("veri.build_develop_prompt")
    spec = tmp_path / "spec.md"
    spec.write_bytes(b"# spec\n")
    reason = tmp_path / "reason.md"
    reason.write_bytes(b"rejected\n")

    code = build_develop_prompt.main(
        ["revise", "green", str(spec), "fix it " + marker, "make test", str(reason)])

    out, _ = capsysbinary.readouterr()
    section = out.decode().split("### What to do", 1)[1].split("### Report", 1)[0]
    items = re.split(r"^(?=\d+\.)", section, flags=re.MULTILINE)[1:]
    empty = [item.split()[0] for item in items if not re.sub(r"^\d+\.", "", item).strip()]
    assert (code, len(items) > 0, empty) == (0, True, [])
