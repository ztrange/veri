"""Cases for what skills/tdd/SKILL.md tells the conductor to narrate out of the red leaf's prediction."""
import pathlib
import re

from skill_sections import heading_window

REVISE_MD = pathlib.Path(__file__).resolve().parents[4] / "REVISE.md"

REVISE = "## Revising on a REJECT"

EXIT_0_OR_2 = r"exit(s| code)? 0 (or|\|) 2|0 or 2|\b0\b[^.]*\b2\b"


def says(text, pattern, message):
    assert re.search(pattern, text), message


def test_revise_loop_checks_a_revise_red_report_with_red_divergence_and_spends_the_attempt_without_re_verifying():
    text = heading_window(REVISE_MD, REVISE, "red-divergence")
    says(text, r"revise-red|revise of red|red revise|phase is red|<phase> is red",
         "the check is not said to be the red phase's")
    says(text, EXIT_0_OR_2, "revise loop names red-divergence.sh without the exit codes that take the diverged path")
    says(text, r"without (launching|running|re-running) the verifier|skip(s|ping)? (the )?re-verif|do not re-verify|never re-verif|without re-verifying",
         "a diverged revise-red is not said to skip the re-verification")
    says(text, r"spends? (the |that )?(next )?attempt|attempt .* (is |still )?spen|counts? against|against .*revise_budget",
         "the diverged attempt is not said to spend REVISE_BUDGET")


def test_red_and_revise_launches_remove_the_previous_leafs_prediction_file_and_run_output_file_before_the_leaf_starts():
    text = heading_window(REVISE_MD, REVISE, r"Fresh developer leaf")
    before_launch = text.split("detach-leaf.sh")[0]
    for name in ("red-prediction.md", "red-run-output.txt"):
        assert re.search(r"rm -f[^`;|]*\.tdd/" + re.escape(name), before_launch), (
            f"{REVISE}: the leaf launches without first running rm -f on .tdd/{name}")
