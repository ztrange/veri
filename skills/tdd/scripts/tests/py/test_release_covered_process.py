"""Cases for release-covered.sh that start the real entry point (#4110)."""
import os
import subprocess

import pytest

from conftest import SCRIPTS
from stub_script import write_stub


@pytest.mark.process("release-covered.sh run as the conductor runs it, with a stub gh on PATH answering the issue reads")
def test_cli_exits_3_for_an_issue_that_is_no_coverage_issue_2_for_no_answer_and_2_with_the_usage_for_no_argument(tmp_path):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    write_stub(bin_dir / "gh",
               'case "$*" in\n'
               '  *"/issues/77") echo \'{"title": "Add a flag", "state": "closed", "labels": []}\' ;;\n'
               '  *) echo "HTTP 502" >&2; exit 1 ;;\n'
               'esac\n')
    env = dict(os.environ, PATH="%s:%s" % (bin_dir, os.environ["PATH"]))

    def run(*argv):
        ran = subprocess.run([str(SCRIPTS / "release-covered.sh"), *argv], cwd=tmp_path, env=env,
                             stdin=subprocess.DEVNULL, capture_output=True, text=True)
        return ran.returncode, ran.stdout, ran.stderr.splitlines()[-1:] if ran.stderr else []

    assert [run("77"), run("78"), run()] == [
        (3, "", ["release-covered.sh: #77 is not a coverage issue a refactor run filed; nothing to release"]),
        (2, "", ["release-covered.sh: no answer from gh reading #78"]),
        (2, "", ["usage: release-covered.sh <issue-number>"])]


@pytest.mark.process("release-covered.sh releasing a bailed refactor issue through the real release-issue.sh path, a stub gh logging each call")
def test_cli_releases_the_bailed_refactor_issue_a_coverage_issue_names_through_gh_and_prints_it(tmp_path):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    (tmp_path / ".tdd").mkdir()
    log = tmp_path / "gh.log"
    write_stub(bin_dir / "gh",
               'echo "$*" >> "$GH_LOG"\n'
               'case "$*" in\n'
               '  "api repos/{owner}/{repo}/issues/77") echo \'{"title": "Cover the behaviour #60 refactors", "state": "closed", "labels": []}\' ;;\n'
               '  "api repos/{owner}/{repo}/issues/60") echo \'{"title": "x", "state": "open", "body": "", "labels": [{"name": "taken:main"}, {"name": "bailed"}]}\' ;;\n'
               '  *) echo \'{}\' ;;\n'
               'esac\n')
    env = dict(os.environ, PATH="%s:%s" % (bin_dir, os.environ["PATH"]), GH_LOG=str(log))
    env.pop("VERI_GH_DRIVER", None)

    ran = subprocess.run([str(SCRIPTS / "release-covered.sh"), "77"], cwd=tmp_path, env=env,
                         stdin=subprocess.DEVNULL, capture_output=True, text=True)

    calls = log.read_text().splitlines()
    assert (ran.returncode, ran.stdout) == (0, "released #60\n"), ran.stderr
    assert [c for c in calls if "/issues/60/labels" in c] == [
        "api repos/{owner}/{repo}/issues/60/labels -f labels[]=ready-for-agent",
        "api -X DELETE repos/{owner}/{repo}/issues/60/labels/taken:main",
        "api -X DELETE repos/{owner}/{repo}/issues/60/labels/parked",
        "api -X DELETE repos/{owner}/{repo}/issues/60/labels/bailed"]
