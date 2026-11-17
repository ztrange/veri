"""Cases for veri/content_mtimes.py that run real git over scratch repositories."""
import importlib
import os
import subprocess
import sys

import pytest

FILES = {"a.py": "x = 1\n", "pkg/b.py": "y = 2\n", "notes.txt": "plain\n"}


@pytest.fixture
def content_mtimes():
    return importlib.import_module("veri.content_mtimes")


def repository(root, files, mtime):
    """A git working tree at <root> tracking <files>, every one's mtime set to <mtime>."""
    for name, text in files.items():
        (root / name).parent.mkdir(parents=True, exist_ok=True)
        (root / name).write_text(text)
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    subprocess.run(["git", "add", "."], cwd=root, check=True)
    for name in files:
        os.utime(root / name, (mtime, mtime))


def mtimes(root, files):
    return {name: os.stat(root / name).st_mtime for name in files}


@pytest.mark.process("git init and git add run for real in two scratch repositories, then content_mtimes in each")
def test_two_working_trees_holding_the_same_content_get_equal_mtimes_per_file_and_a_file_changed_in_one_a_different_one_3922(
        content_mtimes, run_cli, tmp_path):
    one, other = tmp_path / "one", tmp_path / "other"
    repository(one, FILES, 1600000000)
    repository(other, dict(FILES, **{"pkg/b.py": "y = 3\n"}), 1700000000)

    answers = [run_cli(content_mtimes, [], cwd=root) for root in (one, other)]
    stamped = (mtimes(one, FILES), mtimes(other, FILES))

    assert (answers, [name for name in FILES if stamped[0][name] == stamped[1][name]],
            stamped[0]["pkg/b.py"] != stamped[1]["pkg/b.py"]) == ([(0, "", "")] * 2, ["a.py", "notes.txt"], True)


PROBE_TEST = (
    "import os, sys\n"
    "sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'veri'))\n"
    "import probe_mod\n"
    "SEEN = '%s'\n"
    "def test_records_what_it_ran():\n"
    "    open(os.environ['PROBE_OUT'], 'w').write(probe_mod.VALUE + SEEN)\n"
)


def run_the_leg(tree, prefix, out):
    """The real leg, as `make test` starts it, over <tree>'s one test file, its bytecode under <prefix>; what the case ran."""
    scripts = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    env = {k: v for k, v in os.environ.items() if k != "PYTHONDONTWRITEBYTECODE"}
    env.update(PYTHONPYCACHEPREFIX=str(prefix), VERI_PYTEST_WORKERS="1", PROBE_OUT=str(out),
               PYTHONPATH=os.path.join(scripts, "veri"))
    done = subprocess.run(
        [sys.executable, "-c", "import runpy, sys; sys.argv[0] = sys.argv.pop(1); runpy.run_path(sys.argv[0], run_name='__main__')",
         os.path.join(scripts, "tests", "leg", "pytest_leg.py"), "--subset", "-q", "-p", "no:cacheprovider", "test_probe.py"],
        cwd=tree, env=env, capture_output=True, text=True, timeout=60)
    assert done.returncode == 0, done.stdout + done.stderr
    return out.read_text()


@pytest.mark.process("git init and git add run for real in a scratch repository, then the real leg twice over its one test file")
def test_a_test_file_and_a_veri_module_changed_after_their_pyc_was_cached_run_their_new_content_even_when_their_stamps_collide_3922(
        content_mtimes, run_cli, tmp_path):
    tree, prefix, out = tmp_path / "tree", tmp_path / "pycache", tmp_path / "ran"
    prefix.mkdir()
    repository(tree, {"test_probe.py": PROBE_TEST % "xxx", "veri/probe_mod.py": "VALUE = 'aaa'\n"}, 1600000000)
    run_cli(content_mtimes, [], cwd=tree)
    first = run_the_leg(tree, prefix, out)
    cached = mtimes(tree, ["test_probe.py", "veri/probe_mod.py"])

    (tree / "test_probe.py").write_text(PROBE_TEST % "yyy")
    (tree / "veri" / "probe_mod.py").write_text("VALUE = 'bbb'\n")
    run_cli(content_mtimes, [], cwd=tree)
    # A stamp is 28 bits of the blob id, so two contents of one size can share it; then only the leg's manifest
    # stands between the run and the cached .pyc. Each changed file takes its old stamp to make that so.
    for name, mtime in cached.items():
        os.utime(tree / name, (mtime, mtime))
    second = run_the_leg(tree, prefix, out)

    assert (first, second) == ("aaaxxx", "bbbyyy")
