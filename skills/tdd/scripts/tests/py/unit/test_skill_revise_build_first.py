"""Cases for the order REVISE.md's revise loop builds the prompt and mirrors the attempt (#2929)."""
import pathlib

REVISE = pathlib.Path(__file__).resolve().parents[4] / "REVISE.md"


def test_revise_md_builds_prompt_before_mirror_and_bails_on_build_exit_2_2929():
    text = REVISE.read_text()
    start = text.index("2. **Mirror.**")
    end = text.index("3. **Fresh developer leaf.**")
    mirror = text[start:end]
    build = mirror.index("build-develop-prompt.sh revise")
    comment = mirror.index("### ♻️ Revise")
    mark = mirror.index("event.sh revise")
    assert build < comment < mark, (
        f"build at {build}, comment at {comment}, mark at {mark}: the prompt is not built first")
