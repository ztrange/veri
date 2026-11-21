"""CLAUDE.md stays under a byte cap (#4517, PRD 042.2)."""


def cap_failure(text, cap, baseline):
    size = len(text.encode("utf-8"))
    if size <= cap:
        return None
    return "CLAUDE.md is %d B, over its %d B cap" % (size, cap)


def test_a_text_exactly_at_the_cap_reports_no_failure_4517():
    text = "# x\n\n## A\n\né\n"
    cap = len(text.encode("utf-8"))

    assert cap_failure(text, cap, {"A": 1}) is None
