"""Source-text audit of the develop prompts: each one that asks for a commit states the `(#<issue>)` suffix.

Each case's subject is source text: a develop-*.md prompt, planted or shipped, read as text.
"""
import pytest
import re

from conftest import SCRIPTS

ASKS = re.compile(
    r"(^|[^a-z])commit (it|that|the|these|them|everything|each|this|your)([^a-z]|$)"
    r"|(^|[.!?]\s+)commit\."
    r"|(^|[^a-z])(make|create) a commit([^a-z]|$)",
    re.IGNORECASE | re.MULTILINE,
)


def offenders(directory):
    found = []
    for path in sorted(directory.glob("develop-*.md")):
        text = path.read_text(encoding="utf-8", errors="surrogateescape")
        if ASKS.search(text) and "(#<issue>)" not in text:
            found.append(f"{path}: asks for a commit without stating the (#<issue>) subject suffix")
    return found


def plant(tmp_path, name, *lines):
    (tmp_path / f"develop-{name}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return tmp_path


def test_a_planted_develop_prompt_that_asks_for_a_commit_without_the_suffix_is_named(tmp_path):
    """Its subject is source text: a planted develop prompt, read as text."""
    found = offenders(plant(tmp_path, "planted", "## Phase: develop-planted", "", "Make the change the step names, then commit that change."))

    assert len(found) == 1 and "develop-planted.md" in found[0]


@pytest.mark.tree_audit("every develop-*.md under skills/tdd/scripts/prompts")
def test_a_planted_develop_prompt_that_makes_no_commit_and_the_real_prompts_directory_are_clean(tmp_path):
    """Its subject is source text: a planted develop prompt and the shipped prompts, read as text."""
    quiet = plant(tmp_path, "quiet", "## Phase: develop-quiet", "", "Make no commit.")

    assert (offenders(quiet), offenders(SCRIPTS / "prompts")) == ([], [])


def test_a_planted_develop_prompt_with_another_commit_phrasing_is_named(tmp_path):
    """Its subject is source text: a planted develop prompt, read as text."""
    found = offenders(plant(tmp_path, "other", "## Phase: develop-other", "", "Commit your change."))

    assert len(found) == 1 and "develop-other.md" in found[0]


def test_a_planted_develop_prompt_saying_commit_these_changes_is_named(tmp_path):
    """Its subject is source text: a planted develop prompt, read as text."""
    found = offenders(plant(tmp_path, "these", "## Phase: develop-these", "", "Commit these changes."))

    assert len(found) == 1 and "develop-these.md" in found[0]


def test_a_planted_develop_prompt_saying_commit_everything_you_changed_is_named(tmp_path):
    """Its subject is source text: a planted develop prompt, read as text."""
    found = offenders(plant(tmp_path, "everything", "## Phase: develop-everything", "", "Commit everything you changed."))

    assert len(found) == 1 and "develop-everything.md" in found[0]


def test_a_planted_develop_prompt_saying_commit_them_is_named(tmp_path):
    """Its subject is source text: a planted develop prompt, read as text."""
    found = offenders(plant(tmp_path, "them", "## Phase: develop-them", "", "Stage the files you changed, then commit them."))

    assert len(found) == 1 and "develop-them.md" in found[0]


def test_a_planted_develop_prompt_whose_commit_instruction_is_the_bare_sentence_is_named(tmp_path):
    """Its subject is source text: a planted develop prompt, read as text."""
    found = offenders(plant(tmp_path, "bare", "## Phase: develop-bare", "", "Make the change the step names.", "Commit."))

    assert len(found) == 1 and "develop-bare.md" in found[0]


def test_a_planted_develop_prompt_saying_make_a_commit_is_named(tmp_path):
    """Its subject is source text: a planted develop prompt, read as text."""
    found = offenders(plant(tmp_path, "make", "## Phase: develop-make", "", "Make the change the step names, then make a commit."))

    assert len(found) == 1 and "develop-make.md" in found[0]


def test_a_planted_develop_prompt_saying_create_a_commit_is_named(tmp_path):
    """Its subject is source text: a planted develop prompt, read as text."""
    found = offenders(plant(tmp_path, "create", "## Phase: develop-create", "", "Create a commit for this work."))

    assert len(found) == 1 and "develop-create.md" in found[0]


def test_a_planted_develop_prompt_mentioning_only_git_diff_base_sha_head_is_clean(tmp_path):
    """Its subject is source text: a planted develop prompt, read as text."""
    diff = plant(tmp_path, "diff", "## Phase: develop-diff", "", "Read what the step changed with `git diff <base-sha>..HEAD`.")

    assert offenders(diff) == []


def test_a_planted_develop_prompt_mentioning_only_the_steps_green_commit_is_clean(tmp_path):
    """Its subject is source text: a planted develop prompt, read as text."""
    green = plant(tmp_path, "green", "## Phase: develop-green", "", "Compare the tree against the step's green commit.")

    assert offenders(green) == []


@pytest.mark.tree_audit("every develop-*.md under skills/tdd/scripts/prompts")
def test_every_shipped_develop_prompt_is_clean():
    """Its subject is source text: the shipped develop-*.md prompts, read as text."""
    assert offenders(SCRIPTS / "prompts") == []
