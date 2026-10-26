"""Cases for the tests-frozen record and check in skills/tdd/SKILL.md, read as text.

Contract under test:
  Every record and check SKILL.md runs outside Green's own check names the step's record by
  `tests-frozen.sh path` over the step text, and no `tests-frozen-<step>` key survives.

Every case's subject is source text: it reads SKILL.md and starts no process.
"""
import pathlib
import re

SKILL = pathlib.Path(__file__).resolve().parents[4] / "SKILL.md"

GREEN = "#### Green"

RECORD_ARG = '--step "$($S/next-unchecked.sh < .tdd/issue-<n>.md)"'


def numbered_section(heading):
    out, inside = [], False
    for n, line in enumerate(SKILL.read_text().split("\n"), 1):
        if not inside:
            inside = line.startswith(heading)
        elif line.startswith("#"):
            break
        else:
            out.append((n, line))
    return out


def plain(text):
    return text.replace("*", "").replace("`", "").lower()


def sentences(text):
    return plain(text).replace(". ", ".\n").split("\n")


def frozen_sentences(heading):
    kept, fence = [], False
    for _, line in numbered_section(heading):
        if line.lstrip().startswith("```"):
            fence = not fence
        elif not fence:
            kept.append(line)
    return [s for s in sentences(" ".join(kept)) if "tests-frozen" in s]


def test_every_tests_frozen_record_and_check_names_the_record_by_path_over_the_step_text_and_red_defines_the_key():
    text = SKILL.read_text()
    in_green = {n for n, _ in numbered_section(GREEN)}
    commands = [(n, line) for n, line in enumerate(text.split("\n"), 1)
                if re.search(r"tests-frozen\.sh (record|check)(?![-\w])", line)
                and not (n in in_green and "tests-frozen.sh check" in line)]
    assert commands, "no tests-frozen.sh record or check command to read"
    for n, line in commands:
        assert f"tests-frozen.sh record {RECORD_ARG}" in line or f"tests-frozen.sh check {RECORD_ARG}" in line, (
            f"SKILL.md:{n} runs record or check without {RECORD_ARG}")
    assert "tests-frozen-<step>" not in text


def test_every_reroute_re_record_in_green_passes_the_steps_own_red_case_and_routes_its_refusal_to_verify_red_reason():
    rerecords = [(n, line) for n, line in numbered_section(GREEN)
                 if "re-record the step's frozen tests with `$S/tests-frozen.sh record" in line]
    leaves = {leaf for leaf in ("red-contradicted", "red-repair", "red-supersede", "red-missing")
              if any(f"`{leaf}` red" in line for _, line in rerecords)}
    assert leaves == {"red-contradicted", "red-repair", "red-supersede", "red-missing"}, (
        f"Green's reroute re-records found only for {sorted(leaves)}")
    for n, line in rerecords:
        assert f"tests-frozen.sh record {RECORD_ARG} --red-case '<red-test-id>'" in line, (
            f"SKILL.md:{n} re-records a reroute's frozen tests without --red-case '<red-test-id>'")
    refusal = [s for s in frozen_sentences(GREEN) if "exit 1" in s and "deleted case" in s]
    assert any("verify-red.reason" in s for s in refusal), (
        "no Green sentence routes tests-frozen record exit 1 (the deleted case) to .tdd/verify-red.reason")
