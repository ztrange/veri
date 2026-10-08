"""In-process cases for veri/detect_test_command.py, the module detect-test-command.sh is a shim over."""
import importlib

import pytest

from conftest import SCRIPTS


@pytest.fixture
def detect():
    return importlib.import_module("veri.detect_test_command")


def test_main_returns_0_with_the_command_3_with_nothing_and_1_for_a_valueless_tier_or_issue(tmp_path, capsys, detect):
    made = tmp_path / "made"
    made.mkdir()
    (made / "Makefile").write_text("test:\n\t./run\n")
    bare = tmp_path / "bare"
    bare.mkdir()

    found = (detect.main([str(made)]), capsys.readouterr().out)
    none = (detect.main([str(bare)]), capsys.readouterr().out)
    tier = detect.main(["--tier"])
    issue = detect.main(["--issue"])

    assert (found, none, tier, issue) == ((0, "make test\n"), (3, ""), 1, 1)


def test_main_returns_3_with_nothing_for_a_makefile_without_a_test_target(tmp_path, capsys, detect):
    (tmp_path / "Makefile").write_text("build:\n\tcc main.c\n")

    assert (detect.main([str(tmp_path)]), capsys.readouterr().out) == (3, "")


def test_main_answers_the_issue_bodys_test_command_ahead_of_veri_test_command_and_inference(tmp_path, capsys, detect):
    repo = tmp_path / "repo"
    (repo / ".veri").mkdir(parents=True)
    (repo / ".veri" / "test-command").write_text("./run-tests\n")
    (repo / "Makefile").write_text("test:\n\t./run\n")
    (repo / "go.mod").write_text("module x\n")
    body = tmp_path / "body.md"
    body.write_text("## What to build\n\nA thing.\n\nTest command: make docs-test\n")

    assert (detect.main(["--issue", str(body), str(repo)]), capsys.readouterr().out) == (0, "make docs-test\n")


def test_main_answers_from_the_working_directory_when_the_root_is_empty(tmp_path, capsys, monkeypatch, detect):
    (tmp_path / "Makefile").write_text("test:\n\t./run\n")
    monkeypatch.chdir(tmp_path)

    assert (detect.main([""]), capsys.readouterr().out) == (0, "make test\n")


def test_main_finds_tests_under_a_root_whose_name_holds_glob_characters(tmp_path, capsys, detect):
    root = tmp_path / "r[x]"
    (root / "tests").mkdir(parents=True)
    (root / "tests" / "test_a.py").write_text("")
    (tmp_path / "rx" / "tests").mkdir(parents=True)

    assert (detect.main([str(root)]), capsys.readouterr().out) == (0, "python3 -m unittest discover -q\n")


def test_main_counts_a_makefile_test_assignment_as_a_test_target(tmp_path, capsys, detect):
    (tmp_path / "Makefile").write_text("test := x\n")

    assert (detect.main([str(tmp_path)]), capsys.readouterr().out) == (0, "make test\n")


def test_main_answers_the_issue_bodys_marker_bare_or_backticked_and_falls_through_without_one(tmp_path, capsys, detect):
    def answer(*argv):
        return detect.main(list(argv)), capsys.readouterr().out

    override = tmp_path / "override"
    (override / ".veri").mkdir(parents=True)
    (override / ".veri" / "test-command").write_text("bin/run-suite --all --strict\n")
    (override / "package.json").write_text('{"scripts":{"test":"jest"}}\n')
    inference = tmp_path / "inference"
    inference.mkdir()
    (inference / "Makefile").write_text("test:\n\techo hi\n")
    (inference / "pytest.ini").write_text("")
    none = tmp_path / "none"
    (none / "src").mkdir(parents=True)
    (none / "README.md").write_text("# demo\n\nRun the test suite however you like.\n")
    silent = tmp_path / "silent.md"
    silent.write_text("## Notes\n\nNo line here names the run command; `make docs-test` appears in prose only.\n")
    midline = tmp_path / "midline.md"
    midline.write_text("## Notes\n\n`docs/wt/app.js`, `docs/wt/style.css`. Test command: `make docs-test`. More prose.\n")
    linestart = tmp_path / "linestart.md"
    linestart.write_text("## Notes\n\nTest command: `make docs-test`. `docs/walkthrough.html` is GENERATED — never hand-edit it.\n")
    bare = tmp_path / "bare.md"
    bare.write_text("## Notes\n\nTest command: bin/run --all\n")
    fixtures = SCRIPTS / "tests" / "fixtures" / "detect-test-command"

    untouched = [answer(*flag, str(repo)) for repo in (override, inference, none) for flag in (["--issue", str(silent)], [])]
    stated = [answer("--issue", str(body), str(inference)) for body in (midline, linestart, bare)]
    real = [answer("--issue", str(fixtures / f"issue-{n}.md"), str(inference)) for n in (71, 75, 80, 123)]

    assert (untouched, stated, real) == (
        [(0, "bin/run-suite --all --strict\n")] * 2 + [(0, "make test\n")] * 2 + [(3, "")] * 2,
        [(0, "make docs-test\n"), (0, "make docs-test\n"), (0, "bin/run --all\n")],
        [(0, "make docs-test\n")] * 4,
    )


def test_main_skips_a_marker_quoted_inside_a_backtick_span_and_answers_a_stated_one(tmp_path, capsys, detect):
    def answer(*argv):
        return detect.main(list(argv)), capsys.readouterr().out

    def body(name, text):
        path = tmp_path / f"{name}.md"
        path.write_text(text)
        return str(path)

    override = tmp_path / "override"
    (override / ".veri").mkdir(parents=True)
    (override / ".veri" / "test-command").write_text("bin/run-suite --all --strict\n")
    made = tmp_path / "made"
    made.mkdir()
    (made / "Makefile").write_text("test:\n\techo hi\n")
    intro = "# Leaves run one suite instead of the full one\n\nSince #120 a leaf takes its command from the issue body: {}, and #131 made that line count mid-sentence.\n\n## Notes\n\n"
    quoted = body("quoted", intro.format("the `Test command:` line names it") + "Test command: make test\n")
    only_quoted = body("only-quoted", intro.format("the `Test command:` line names it") + "Files: `skills/tdd/scripts/detect-test-command.sh`.\n")
    absent = body("absent", intro.format("a line in its Notes names it") + "Files: `skills/tdd/scripts/detect-test-command.sh`.\n")
    then_stated = body("then-stated", "## Notes\n\nA leaf takes its command from the `Test command:` line, so: Test command: `make docs-test`. More prose.\n")
    docs_quoted = body("docs-quoted", "# Rule 0 answers a development issue with its own suite\n\nA docs issue writes `Test command: make docs-test` in its Notes, so every leaf on it runs the docs suite. This issue is not a docs issue.\n\n## Notes\n\nFiles: `skills/tdd/scripts/detect-test-command.sh`.\n\nTest command: make test\n")
    issue_144 = str(SCRIPTS / "tests" / "fixtures" / "detect-test-command" / "issue-144.md")

    got = [
        answer("--issue", quoted, str(override)),
        answer("--issue", only_quoted, str(override)),
        answer("--issue", absent, str(override)),
        answer("--issue", then_stated, str(made)),
        answer("--issue", docs_quoted, str(override)),
        answer("--issue", issue_144, str(override)),
    ]

    assert got == [
        (0, "make test\n"),
        (0, "bin/run-suite --all --strict\n"),
        (0, "bin/run-suite --all --strict\n"),
        (0, "make docs-test\n"),
        (0, "make test\n"),
        (0, "make test\n"),
    ]


def test_main_answers_veri_test_command_ahead_of_package_json_and_makefile_and_names_the_node_runner_by_lockfile(tmp_path, capsys, detect):
    def answer(repo):
        return detect.main([str(repo)]), capsys.readouterr().out

    override = tmp_path / "override"
    (override / ".veri").mkdir(parents=True)
    (override / ".veri" / "test-command").write_text("bin/run-suite --all --strict\n")
    (override / "package.json").write_text('{"scripts":{"test":"jest"}}\n')
    (override / "Makefile").write_text("test:\n\techo hi\n")
    lockfiles = {"npm": None, "pnpm": ("pnpm-lock.yaml", "lockfileVersion: 9.0\n"), "yarn": ("yarn.lock", "# yarn lockfile v1\n")}
    for runner, lockfile in lockfiles.items():
        repo = tmp_path / f"node-{runner}"
        repo.mkdir()
        (repo / "package.json").write_text('{"scripts":{"test":"jest"}}\n')
        if lockfile:
            (repo / lockfile[0]).write_text(lockfile[1])

    assert [answer(override)] + [answer(tmp_path / f"node-{runner}") for runner in lockfiles] == [
        (0, "bin/run-suite --all --strict\n"),
        (0, "npm test\n"),
        (0, "pnpm test\n"),
        (0, "yarn test\n"),
    ]


def test_main_answers_pytest_from_its_config_files_after_a_makefile_test_target_and_ahead_of_go_mod(tmp_path, capsys, detect):
    def repo(name, **files):
        root = tmp_path / name
        root.mkdir()
        for file, text in files.items():
            (root / file.replace("_", ".")).write_text(text)
        return detect.main([str(root)]), capsys.readouterr().out

    makefile = "test:\n\techo hi\n"
    setup_cfg = "[tool:pytest]\naddopts = -ra\n"

    got = [
        repo("make-over-pytest", Makefile=makefile, pytest_ini=""),
        repo("py-pytest-ini", pytest_ini=""),
        repo("py-pyproject", pyproject_toml='[tool.pytest.ini_options]\naddopts = "-ra"\n'),
        repo("py-setup-cfg", setup_cfg=setup_cfg),
        repo("setupcfg-no-pytest", setup_cfg="[metadata]\nname = demo\n"),
        repo("setupcfg-vs-makefile", setup_cfg=setup_cfg, Makefile=makefile),
        repo("setupcfg-vs-go-mod", setup_cfg=setup_cfg, go_mod=""),
    ]

    assert got == [
        (0, "make test\n"),
        (0, "pytest -q\n"),
        (0, "pytest -q\n"),
        (0, "pytest -q\n"),
        (3, ""),
        (0, "make test\n"),
        (0, "pytest -q\n"),
    ]


def test_main_answers_go_test_for_go_mod_cargo_test_for_cargo_toml_and_unittest_for_a_bare_tests_directory(tmp_path, capsys, detect):
    def answer(repo):
        return detect.main([str(repo)]), capsys.readouterr().out

    for marker in ("go.mod", "Cargo.toml"):
        (tmp_path / marker).mkdir()
        (tmp_path / marker / marker).write_text("")
    (tmp_path / "unittest-only" / "tests").mkdir(parents=True)
    (tmp_path / "unittest-only" / "tests" / "test_foo.py").write_text("import unittest\n")

    assert [answer(tmp_path / name) for name in ("go.mod", "Cargo.toml", "unittest-only")] == [
        (0, "go test ./...\n"),
        (0, "cargo test\n"),
        (0, "python3 -m unittest discover -q\n"),
    ]


def test_main_without_a_tier_leaves_every_single_command_answer_as_today_and_exits_3_on_claude_md_tier_markers_alone(tmp_path, capsys, detect):
    body = tmp_path / "tier-issue-body.md"
    body.write_text("## Notes\n\nTest command: bin/issue-suite\n")
    shapes = {
        "override": ({".veri/test-command": "bin/run-suite --all --strict\n"}, "bin/run-suite --all --strict"),
        "npm": ({"package.json": '{"scripts":{"test":"jest"}}\n'}, "npm test"),
        "pnpm": ({"package.json": '{"scripts":{"test":"jest"}}\n', "pnpm-lock.yaml": "lockfileVersion: 9.0\n"}, "pnpm test"),
        "yarn": ({"package.json": '{"scripts":{"test":"jest"}}\n', "yarn.lock": "# yarn lockfile v1\n"}, "yarn test"),
        "make": ({"Makefile": "test:\n\techo hi\n"}, "make test"),
        "pytest.ini": ({"pytest.ini": ""}, "pytest -q"),
        "pyproject.toml": ({"pyproject.toml": '[tool.pytest.ini_options]\naddopts = "-ra"\n'}, "pytest -q"),
        "setup.cfg": ({"setup.cfg": "[tool:pytest]\naddopts = -ra\n"}, "pytest -q"),
        "go.mod": ({"go.mod": ""}, "go test ./..."),
        "Cargo.toml": ({"Cargo.toml": ""}, "cargo test"),
        "unittest": ({"tests/test_foo.py": "import unittest\n"}, "python3 -m unittest discover -q"),
        "issue": ({"Makefile": "test:\n\techo hi\n"}, "bin/issue-suite"),
        "markers-only": ({}, None),
    }

    got, want = {}, {}
    for shape, (files, command) in shapes.items():
        repo = tmp_path / f"untiered-{shape}"
        repo.mkdir()
        (repo / "CLAUDE.md").write_text("# demo\n\nveri: fast tests: bin/fast-suite\nveri: all tests: bin/all-suite\n")
        for name, text in files.items():
            (repo / name).parent.mkdir(parents=True, exist_ok=True)
            (repo / name).write_text(text)
        argv = ["--issue", str(body), str(repo)] if shape == "issue" else [str(repo)]
        got[shape] = (detect.main(argv), capsys.readouterr().out)
        want[shape] = (0, command + "\n") if command else (3, "")

    assert got == want


def test_main_with_a_tier_answers_from_its_claude_md_marker_and_falls_back_to_the_single_command_chain(tmp_path, capsys, detect):
    def repo(name, files):
        root = tmp_path / name
        root.mkdir()
        for path, text in files.items():
            (root / path).parent.mkdir(parents=True, exist_ok=True)
            (root / path).write_text(text)
        return str(root)

    makefile = "test:\n\techo hi\n"
    both = repo("tiered-both", {"Makefile": makefile, "CLAUDE.md": '# demo\n\nveri: fast tests: bin/fast-suite  --only "unit tier" -q\nveri: all tests: bin/all-suite  --every "suite there is" -v\n'})
    quoted = repo("tiered-anywhere-quoted", {"Makefile": makefile, "CLAUDE.md": (
        "# demo\n\n"
        "Leaves never read `veri: fast tests: bin/quoted-fast` as a declaration.\n"
        "In this repo the fast tier is veri: fast tests: `bin/real-fast -q`. More prose.\n"
        "Nor `veri: all tests: bin/quoted-all` either.\n"
        "And the full suite is veri: all tests: `bin/real-all -v`. More prose.\n"
    )})
    tierless = repo("tierless-claude-md", {"Makefile": makefile, "CLAUDE.md": "# demo\n\nThe fast tests and all tests are the same here.\n"})
    no_claude = repo("tierless-no-claude-md", {".veri/test-command": "bin/run-suite --all --strict\n"})
    all_only = repo("tiered-all-only", {"Makefile": makefile, "CLAUDE.md": "# demo\n\nveri: all tests: bin/all-only-suite --every -v\n"})
    issue_both = repo("tiered-issue-both", {"Makefile": makefile, "CLAUDE.md": "# demo\n\nveri: fast tests: bin/fast-suite --unit -q\nveri: all tests: bin/all-suite --every -v\n"})
    issue_all_only = repo("tiered-issue-all-only", {"Makefile": makefile, "CLAUDE.md": "# demo\n\nveri: all tests: bin/all-suite --every -v\n"})
    body = tmp_path / "tiered-issue-body.md"
    body.write_text('## Notes\n\nTest command: bin/issue-suite --only "this run" -q\n')
    veri = str(SCRIPTS.parents[2])

    cases = {
        ("both", "fast"): (["--tier", "fast", both], 'bin/fast-suite  --only "unit tier" -q'),
        ("both", "all"): (["--tier", "all", both], 'bin/all-suite  --every "suite there is" -v'),
        ("quoted", "fast"): (["--tier", "fast", quoted], "bin/real-fast -q"),
        ("quoted", "all"): (["--tier", "all", quoted], "bin/real-all -v"),
        ("tierless", "fast"): (["--tier", "fast", tierless], "make test"),
        ("tierless", "all"): (["--tier", "all", tierless], "make test"),
        ("no-claude-md", "fast"): (["--tier", "fast", no_claude], "bin/run-suite --all --strict"),
        ("no-claude-md", "all"): (["--tier", "all", no_claude], "bin/run-suite --all --strict"),
        ("all-only", "fast"): (["--tier", "fast", all_only], "make test"),
        ("issue-both", "fast"): (["--tier", "fast", "--issue", str(body), issue_both], "bin/fast-suite --unit -q"),
        ("issue-both", "all"): (["--tier", "all", "--issue", str(body), issue_both], 'bin/issue-suite --only "this run" -q'),
        ("issue-all-only", "fast"): (["--tier", "fast", "--issue", str(body), issue_all_only], "make test"),
        ("issue-all-only", "all"): (["--tier", "all", "--issue", str(body), issue_all_only], 'bin/issue-suite --only "this run" -q'),
        ("veri", "fast"): (["--tier", "fast", veri], "make unit"),
        ("veri", "all"): (["--tier", "all", veri], "make test"),
    }

    got, want = {}, {}
    for key, (argv, command) in cases.items():
        got[key] = (detect.main(argv), capsys.readouterr().out)
        want[key] = (0, command + "\n")

    assert got == want


def test_main_reads_tier_only_first_and_issue_only_first_or_after_tier_takes_any_tier_skips_a_missing_issue_and_exits_3_on_a_missing_root(tmp_path, capsys, detect):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "Makefile").write_text("test:\n\techo hi\n")
    (repo / "CLAUDE.md").write_text("# demo\n\nveri: fast tests: bin/fast-suite\nveri: slow tests: bin/slow-suite\n")
    body = tmp_path / "body.md"
    body.write_text("## Notes\n\nTest command: bin/issue-suite\n")
    missing = str(tmp_path / "no-such-body.md")

    cases = {
        "issue-before-tier": ["--issue", str(body), "--tier", "fast", str(repo)],
        "unvalidated-tier": ["--tier", "slow", str(repo)],
        "unvalidated-tier-reads-issue": ["--tier", "slow", "--issue", str(body), str(repo)],
        "fast-tier-skips-issue": ["--tier", "fast", "--issue", str(body), str(repo)],
        "missing-issue-file": ["--issue", missing, str(repo)],
        "missing-root": [str(tmp_path / "no-such-repo")],
    }

    got = {}
    for name, argv in cases.items():
        code = detect.main(argv)
        captured = capsys.readouterr()
        got[name] = (code, captured.out, captured.err)

    assert got == {
        "issue-before-tier": (0, "bin/issue-suite\n", ""),
        "unvalidated-tier": (0, "bin/slow-suite\n", ""),
        "unvalidated-tier-reads-issue": (0, "bin/issue-suite\n", ""),
        "fast-tier-skips-issue": (0, "bin/fast-suite\n", ""),
        "missing-issue-file": (0, "make test\n", ""),
        "missing-root": (3, "", ""),
    }


def test_main_keeps_a_markers_trailing_whitespace_answers_an_unclosed_backtick_skips_an_empty_command_and_answers_a_whitespace_only_override_line(tmp_path, capsys, detect):
    def answer(*argv):
        code = detect.main(list(argv))
        return code, capsys.readouterr().out

    def body(name, text):
        path = tmp_path / f"{name}.md"
        path.write_bytes(text)
        return str(path)

    made = tmp_path / "made"
    made.mkdir()
    (made / "Makefile").write_text("test:\n\techo hi\n")
    blank = tmp_path / "blank"
    (blank / ".veri").mkdir(parents=True)
    (blank / ".veri" / "test-command").write_bytes(b"   \nbin/run-suite\n")
    (blank / "Makefile").write_text("test:\n\techo hi\n")

    got = [
        answer("--issue", body("trailing", b"## Notes\n\nTest command: bin/run --all  \t\r\n"), str(made)),
        answer("--issue", body("unclosed", b"## Notes\n\nTest command: `make docs-test and the rest\n"), str(made)),
        answer("--issue", body("empty", b"## Notes\n\nTest command: `` and later Test command: make docs-test\n"), str(made)),
        answer(str(blank)),
    ]

    assert got == [
        (0, "bin/run --all  \t\r\n"),
        (0, "make docs-test and the rest\n"),
        (0, "make docs-test\n"),
        (0, "   \n"),
    ]


def test_main_hides_package_json_test_behind_an_object_valued_script_counts_a_makefile_test_assignment_and_looks_for_tests_one_level_deep(tmp_path, capsys, detect):
    def repo(name, files):
        root = tmp_path / name
        root.mkdir()
        for path, text in files.items():
            (root / path).parent.mkdir(parents=True, exist_ok=True)
            (root / path).write_text(text)
        return detect.main([str(root)]), capsys.readouterr().out

    got = [
        repo("spaced-package", {"package.json": '{\n  "scripts" : {\n    "test" : "jest"\n  }\n}\n'}),
        repo("object-before-test", {"package.json": '{"scripts":{"lint":{"cmd":"eslint"},"test":"jest"}}\n'}),
        repo("make-assignment", {"Makefile": "test := x\n"}),
        repo("nested-tests", {"tests/unit/test_foo.py": "import unittest\n"}),
    ]

    assert got == [
        (0, "npm test\n"),
        (3, ""),
        (0, "make test\n"),
        (3, ""),
    ]
