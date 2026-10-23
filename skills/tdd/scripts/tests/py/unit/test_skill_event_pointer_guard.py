"""The event-pointer guard names the file and line of a send into an event that has no pointer (#2075)."""
import test_skill_event_files as guard


def test_a_bare_bail_instruction_without_a_bail_md_pointer_is_reported_by_file_and_line():
    """Subject is the guard: a planted '**bail**' line with no BAIL.md pointer is named by event file and line."""
    text = "\n".join([
        "## Some section",
        "",
        "If the push is refused twice, **bail**.",
    ])

    assert ("BAIL.md", 3) in guard.unpointed_sends(text)


def test_a_bail_heading_script_name_cause_token_or_mention_without_a_pointer_is_not_reported():
    """Subject is the guard: only a sentence sending the run into a bail matches BAIL.md, not four look-alikes."""
    text = "\n".join([
        "## Bail",
        "classify-bail.sh labels the bail by its cause.",
        "The cause is `bail-stuck`.",
        "A bail is recorded in the ledger once it happens.",
    ])

    assert guard.unpointed_sends(text) == []
