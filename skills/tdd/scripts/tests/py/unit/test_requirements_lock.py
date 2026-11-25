"""requirements-dev.txt is a hash-checked lock of requirements-dev.in's direct pins and everything they pull in (#3967)."""
import importlib.metadata
import re

from packaging.requirements import Requirement
from packaging.utils import canonicalize_name

from conftest import ROOT

# The environment a lock serves: veri's Python floor, on Linux (CI) or macOS (the operator's machine).
FLOOR = [{"python_version": "3.12", "sys_platform": platform, "extra": ""} for platform in ("linux", "darwin")]


def requirements(path):
    """The logical lines of the requirements file <path>: continuations joined, comments and blanks dropped."""
    joined = re.sub(r"\\\n", " ", path.read_text())
    lines = (re.sub(r"(^|\s)#.*", "", line).strip() for line in joined.splitlines())
    return [line for line in lines if line]


def pulled_in(names):
    """The canonical names of <names> and of every package their installed metadata requires on the floor."""
    seen, todo = set(), [canonicalize_name(n) for n in names]
    while todo:
        name = todo.pop()
        if name in seen:
            continue
        seen.add(name)
        for raw in importlib.metadata.requires(name) or []:
            req = Requirement(raw)
            if req.marker is None or any(req.marker.evaluate(env) for env in FLOOR):
                todo.append(canonicalize_name(req.name))
    return seen


def test_requirements_dev_txt_locks_every_package_the_direct_pins_pull_in_each_with_a_sha256_hash_issue_3967():
    direct = [Requirement(line) for line in requirements(ROOT / "requirements-dev.in")]
    lock = requirements(ROOT / "requirements-dev.txt")
    pins = {canonicalize_name(line.split("==")[0]): line.split("==")[1].split()[0] for line in lock}
    unhashed = [line for line in lock if not re.search(r"==\S+ .*--hash=sha256:[0-9a-f]{64}\b", line)]
    header = ROOT.joinpath("requirements-dev.txt").read_text().split("\n\n")[0]

    assert (len(direct), unhashed, sorted(pulled_in(r.name for r in direct) - pins.keys())) == (4, [], [])
    assert {canonicalize_name(r.name): str(r.specifier) for r in direct} == {
        name: "==" + pins[name] for name in (canonicalize_name(r.name) for r in direct)}
    assert [word in header for word in ("requirements-dev.in", "pip download", "shasum -a 256", "pip-compile")] == [
        True, True, True, False], header


def test_ci_keys_its_pip_cache_on_the_lock_issue_3967():
    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text()

    assert re.findall(r"cache-dependency-path:\s*(\S+)", ci) == ["requirements-dev.txt"]
