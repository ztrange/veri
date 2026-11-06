"""Case for SKILL.md's Green step routing a SUPERSEDED:-only develop-green report, read as text (#2254)."""
import pathlib
import re

SKILL = pathlib.Path(__file__).resolve().parents[4] / "SKILL.md"
HEADING = "#### Green — minimum implementation (developer leaf), then verify-green (blind)"


def _green():
    text = SKILL.read_text(encoding="utf-8")
    start = text.index(HEADING)
    following = re.search(r"^#{1,4} ", text[start + len(HEADING):], re.M)
    stop = start + len(HEADING) + following.start() if following else len(text)
    return " ".join(text[start:stop].split())


def test_2254_a_green_report_naming_a_superseded_case_alone_goes_through_wrong_test_route_to_a_free_red_contradicted_reroute():
    green = _green()
    assert "`$S/wrong-test-route.sh --spec .tdd/issue-<n>-spec.md .tdd/develop-green.out '<target-test-id>'`" in green, "Green has no wrong-test-route.sh call"
    red = re.search(r"exit 0 prints `red <case>`.*?then retry green\.", green)
    assert red, "Green has no `red <case>` answer that retries green"
    assert "`red-contradicted`" in red.group(0), "the `red <case>` answer lacks `red-contradicted`"
