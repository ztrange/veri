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
