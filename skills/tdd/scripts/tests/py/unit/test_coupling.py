"""In-process cases for veri/coupling.py, the module coupling.sh is a shim over (#4124, PRD 032.8)."""
import importlib
import os

import pytest


@pytest.fixture
def coupling():
    return importlib.import_module("veri.coupling")


def range_git(fake_processes, changed, tracked=()):
    """Answers the git calls of a run: the base resolves, `diff --name-only` names <changed>, and `ls-files` lists
    <tracked> as the files git does not ignore."""
    def answer(line, **kwargs):
        if line.startswith("git rev-parse --show-toplevel"):
            return 0, os.getcwd() + "\n", ""
        if line.startswith("git rev-parse"):
            return 0, "abc\n", ""
        if line.startswith("git diff"):
            return 0, "".join(f + "\0" for f in changed), ""
        if line.startswith("git ls-files"):
            return 0, "".join(f + "\0" for f in tracked), ""
        raise AssertionError("unexpected command: %s" % line)

    return fake_processes.answers({"git": answer})


def write(root, files):
    for name, text in files.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)


def test_each_same_extension_non_test_pair_importing_each_other_one_of_them_changed_is_printed_in_byte_order(
        tmp_path, monkeypatch, capsys, coupling, fake_processes):
    tree = {"src/b.py": "import a\n", "src/a.py": "import b\nimport Z\n",
            "src/c.py": "import a\n",
            "src/d.py": "import e\n", "src/e.py": "import d\n",
            "src/f.js": "require('./g')\n", "src/g.py": "f = 1\n",
            "docs/h.md": "i\n", "docs/i.md": "h\n",
            "tests/test_j.py": "import a\n", "src/Z.py": "import a\n"}
    write(tmp_path, tree)
    range_git(fake_processes, ["src/b.py", "src/Z.py", "src/f.js", "docs/h.md", "tests/test_j.py"], list(tree))
    monkeypatch.chdir(tmp_path)
    assert (coupling.main(["base"]),) + tuple(capsys.readouterr()) == (
        0, "mutual: src/Z.py src/a.py\nmutual: src/a.py src/b.py\n", "")


def test_no_pair_exits_3_printing_nothing_and_a_base_that_does_not_resolve_exits_2_with_one_stderr_line(
        tmp_path, monkeypatch, capsys, coupling, fake_processes):
    tree = {"src/a.py": "import b\n", "src/b.py": "x = 1\n"}
    write(tmp_path, tree)
    monkeypatch.chdir(tmp_path)
    range_git(fake_processes, ["src/a.py"], list(tree))
    results = [(coupling.main(["base"]),) + tuple(capsys.readouterr())]
    fake_processes.answers({"git": (128, "", "fatal: bad revision\n")})
    results.append((coupling.main(["nope"]),) + tuple(capsys.readouterr()))
    assert results == [(3, "", ""), (2, "", "coupling: cannot resolve 'nope'\n")]


@pytest.mark.parametrize("mention", [
    '"""Events the revise phase writes."""\n',
    "# the revise phase writes these\n",
    "revise = 1\n",
    "def write(revise):\n    return revise\n",
    "def write(step):\n    return step.revise\n",
    'PHASE = "revise"\n',
    'print("revise.sh: %s" % error)\n',
    'def journals(who="revise.sh"):\n    return who\n',
    'if "revise.py" not in command:\n    pass\n',
    'def mine(args):\n    return f"veri/revise.py {args} " in args\n',
    'x = 1  # import revise\n',
    'import revise_extra\nPHASE = "revise"\n',
    'from pkg import prerevise\nPHASE = "revise"\n',
    'rm -f $DIR/revise.pyc\n',
], ids=["docstring", "comment", "variable", "parameter", "attribute", "string literal", "message prefix",
        "keyword label", "membership test", "path inside a longer string", "import inside a comment",
        "import of a longer module name", "from-import of a longer name",
        "path with a longer extension"])
def test_a_file_that_only_holds_the_others_stem_as_a_word_and_does_not_import_it_makes_no_pair_exit_3_4556(
        mention, tmp_path, monkeypatch, capsys, coupling, fake_processes):
    tree = {"veri/event.py": mention, "veri/revise.py": "import event\n"}
    write(tmp_path, tree)
    range_git(fake_processes, list(tree), list(tree))
    monkeypatch.chdir(tmp_path)
    assert (coupling.main(["base"]),) + tuple(capsys.readouterr()) == (3, "", "")


@pytest.mark.parametrize("tree", [
    {"bin/a.sh": 'exec "$(dirname "$0")/b.sh" "$@"\n', "bin/b.sh": '. "$(dirname "$0")/a.sh"\n'},
    {"bin/a.py": 'run([os.path.join(here, "b.sh")])\n', "bin/b.py": 'run(["python3", "a.py"])\n'},
    {"bin/a.js": "const b = require('./b')\n", "bin/b.js": "import { a } from './a.js'\n"},
    {"bin/a.sh": '$S/b.sh --flag "$@"\n', "bin/b.sh": 'next="$HERE/a.sh"\n'},
], ids=["shell scripts by path", "python modules running each other's script", "javascript modules",
        "unquoted shell command and an assigned path"])
def test_two_files_each_invoking_the_others_script_by_path_are_still_a_pair_4556(
        tree, tmp_path, monkeypatch, capsys, coupling, fake_processes):
    write(tmp_path, tree)
    range_git(fake_processes, list(tree), list(tree))
    monkeypatch.chdir(tmp_path)
    a, b = sorted(tree)
    assert (coupling.main(["base"]),) + tuple(capsys.readouterr()) == (0, "mutual: %s %s\n" % (a, b), "")


@pytest.mark.parametrize("tree", [
    {"veri/a.py": "import os, b as bee\n", "veri/b.py": "import veri.a\n"},
    {"veri/a.py": "from b import run\n", "veri/b.py": "from veri.a import x\n"},
    {"veri/a.py": "from veri import b\n", "veri/b.py": "from . import (\n    a,\n    c,\n)\n"},
], ids=["import", "from module import", "from package import module"])
def test_two_python_modules_each_importing_the_other_in_any_import_form_are_a_pair_4556(
        tree, tmp_path, monkeypatch, capsys, coupling, fake_processes):
    write(tmp_path, tree)
    range_git(fake_processes, list(tree), list(tree))
    monkeypatch.chdir(tmp_path)
    assert (coupling.main(["base"]),) + tuple(capsys.readouterr()) == (0, "mutual: veri/a.py veri/b.py\n", "")
