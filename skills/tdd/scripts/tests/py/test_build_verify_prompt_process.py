"""Cases for veri/build_verify_prompt.py that start a real process: a symlinked entry point."""
import subprocess
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[2]
SPEC_TEXT = 'slugify("Hello & World/Foo") must return "hello-world-foo" — see {ref}\\n done.\n'


@pytest.mark.process("build-verify-prompt.sh run through a symlink to the scripts directory from another working directory")
def test_red_green_and_diff_calls_through_a_symlink_to_the_scripts_directory_answer_as_in_place_but_name_the_symlink_in_the_timed_test_run_path(
        tmp_path):
    spec = tmp_path / "spec.md"
    spec.write_bytes(SPEC_TEXT.encode())
    linked = tmp_path / "linked"
    linked.mkdir()
    (linked / "veri-scripts").symlink_to(SCRIPTS, target_is_directory=True)
    in_place = SCRIPTS / "timed-test-run.sh"
    through_link = linked / "veri-scripts" / "timed-test-run.sh"
    problems = []

    def same_through_link(label, args):
        want = subprocess.run([str(SCRIPTS / "build-verify-prompt.sh"), *args], stdin=subprocess.DEVNULL,
                              capture_output=True)
        got = subprocess.run(["./veri-scripts/build-verify-prompt.sh", *args], cwd=linked,
                             stdin=subprocess.DEVNULL, capture_output=True)
        if str(in_place).encode() not in want.stdout:
            problems.append(f"{label} in place names no {in_place}")
        want_out = want.stdout.replace(str(in_place).encode(), str(through_link).encode())
        if got.returncode != want.returncode:
            problems.append(f"{label} exited {got.returncode} through the link, {want.returncode} in place")
        if got.stdout != want_out:
            problems.append(f"{label} stdout differs through the link")
        if got.stderr != want.stderr:
            problems.append(f"{label} stderr differs through the link")

    same_through_link("red", ["red", str(spec), "tests/test_slugify.py", "test_slugify_lowercases"])
    same_through_link("green", ["--fast-cmd", "make unit", "green", str(spec), "tests/test_slugify.py",
                                "test_slugify_lowercases"])
    same_through_link("diff", ["--step", "s", "--fast-cmd", "make unit", "diff", str(spec), "0123abc", "4567def"])

    assert problems == []
