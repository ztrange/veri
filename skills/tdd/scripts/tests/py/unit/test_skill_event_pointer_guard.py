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


def test_a_skill_edit_step_send_without_a_skill_edit_md_pointer_is_reported_and_with_one_is_not():
    """Subject is the guard: a planted sentence entering a ⟦skill-edit⟧ step is named by file and line until it names SKILL-EDIT.md."""
    bare = "\n".join([
        "## Some section",
        "",
        "Then run the ⟦skill-edit⟧ step for the requirements row.",
    ])
    pointed = bare + " Read `<base directory>/SKILL-EDIT.md` first."

    assert ("SKILL-EDIT.md", 3) in guard.unpointed_sends(bare)
    assert ("SKILL-EDIT.md", 3) not in guard.unpointed_sends(pointed)


def test_the_pointer_is_read_within_the_whole_sentence_however_many_lines_it_spans_and_not_in_another_sentence():
    """Subject is the guard: a pointer ending a sentence four lines below its trigger counts; one in the next sentence does not."""
    spanning = "\n".join([
        "If the push is refused, **bail**",
        "once the retries",
        "are spent and the",
        "remote still says no, Read `<base directory>/BAIL.md`.",
    ])
    next_sentence = "\n".join([
        "If the push is refused, **bail**.",
        "Then Read `<base directory>/BAIL.md` for the procedure.",
    ])

    assert ("BAIL.md", 1) not in guard.unpointed_sends(spanning)
    assert ("BAIL.md", 1) in guard.unpointed_sends(next_sentence)


def test_every_other_phrasing_that_sends_the_run_into_a_bail_is_reported_without_a_pointer():
    """Subject is the guard: 'bails as', 'bail with cause', 'bails with cause', '→ bail', 'is a bail' and a bare 'bail' each name BAIL.md and their line."""
    text = "\n".join([
        "A refused push bails as stuck.",
        "A refused push: bail with cause push-refused.",
        "A refused push bails with cause push-refused.",
        "A refused push → bail.",
        "A third refusal is a bail.",
        "A refused push twice in a row: bail.",
    ])

    assert sorted(line for event_file, line in guard.unpointed_sends(text) if event_file == "BAIL.md") == [1, 2, 3, 4, 5, 6]
