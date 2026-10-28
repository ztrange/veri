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
    """Subject is the guard: a planted sentence entering a ⟦skill-edit⟧ step is named by file and line until it names SKILL-EDIT.md in its own sentence."""
    bare = "\n".join([
        "## Some section",
        "",
        "Then run the ⟦skill-edit⟧ step for the requirements row.",
    ])
    neighbouring = bare + ". Read `<base directory>/SKILL-EDIT.md` first."
    own_sentence = bare + ", Read `<base directory>/SKILL-EDIT.md` first."

    assert ("SKILL-EDIT.md", 3) in guard.unpointed_sends(bare)
    assert ("SKILL-EDIT.md", 3) in guard.unpointed_sends(neighbouring)
    assert ("SKILL-EDIT.md", 3) not in guard.unpointed_sends(own_sentence)


def test_a_pointer_in_a_neighbouring_sentence_on_the_same_line_does_not_point_the_trigger():
    """Subject is the guard: a '**bail**' sentence whose BAIL.md pointer sits in the next sentence of the same line is named by event file and line."""
    text = "\n".join([
        "## Some section",
        "",
        "If the push is refused twice, **bail**. Then Read `<base directory>/BAIL.md` for the procedure.",
    ])

    assert ("BAIL.md", 3) in guard.unpointed_sends(text)


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


def test_a_pointer_before_a_colon_ahead_of_a_code_block_or_before_the_final_period_passes_and_one_inside_a_clause_is_reported():
    """Subject is the guard: a pointer ends its sentence before '):' or the final period; one mid-clause is named by event file and line."""
    colon = "\n".join([
        "If the push is refused, bail (see `<base directory>/BAIL.md`):",
        "",
        "```",
        "git push",
        "```",
    ])
    period = "If the push is refused, **bail**, Read `<base directory>/BAIL.md`."
    mid_clause = "If the push is refused, Read `<base directory>/BAIL.md` and then **bail** at once."

    assert guard.misplaced_pointers(colon) == []
    assert guard.misplaced_pointers(period) == []
    assert guard.misplaced_pointers(mid_clause) == [("BAIL.md", 1)]


def test_a_mid_clause_pointer_in_a_send_is_reported_by_file_and_line_and_a_bare_mention_in_a_sentence_that_sends_nothing_is_not():
    """Subject is the guard: only a pointer inside a sentence that sends the run into its event, and does not end it, is named."""
    send = "\n".join([
        "## Some section",
        "",
        "If the run stops, resume at `<base directory>/RESUME.md` and read the ledger.",
    ])
    bare = "The ledger is described in `<base directory>/RESUME.md` and in the glossary."

    assert guard.misplaced_send_pointers(send) == [("RESUME.md", 3)]
    assert guard.misplaced_send_pointers(bare) == []


def test_a_send_into_a_refactor_kind_run_a_phased_step_or_the_structural_pass_without_its_pointer_is_reported_by_file_and_line():
    """Subject is the guard: each planted send to REFACTOR-KIND.md, PHASED.md and STRUCTURAL.md is named by file and line until its pointer is added."""
    bare = "\n".join([
        "When the spec carries the `## Refactor` section `capture-spec.sh` writes, run it when you plan.",
        "",
        "When `next-unchecked.sh` hands over a step listing `⟦phases: …⟧`, run it in place of Red.",
        "",
        "When it prints a candidate, run the issue's one structural pass, once, before the PR is readied.",
    ])
    pointed = bare.replace("run it when you plan.", "when you plan, `Read` and run `<base directory>/REFACTOR-KIND.md`.")
    pointed = pointed.replace("run it in place of Red.", "in place of Red, `Read` and run `<base directory>/PHASED.md`.")
    pointed = pointed.replace("readied.", "readied: `Read` and run `<base directory>/STRUCTURAL.md`.")

    assert sorted(guard.unpointed_sends(bare)) == [("PHASED.md", 3), ("REFACTOR-KIND.md", 1), ("STRUCTURAL.md", 5)]
    assert guard.unpointed_sends(pointed) == []
