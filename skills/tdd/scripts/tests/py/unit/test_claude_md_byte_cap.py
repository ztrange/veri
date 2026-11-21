"""CLAUDE.md stays under a byte cap (#4517, PRD 042.2)."""

from conftest import ROOT

# Root CLAUDE.md at 8cc6b5d1bc plus 1,000 B headroom; raise it here, as a reviewed change.
CAP = 19215 + 1000

# Bytes per `##` section of root CLAUDE.md at 8cc6b5d1bc, and above its first `##`,
# as section_bytes counts them.
BASELINE = {
    "(above the first ##)": 691,
    "Commands": 2929,
    "Exit codes are the API": 576,
    "Invariants worth not breaking": 5767,
    "Testing idiom": 7165,
    "Graded prose": 2087,
}


def section_bytes(text):
    title = "(above the first ##)"
    sizes = {title: 0}
    for line in text.splitlines(keepends=True):
        if line.startswith("## "):
            title = line[3:].strip()
            sizes[title] = 0
        sizes[title] += len(line.encode("utf-8"))
    return sizes


def cap_failure(text, cap, baseline):
    size = len(text.encode("utf-8"))
    if size <= cap:
        return None
    sizes = section_bytes(text)
    growth = {title: sizes[title] - baseline.get(title, 0) for title in sizes}
    grown = max(growth, key=growth.get)
    if growth[grown] <= 0:
        named = "no section grew over its baseline"
    elif grown == "(above the first ##)":
        named = "%s grew most over its baseline" % grown
    else:
        named = "section '## %s' grew most over its baseline" % grown
    return "CLAUDE.md is %d B, over its %d B cap; %s" % (size, cap, named)


def test_a_text_exactly_at_the_cap_reports_no_failure_4517():
    text = "# x\n\n## A\n\né\n"
    cap = len(text.encode("utf-8"))

    assert cap_failure(text, cap, {"A": 1}) is None


def test_a_text_over_the_cap_names_its_size_the_cap_and_the_most_grown_section_4517():
    big = "## Alpha\n\n" + "a" * 300 + "\n"
    grown = "## Beta\n\n" + "b" * 120 + "\n"
    small = "## Gamma\n\nc\n"
    text = "# x\n\n" + big + grown + small
    size = len(text.encode("utf-8"))
    baseline = {"Alpha": len(big), "Beta": 20, "Gamma": len(small)}

    message = cap_failure(text, 100, baseline)

    assert str(size) in message
    assert "100" in message
    assert "Beta" in message


def test_the_root_claude_md_is_within_its_cap_4517():
    failure = cap_failure((ROOT / "CLAUDE.md").read_text(), CAP, BASELINE)

    assert failure is None, failure


def test_a_text_over_the_cap_in_utf8_bytes_but_not_in_characters_fails_4517():
    text = "# x\n\n## A\n\n" + "é" * 10 + "\n"
    cap = len(text.encode("utf-8")) - 1
    assert cap >= len(text)

    assert cap_failure(text, cap, {"A": 1}) is not None


def test_the_most_grown_section_is_chosen_by_utf8_bytes_not_characters_4517():
    more_characters = "## A\n\n" + "a" * 30 + "\n"
    more_bytes = "## B\n\n" + "é" * 20 + "\n"
    assert len(more_characters) > len(more_bytes)
    assert len(more_characters.encode("utf-8")) < len(more_bytes.encode("utf-8"))
    text = "# x\n\n" + more_characters + more_bytes

    message = cap_failure(text, 10, {})

    assert "'## B'" in message


def test_growth_above_the_first_section_is_named_as_its_own_pseudo_section_4517():
    preamble = "# x\n\n" + "p" * 200 + "\n\n"
    section = "## A\n\na\n"
    text = preamble + section
    baseline = {"(above the first ##)": 10, "A": len(section) - 1}

    message = cap_failure(text, 10, baseline)

    assert "(above the first ##)" in message


def test_the_over_cap_message_names_the_pseudo_section_without_a_heading_prefix_4517():
    preamble = "# x\n\n" + "p" * 200 + "\n\n"
    section = "## A\n\na\n"
    text = preamble + section
    baseline = {"(above the first ##)": 10, "A": len(section) - 1}

    message = cap_failure(text, 10, baseline)

    assert "(above the first ##)" in message
    assert "## (above the first ##)" not in message


def test_the_over_cap_message_names_no_section_when_none_grew_over_its_baseline_4517():
    preamble = "# x\n\n"
    alpha = "## Alpha\n\n" + "a" * 50 + "\n"
    beta = "## Beta\n\n" + "b" * 30 + "\n"
    text = preamble + alpha + beta
    baseline = {"(above the first ##)": len(preamble), "Alpha": len(alpha) + 5, "Beta": len(beta)}

    message = cap_failure(text, 10, baseline)

    assert message is not None
    for title in baseline:
        assert title not in message, title
    assert "grew most" not in message
