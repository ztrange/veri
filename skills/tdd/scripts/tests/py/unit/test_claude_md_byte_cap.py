"""CLAUDE.md stays under a byte cap (#4517, PRD 042.2)."""


def section_bytes(text):
    sizes = {}
    title = None
    for line in text.splitlines(keepends=True):
        if line.startswith("## "):
            title = line[3:].strip()
            sizes[title] = 0
        if title is not None:
            sizes[title] += len(line.encode("utf-8"))
    return sizes


def cap_failure(text, cap, baseline):
    size = len(text.encode("utf-8"))
    if size <= cap:
        return None
    sizes = section_bytes(text)
    grown = max(sizes, key=lambda title: sizes[title] - baseline.get(title, 0))
    return "CLAUDE.md is %d B, over its %d B cap; section '## %s' grew most over its baseline" % (
        size,
        cap,
        grown,
    )


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
