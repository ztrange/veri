"""Cases for what skills/tdd/SKILL.md tells the conductor to narrate out of the red leaf's prediction."""
import importlib
import pathlib
import re

SKILL = pathlib.Path(__file__).resolve().parents[4] / "SKILL.md"
REVISE_MD = SKILL.with_name("REVISE.md")

RED = "#### Red — one failing test (developer leaf), then verify-red (blind)"
REVISE = "## Revising on a REJECT"

EXIT_0_OR_2 = r"exit(s| code)? 0 (or|\|) 2|0 or 2|\b0\b[^.]*\b2\b"


def _window(heading, start):
    section = importlib.import_module("skill_sections").section(REVISE_MD if heading == REVISE else SKILL, heading)
    lines = section.splitlines()[1:]
    for i, line in enumerate(lines):
        if line.startswith("#"):
            lines = lines[:i]
            break
    for i, line in enumerate(lines):
        if re.search(start, line):
            return plain(lines[i:])
    raise AssertionError(f"{heading!r} in SKILL.md has no line matching {start!r}")


def plain(lines):
    return " ".join(line.replace("*", "").replace("`", "").lower() for line in lines) + " "


def says(text, pattern, message):
    assert re.search(pattern, text), message


def test_red_narration_puts_the_leafs_prediction_and_whether_it_matched_in_the_red_comment():
    text = _window(RED, "### 🔴 Red")
    says(text, r"predicted_failure|predicted failure|prediction it (made|wrote)|what it predicted",
         "SKILL.md tells the conductor to post the Red comment without the leaf's predicted failure")
    says(text, r"prediction: *matched|matched \| diverged|whether (the|its) (prediction|predicted failure) (matched|was)|matched or diverged",
         "SKILL.md's Red comment never says whether the prediction matched")


def test_red_section_runs_red_divergence_and_sends_a_diverged_prediction_to_the_red_revise_loop():
    text = _window(RED, "red-divergence")
    says(text, EXIT_0_OR_2, "red-divergence.sh named without the exit codes that take the diverged path")
    says(text, r"skips? verify-red and verify-pin|skips? both verify-red and verify-pin|verify-red and verify-pin entirely",
         "a divergence does not skip verify-red and verify-pin")
    says(text, r"verify-red.reason", "the divergence reason is not written to .tdd/verify-red.reason")
    says(text, r"prediction-diverged", "no prediction-diverged event is emitted")
    says(text, r"revise loop|revising on a reject|revise", "a diverged red is not sent into the revise loop")


def test_revise_loop_checks_a_revise_red_report_with_red_divergence_and_spends_the_attempt_without_re_verifying():
    text = _window(REVISE, "red-divergence")
    says(text, r"revise-red|revise of red|red revise|phase is red|<phase> is red",
         "the check is not said to be the red phase's")
    says(text, EXIT_0_OR_2, "revise loop names red-divergence.sh without the exit codes that take the diverged path")
    says(text, r"without (launching|running|re-running) the verifier|skip(s|ping)? (the )?re-verif|do not re-verify|never re-verif|without re-verifying",
         "a diverged revise-red is not said to skip the re-verification")
    says(text, r"spends? (the |that )?(next )?attempt|attempt .* (is |still )?spen|counts? against|against .*revise_budget",
         "the diverged attempt is not said to spend REVISE_BUDGET")


def test_red_divergence_calls_hand_it_the_prediction_file_and_the_runs_output_and_exit_1_narrates_a_prediction_not_written_before_the_run():
    for heading in (RED, REVISE):
        text = _window(heading, "red-divergence")
        says(text, r"red-divergence\.sh[^`]*\.tdd/red-prediction\.md[^`]*\.tdd/red-run-output\.txt",
             f"{heading}: red-divergence.sh runs without the prediction file and the run-output file")
        says(text, r"exit 1[^.]*(missing|newer|not written)|(missing|newer|not written)[^.]*exit 1",
             f"{heading}: no branch on red-divergence.sh exit 1")
        says(text, r"prediction not written before the run",
             f"{heading}: never narrates 'prediction not written before the run'")
        says(text, r"spends? (the |that )?(next )?attempt|spends? .*REVISE_BUDGET|counts? against|against .*REVISE_BUDGET",
             f"{heading}: a late prediction is not said to spend the attempt")


def test_red_and_revise_launches_remove_the_previous_leafs_prediction_file_and_run_output_file_before_the_leaf_starts():
    for heading, start in ((RED, r"Develop\."), (REVISE, r"Fresh developer leaf")):
        text = _window(heading, start)
        before_launch = text.split("detach-leaf.sh")[0]
        for name in ("red-prediction.md", "red-run-output.txt"):
            assert re.search(r"rm -f[^`;|]*\.tdd/" + re.escape(name), before_launch), (
                f"{heading}: the leaf launches without first running rm -f on .tdd/{name}")
