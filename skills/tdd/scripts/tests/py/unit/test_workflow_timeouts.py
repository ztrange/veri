"""The workflow files under .github/workflows/, read as text the way GitHub Actions reads them."""
import pytest
import re

from conftest import ROOT

CI_YML = ROOT / ".github/workflows/ci.yml"
WORKFLOWS = ROOT / ".github/workflows"


def read_lines(path):
    return path.read_bytes().decode("utf-8", "surrogateescape").split("\n")


def job_block(path, job):
    block = []
    inside = False
    for line in read_lines(path):
        if not inside:
            inside = line == "  %s:" % job
        elif re.match(r"  [^ ]", line):
            break
        else:
            block.append(line)
    return block


def job_names(path):
    names = []
    inside = False
    for line in read_lines(path):
        if not inside:
            inside = re.match(r"jobs:\s*$", line) is not None
        elif re.match(r"[^\s]", line):
            break
        else:
            found = re.match(r"  ([A-Za-z0-9_.-]+):\s*$", line)
            if found:
                names.append(found.group(1))
    return names


def timeout_comment(path, job, minutes, problems):
    block = job_block(path, job)
    if not block:
        problems.append("no %s job found in %s" % (job, path))
        return None
    pattern = re.compile(r"    timeout-minutes: *%s *(#.*)?$" % minutes)
    idx = next((i for i, line in enumerate(block) if pattern.match(line)), -1)
    if idx < 0:
        problems.append("%s job declares no job-level 'timeout-minutes: %s'" % (job, minutes))
        return None
    context = [block[idx]]
    j = idx - 1
    while j >= 0 and re.match(r"\s*#", block[j]):
        context.insert(0, block[j])
        j -= 1
    return re.sub(r"[A-Z]", lambda m: m.group(0).lower(), "\n".join(context))


def probe(problems, text, message, *patterns):
    for pattern in patterns:
        if not re.search(pattern, text):
            problems.append(message)
            return


def probe_ceiling(problems, text):
    probe(problems, text, "comment beside the timeout does not name the 6-hour default ceiling", r"(6[ -]?h|six[ -]?hour)")


def test_ci_yml_gates_timeout_minutes_8_with_a_comment_citing_the_ceiling_the_measurement_and_the_temporary_raise():
    problems = []
    text = timeout_comment(CI_YML, "gates", 8, problems)
    if text is not None:
        probe_ceiling(problems, text)
        probe(problems, text, "comment does not cite the measured 160-175 s the job takes", r"(^|[^0-9])(1[5-9][0-9])[ -]?s")
        probe(problems, text, "comment does not say the 8 is temporary, naming what has to land first", "temporar", r"(#282|#290)")

    assert problems == []


@pytest.mark.tree_audit("the workflow files under .github/workflows")
def test_every_job_in_every_workflow_file_declares_a_job_level_timeout_minutes():
    problems = []
    files = sorted(p for pattern in ("*.yml", "*.yaml") for p in WORKFLOWS.glob(pattern) if p.is_file())
    for wf in files:
        names = job_names(wf)
        for job in names:
            if not any(re.match(r"    timeout-minutes: *[0-9]+", line) for line in job_block(wf, job)):
                problems.append("%s: job '%s' declares no job-level timeout-minutes" % (wf.name, job))
        if not names:
            problems.append("%s: no jobs found — the sweep read nothing" % wf.name)
    if not files:
        problems.append("no workflow files found under .github/workflows/")

    assert problems == []


def timeouts_over(path, cap):
    problems = []
    for job in job_names(path):
        for line in job_block(path, job):
            found = re.match(r"    timeout-minutes: *([0-9]+)", line)
            if found:
                minutes = int(found.group(1))
                if minutes > cap:
                    problems.append("%s: job '%s' declares timeout-minutes %d, above %d" % (path.name, job, minutes, cap))
    return problems


def test_a_ci_yml_job_declaring_timeout_minutes_above_10_fails_named_and_every_job_in_ci_yml_declares_at_most_10(tmp_path):
    fixture = tmp_path / "ci.yml"
    fixture.write_text(
        "jobs:\n  slow:\n    runs-on: ubuntu-latest\n    timeout-minutes: 11\n"
        "  capped:\n    runs-on: ubuntu-latest\n    timeout-minutes: 10\n"
    )

    assert timeouts_over(fixture, 10) == ["ci.yml: job 'slow' declares timeout-minutes 11, above 10"]
    assert timeouts_over(CI_YML, 10) == []


def test_ci_yml_gates_python_from_setup_python_at_3_12_cached_on_requirements_dev_then_make_install_dev_before_make_test():
    problems = []
    gates = job_block(CI_YML, "gates")

    def has(message, pattern):
        if not any(re.match(pattern, line) for line in gates):
            problems.append(message)

    has("gates job does not run on ubuntu-latest", r"    runs-on: *ubuntu-latest *$")
    has("gates job declares no job-level timeout-minutes", r"    timeout-minutes: *[0-9]+")
    has("gates job has no actions/setup-python step", r" +(- )?uses: *actions/setup-python@")
    has("setup-python is not pinned to python-version 3.12", r""" +python-version: *["']?3\.12["']? *$""")
    has("setup-python does not declare cache: pip", r""" +cache: *["']?pip["']? *$""")
    has("pip's cache is not keyed on requirements-dev.txt", r""" +cache-dependency-path: *["']?requirements-dev\.txt["']? *$""")
    install_at = next((i + 1 for i, line in enumerate(gates) if re.match(r" +run: *make install-dev *$", line)), None)
    test_at = next((i + 1 for i, line in enumerate(gates) if re.match(r" +run: *make test *$", line)), None)
    if install_at is None:
        problems.append("gates job has no step running make install-dev")
    elif test_at is None or install_at >= test_at:
        problems.append("make install-dev does not run before make test (install at line %s, test at line %s)" % (install_at, test_at or "none"))

    assert problems == []


def test_ci_yml_cancels_a_prs_in_progress_run_on_a_newer_push_and_never_cancels_a_push_to_main():
    problems = []
    top = []
    for line in read_lines(CI_YML):
        if re.match(r"jobs:\s*$", line):
            break
        top.append(line)

    def has(message, pattern):
        if not any(re.match(pattern, line) for line in top):
            problems.append(message)

    has("ci.yml declares no workflow-level concurrency", r"concurrency:\s*$")
    has("concurrency group is not keyed on the PR number, falling back to the ref", r"  group:.*github\.event\.pull_request\.number\s*\|\|\s*github\.ref")
    has(
        "cancel-in-progress is not limited to non-draft pull_request events, so a push to main or a draft event could cancel a run",
        r"  cancel-in-progress:\s*\$\{\{\s*github\.event_name\s*==\s*'pull_request'\s*&&\s*!github\.event\.pull_request\.draft\s*\}\}\s*$",
    )

    assert problems == []
