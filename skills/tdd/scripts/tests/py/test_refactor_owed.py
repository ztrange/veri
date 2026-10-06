"""In-process cases for veri/refactor_owed.py, the module refactor-owed.sh is a shim over."""
import importlib
import io
import pathlib
import sys

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
for path in (SCRIPTS, SCRIPTS / "veri"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

USAGE = (
    "refactor-owed: usage: refactor-owed.sh append <file> '<STEP>' < leaf-report.txt\n"
    "                      refactor-owed.sh render <file>\n"
    "                      refactor-owed.sh list <file>\n"
)


@pytest.fixture
def refactor_owed():
    return importlib.import_module("veri.refactor_owed")


def test_main_refuses_a_missing_argument_or_unknown_verb_with_the_usage_text_and_answers_within_0_to_3(
        monkeypatch, capsys, tmp_path, refactor_owed):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "stdin", io.StringIO(""))

    for argv in ([], ["list"], ["", "f"], ["list", ""], ["bogus", "f"]):
        code = refactor_owed.main(argv)
        captured = capsys.readouterr()
        assert (argv, code, captured.out, captured.err) == (argv, 2, "", USAGE)
        assert (argv, sorted(p.name for p in tmp_path.iterdir())) == (argv, [])

    empty = tmp_path / "empty.md"
    empty.write_text("")
    for argv in (["list", str(tmp_path / "absent.md")], ["render", str(empty)]):
        code = refactor_owed.main(argv)
        captured = capsys.readouterr()
        assert (argv, code, captured.out) == (argv, 3, "")

    owed = tmp_path / "owed.md"
    monkeypatch.setattr(sys, "stdin", io.StringIO("CANDIDATES: structural | x\n"))
    code = refactor_owed.main(["append", str(owed), "S"])
    assert code == 0


def test_append_writes_a_test_only_line_under_the_step_as_test_only_candidate_answers_and_no_other_class_as_test_only(
        monkeypatch, tmp_path, refactor_owed):
    step = "append records a test-only candidate as test_only_candidate answers it"
    for line, transform in (
            ("CANDIDATES: test-only | fold the two fixtures into one", "fold the two fixtures into one"),
            ("CANDIDATES: structural | extract the parser", None),
            ("CANDIDATES: cosmetic | rename x to count", None),
            ("CANDIDATES: none", None)):
        owed = tmp_path / "owed.md"
        if owed.exists():
            owed.unlink()
        monkeypatch.setattr(sys, "stdin", io.StringIO(line + "\n"))
        code = refactor_owed.main(["append", str(owed), step])
        text = owed.read_text() if owed.exists() else ""
        assert (line, code) == (line, 0)
        if transform is None:
            assert (line, [l for l in text.splitlines() if l.startswith("- test-only | ")]) == (line, [])
            if not line.startswith("CANDIDATES: structural"):
                assert (line, owed.exists()) == (line, False)
        else:
            assert (line, text) == (line, f"### {step}\n- test-only | {transform}\n")


def test_append_counts_only_an_unindented_candidate_line_and_records_its_transform_after_the_bar_and_its_blanks(
        monkeypatch, tmp_path, refactor_owed):
    owed = tmp_path / "owed.md"
    report = ("CANDIDATES:structural|a\n"
              "  CANDIDATES: structural | b\n"
              "CANDIDATES: Structural | c\n"
              "CANDIDATES:   structural   |   e  \n"
              "CANDIDATES: structural | f | g\n"
              "CANDIDATES: structural |\n"
              "CANDIDATES: structural | h\r\n"
              "CANDIDATES: cosmetic | rename k\n"
              "junk line\n")
    monkeypatch.setattr(sys, "stdin", io.StringIO(report))
    code = refactor_owed.main(["append", str(owed), "S"])
    written = owed.read_bytes() if owed.exists() else b""
    assert (code, written) == (0, b"### S\n- a\n- e  \n- f | g\n- \n- h\r\n")


def test_append_writes_structural_before_test_only_and_appends_a_block_only_when_a_line_is_owed(
        monkeypatch, tmp_path, refactor_owed):
    owed = tmp_path / "owed.md"
    owed.write_bytes(b"prior\n")
    monkeypatch.setattr(sys, "stdin", io.StringIO("CANDIDATES: test-only | t1\n"
                                                  "CANDIDATES: structural | s1\n"
                                                  "CANDIDATES: test-only | t2\n"
                                                  "CANDIDATES: structural | s2"))
    code = refactor_owed.main(["append", str(owed), "", "src/a.sh", "tests/x"])
    assert (code, owed.read_bytes()) == (
        0, b"prior\n### \n- s1\n- s2\n- test-only | t1\n- test-only | t2\n")

    absent = tmp_path / "absent.md"
    monkeypatch.setattr(sys, "stdin", io.StringIO("CANDIDATES: cosmetic | rename k\njunk line\n"))
    code = refactor_owed.main(["append", str(absent), "S"])
    assert (code, absent.exists()) == (0, False)

    before = owed.read_bytes()
    monkeypatch.setattr(sys, "stdin", io.StringIO("CANDIDATES: cosmetic | rename k\njunk line\n"))
    code = refactor_owed.main(["append", str(owed), "S"])
    assert (code, owed.read_bytes()) == (0, before)


def test_append_with_no_step_argument_writes_the_block_under_an_empty_step_heading(
        monkeypatch, tmp_path, refactor_owed):
    owed = tmp_path / "owed.md"
    monkeypatch.setattr(sys, "stdin", io.StringIO("CANDIDATES: structural | x\n"))
    code = refactor_owed.main(["append", str(owed)])
    written = owed.read_bytes() if owed.exists() else b""
    assert (code, written) == (0, b"### \n- x\n")


def test_append_reading_the_real_stdin_as_bytes_keeps_a_crlf_lines_carriage_return_in_the_transform(
        monkeypatch, tmp_path, refactor_owed):
    owed = tmp_path / "owed.md"
    monkeypatch.setattr(sys, "stdin", io.TextIOWrapper(io.BytesIO(b"CANDIDATES: structural | h\r\n")))
    code = refactor_owed.main(["append", str(owed), "S"])
    written = owed.read_bytes() if owed.exists() else b""
    assert (code, written) == (0, b"### S\n- h\r\n")


def test_append_writes_a_structural_transform_holding_non_utf8_bytes_to_the_owed_file_verbatim(
        monkeypatch, tmp_path, refactor_owed):
    owed = tmp_path / "owed.md"
    monkeypatch.setattr(sys, "stdin", io.TextIOWrapper(io.BytesIO(b"CANDIDATES: structural | caf\xe9 \xff\xfe\n")))
    code = refactor_owed.main(["append", str(owed), "S"])
    written = owed.read_bytes() if owed.exists() else b""
    assert (code, written) == (0, b"### S\n- caf\xe9 \xff\xfe\n")


def test_append_records_every_structural_transform_test_only_when_every_bound_on_the_first_line_is_a_test_file(
        monkeypatch, tmp_path, refactor_owed):
    for bounds, all_test in (
            ("a/tests/x,", True), ("x.test.sh", True), ("tests/a\nsrc/b", True),
            (",", False), ("tests/x,,tests/y", False), ("contests/x", False), ("src/tests", False),
            ("Tests/x", False), (" tests/x", False), ("a.tested.sh", False), ("pkg/x.test", False)):
        owed = tmp_path / "owed.md"
        if owed.exists():
            owed.unlink()
        monkeypatch.setattr(sys, "stdin", io.StringIO("CANDIDATES: structural | s\n"))
        code = refactor_owed.main(["append", str(owed), "S", bounds])
        written = owed.read_bytes() if owed.exists() else b""
        expected = b"### S\n- test-only | s\n" if all_test else b"### S\n- s\n"
        assert (bounds, code, written) == (bounds, 0, expected)


def test_render_prints_the_file_under_refactor_owed_with_test_only_lines_moved_under_a_heading_of_their_own(
        monkeypatch, capsys, tmp_path, refactor_owed):
    heading = "## Refactor owed\n\n"
    test_only = ("\n### Test-only\n\n"
                 "These change only files under tests/; the structural pass does not work them.\n\n")
    mixed = tmp_path / "mixed.md"
    mixed.write_text("### S1\n- a\n- test-only | t1\njunk line\n  - test-only | indented\n"
                     "### S2\n- test-only | t2\n")
    structural = tmp_path / "structural.md"
    structural.write_text("### S1\n- a\njunk line\n")
    newline = tmp_path / "newline.md"
    newline.write_text("\n")
    directory = tmp_path / "dd"
    directory.mkdir()
    for path, expected in (
            (mixed, heading + "### S1\n- a\njunk line\n  - test-only | indented\n"
             + test_only + "- t1\n- t2\n"),
            (structural, heading + "### S1\n- a\njunk line\n"),
            (newline, heading + "\n"),
            (directory, heading)):
        code = refactor_owed.main(["render", str(path)])
        captured = capsys.readouterr()
        assert (path.name, code, captured.out) == (path.name, 0, expected)


def test_render_and_list_print_an_owed_file_holding_non_utf8_bytes_verbatim_and_return_0(
        monkeypatch, tmp_path, refactor_owed):
    owed = tmp_path / "owed.md"
    owed.write_bytes(b"### S\n- caf\xe9 \xff\n- test-only | t\xe9\n")
    for verb, expected in (
            ("render", b"## Refactor owed\n\n### S\n- caf\xe9 \xff\n"
             b"\n### Test-only\n\n"
             b"These change only files under tests/; the structural pass does not work them.\n\n"
             b"- t\xe9\n"),
            ("list", b"caf\xe9 \xff\n")):
        stdout = io.TextIOWrapper(io.BytesIO(), write_through=True)
        monkeypatch.setattr(sys, "stdout", stdout)
        code = refactor_owed.main([verb, str(owed)])
        stdout.flush()
        assert (verb, code, stdout.buffer.getvalue()) == (verb, 0, expected)


def test_list_prints_each_structural_transform_once_most_occurrences_first_and_returns_3_when_none_is_left(
        monkeypatch, capsys, tmp_path, refactor_owed):
    mixed = tmp_path / "mixed.md"
    mixed.write_text("-x\n- d\n- a\njunk line\n### S1\n- b\n- a\n- test-only | t\n  - c\n"
                     "- tab\there\n### S2\n- b\n- a\n")
    empty_transforms = tmp_path / "empty-transforms.md"
    empty_transforms.write_text("- \n- \n- z\n")
    empty_last = tmp_path / "empty-last.md"
    empty_last.write_text("- z\n- z\n- \n")
    test_only = tmp_path / "test-only.md"
    test_only.write_text("### S\n- test-only | t1\n- test-only | t2\n")
    only_empty = tmp_path / "only-empty.md"
    only_empty.write_text("### S\n- \n- \n")
    newline = tmp_path / "newline.md"
    newline.write_text("\n")
    directory = tmp_path / "dd"
    directory.mkdir()
    for path, expected in (
            (mixed, (0, "a\nb\nd\ntab\there\n")),
            (empty_transforms, (0, "\nz\n")),
            (empty_last, (0, "z\n")),
            (test_only, (3, "")),
            (only_empty, (3, "")),
            (newline, (3, "")),
            (directory, (3, ""))):
        code = refactor_owed.main(["list", str(path)])
        captured = capsys.readouterr()
        assert (path.name, code, captured.out) == (path.name, *expected)


def test_applied_takes_a_candidate_off_every_step_render_lists_as_owed_and_lists_it_as_applied_naming_the_sha_952(
        monkeypatch, capsys, tmp_path, refactor_owed):
    owed = tmp_path / "owed.md"
    owed.write_text("### S1\n- extract venv_path_advice\n### S2\n- extract venv_path_advice\n")
    code = refactor_owed.main(["applied", str(owed), "extract venv_path_advice", "1a9ce1d"])
    capsys.readouterr()
    assert code == 0

    code = refactor_owed.main(["render", str(owed)])
    out = capsys.readouterr().out
    assert code == 0
    assert [l for l in out.splitlines() if l == "- extract venv_path_advice"] == []
    assert [l for l in out.splitlines() if "extract venv_path_advice" in l and "1a9ce1d" in l] != []


def test_render_still_lists_as_owed_under_its_step_a_candidate_no_applied_call_named_beside_an_applied_one_952(
        monkeypatch, capsys, tmp_path, refactor_owed):
    owed = tmp_path / "owed.md"
    owed.write_text("### S1\n- extract venv_path_advice\n- fold the two awk passes into one\n"
                    "### S2\n- extract venv_path_advice\n- name the bounds walk once\n")
    code = refactor_owed.main(["applied", str(owed), "extract venv_path_advice", "1a9ce1d"])
    capsys.readouterr()
    assert code == 0

    code = refactor_owed.main(["render", str(owed)])
    out = capsys.readouterr().out
    owed_section = out.split("\n### Applied")[0]
    assert (code, owed_section) == (
        0, "## Refactor owed\n\n### S1\n- fold the two awk passes into one\n"
           "### S2\n- name the bounds walk once\n")


def test_main_refuses_an_uppercase_verb_and_returns_1_naming_the_file_when_the_append_write_fails(
        monkeypatch, capsys, tmp_path, refactor_owed):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "stdin", io.StringIO(""))
    owed = tmp_path / "owed.md"
    owed.write_text("- a\n")
    code = refactor_owed.main(["LIST", str(owed)])
    captured = capsys.readouterr()
    assert (code, captured.out, captured.err) == (2, "", USAGE)

    directory = tmp_path / "owed-dir"
    directory.mkdir()
    monkeypatch.setattr(sys, "stdin", io.StringIO("CANDIDATES: structural | x\n"))
    code = refactor_owed.main(["append", str(directory), "S"])
    captured = capsys.readouterr()
    assert (code, captured.out) == (1, "")
    assert len(captured.err.splitlines()) == 1
    assert str(directory) in captured.err


def test_main_answers_every_refactor_owed_contract_case_outside_the_floor_as_the_bash_suite_asserts(
        monkeypatch, capsys, tmp_path, refactor_owed):
    fold = "fold verify.sh's two mktemp calls into one helper"
    hoist = "hoist the ledger path into one variable"
    rename = "rename $tmp to $prompt_file, which is what it holds"
    split = "split the verdict parser out of run-leaf.sh"
    fixtures = "fold the three answers_none fixtures into one helper"
    ledger = "rename $owed_file to $ledger in the list cases"
    lib_walk = "merge the full-path check at lib-walk.test.sh:45 into the /lib/<name>.sh loop"
    test_bounds = "skills/tdd/scripts/tests/unit/lib-walk.test.sh,skills/tdd/scripts/tests/lib/harness.sh"
    mixed_bounds = "skills/tdd/scripts/refactor-owed.sh,skills/tdd/scripts/tests/refactor-owed.test.sh"
    test_only_heading = ("### Test-only\n\n"
                         "These change only files under tests/; the structural pass does not work them.\n\n")

    def run(argv, report=""):
        monkeypatch.setattr(sys, "stdin", io.StringIO(report))
        code = refactor_owed.main(argv)
        return code, capsys.readouterr().out

    def append(owed, step, *lines, bounds=()):
        report = "".join(f"{l}\n" for l in lines)
        return run(["append", str(owed), step, *bounds], report)[0]

    def under_step(text, step, transform):
        lines = text.splitlines()
        heading = lines.index(f"### {step}")
        return f"- {transform}" in lines[heading + 1:]

    owed = tmp_path / "two-appends.md"
    first, second = ("refactor-owed.sh append writes only the structural CANDIDATES lines",
                     "two append calls for different steps keep both steps")
    assert append(owed, first, 'RESULT: applied "x", suite green', "FLAGS: none",
                  f"CANDIDATES: structural | {fold}") == 0
    assert append(owed, second, f"CANDIDATES: cosmetic | reflow the header",
                  f"CANDIDATES: structural | {hoist}") == 0
    text = owed.read_text()
    assert all(w in text for w in (first, second, fold, hoist))

    owed = tmp_path / "render.md"
    append(owed, "first step", "FLAGS: none", f"CANDIDATES: structural | {fold}")
    append(owed, "second step", f"CANDIDATES: structural | {hoist}", f"CANDIDATES: structural | {rename}")
    code, out = run(["render", str(owed)])
    assert (code, out.startswith("## Refactor owed\n")) == (0, True)
    assert all((under_step(out, "first step", fold), under_step(out, "second step", hoist),
                under_step(out, "second step", rename)))

    code, out = run(["list", str(owed)])
    assert (code, out) == (0, f"{fold}\n{hoist}\n{rename}\n")
    absent, empty = tmp_path / "absent.md", tmp_path / "empty.md"
    empty.write_text("")
    for path in (absent, empty):
        assert run(["list", str(path)]) == (3, "")

    owed = tmp_path / "order.md"
    append(owed, "first step", f"CANDIDATES: structural | {fold}", f"CANDIDATES: structural | {hoist}")
    append(owed, "second step", f"CANDIDATES: structural | {hoist}", f"CANDIDATES: structural | {rename}")
    append(owed, "third step", f"CANDIDATES: structural | {rename}", f"CANDIDATES: structural | {hoist}",
           f"CANDIDATES: structural | {split}")
    assert run(["list", str(owed)]) == (0, f"{hoist}\n{rename}\n{fold}\n{split}\n")

    owed = tmp_path / "test-only.md"
    step = "refactor-owed.sh append keeps a test-only candidate under its step"
    assert append(owed, step, f"CANDIDATES: test-only | {fixtures}") == 0
    assert under_step(owed.read_text(), step, f"test-only | {fixtures}")
    assert run(["list", str(owed)]) == (3, "")

    alone, both = tmp_path / "alone.md", tmp_path / "both.md"
    append(alone, "first step", f"CANDIDATES: structural | {fold}", f"CANDIDATES: structural | {hoist}")
    append(alone, "second step", f"CANDIDATES: structural | {hoist}")
    append(both, "first step", f"CANDIDATES: test-only | {fixtures}", f"CANDIDATES: structural | {fold}",
           f"CANDIDATES: test-only | {ledger}", f"CANDIDATES: structural | {hoist}")
    append(both, "second step", f"CANDIDATES: test-only | {fixtures}", f"CANDIDATES: structural | {hoist}",
           f"CANDIDATES: test-only | {ledger}")
    alone_listed = run(["list", str(alone)])
    assert run(["list", str(both)]) == alone_listed == (0, f"{hoist}\n{fold}\n")

    owed = tmp_path / "render-test-only.md"
    append(owed, "first step", f"CANDIDATES: structural | {fold}", f"CANDIDATES: test-only | {fixtures}")
    append(owed, "second step", f"CANDIDATES: test-only | {ledger}", f"CANDIDATES: structural | {hoist}")
    code, out = run(["render", str(owed)])
    section = out[out.index("### Test-only"):] if "### Test-only" in out else ""
    assert (code, out.startswith("## Refactor owed\n"), section) == (
        0, True, f"{test_only_heading}- {fixtures}\n- {ledger}\n")
    assert [out.count(t) for t in (fixtures, ledger)] == [1, 1]

    owed = tmp_path / "structural-only.md"
    append(owed, "first step", f"CANDIDATES: structural | {fold}", "CANDIDATES: cosmetic | rename $tmp")
    assert run(["render", str(owed)]) == (0, "## Refactor owed\n\n" + owed.read_text())

    owed = tmp_path / "test-bounds.md"
    assert append(owed, "a step that touched only test files", 'RESULT: applied "x"', "FLAGS: none",
                  f"CANDIDATES: structural | {lib_walk}", bounds=(test_bounds,)) == 0
    assert run(["list", str(owed)]) == (3, "")
    code, out = run(["render", str(owed)])
    section = out[out.index("### Test-only"):] if "### Test-only" in out else ""
    assert (code, f"- {lib_walk}" in section, out.count(lib_walk)) == (0, True, 1)

    unbounded, bounded = tmp_path / "unbounded.md", tmp_path / "bounded.md"
    for path, bounds in ((unbounded, ()), (bounded, (mixed_bounds,))):
        append(path, "a first step", "CANDIDATES: structural | name the bounds walk once",
               "CANDIDATES: structural | fold the two awk passes into one", bounds=bounds)
        append(path, "a second step", "CANDIDATES: structural | fold the two awk passes into one",
               bounds=bounds)
    want = (0, "fold the two awk passes into one\nname the bounds walk once\n")
    assert run(["list", str(unbounded)]) == run(["list", str(bounded)]) == want


def test_render_prints_no_heading_for_a_step_whose_only_leftovers_are_test_only_and_lists_them_under_test_only_989(
        monkeypatch, capsys, tmp_path, refactor_owed):
    owed = tmp_path / "owed.md"
    monkeypatch.setattr(sys, "stdin", io.StringIO("CANDIDATES: test-only | fold helper A\n"))
    assert refactor_owed.main(["append", str(owed), "step one", "a.sh"]) == 0

    code = refactor_owed.main(["render", str(owed)])
    out = capsys.readouterr().out
    section = out[out.index("### Test-only"):] if "### Test-only" in out else ""
    assert (code, [l for l in out.splitlines() if l == "### step one"], section) == (
        0, [], "### Test-only\n\n"
               "These change only files under tests/; the structural pass does not work them.\n\n"
               "- fold helper A\n")


def test_render_prints_the_structural_steps_heading_and_bullet_and_not_a_test_only_steps_heading_989(
        monkeypatch, capsys, tmp_path, refactor_owed):
    owed = tmp_path / "owed.md"
    monkeypatch.setattr(sys, "stdin", io.StringIO("CANDIDATES: test-only | fold helper A\n"))
    assert refactor_owed.main(["append", str(owed), "step one", "a.sh"]) == 0
    monkeypatch.setattr(sys, "stdin", io.StringIO("CANDIDATES: structural | real one\n"))
    assert refactor_owed.main(["append", str(owed), "step two", "b.sh"]) == 0

    code = refactor_owed.main(["render", str(owed)])
    out = capsys.readouterr().out
    assert (code, [l for l in out.splitlines() if l == "### step one"],
            "### step two\n- real one\n" in out) == (0, [], True)


def test_render_prints_no_heading_for_a_step_whose_every_structural_bullet_is_applied_and_lists_them_under_applied_989(
        monkeypatch, capsys, tmp_path, refactor_owed):
    owed = tmp_path / "o2.md"
    monkeypatch.setattr(sys, "stdin", io.StringIO("CANDIDATES: structural | x\n"))
    assert refactor_owed.main(["append", str(owed), "step A", "b.sh"]) == 0
    assert refactor_owed.main(["applied", str(owed), "x", "abc123"]) == 0

    code = refactor_owed.main(["render", str(owed)])
    out = capsys.readouterr().out
    section = out[out.index("### Applied"):] if "### Applied" in out else ""
    assert (code, [l for l in out.splitlines() if l == "### step A"], section) == (
        0, [], "### Applied\n\n- x — abc123\n")


def test_append_records_an_out_of_scope_candidate_and_list_then_exits_3_printing_nothing_992(
        monkeypatch, capsys, tmp_path, refactor_owed):
    owed = tmp_path / "owed.md"
    monkeypatch.setattr(sys, "stdin", io.StringIO(
        "CANDIDATES: out-of-scope | extract the shared parser across the other scripts\n"))
    appended = refactor_owed.main(["append", str(owed), "step one", "a.sh"])
    recorded = owed.exists() and "extract the shared parser across the other scripts" in owed.read_text()
    capsys.readouterr()

    code = refactor_owed.main(["list", str(owed)])
    assert (appended, recorded, code, capsys.readouterr().out) == (0, True, 3, "")


def test_render_prints_an_out_of_scope_candidate_under_its_own_heading_not_under_its_step_nor_test_only_992(
        monkeypatch, capsys, tmp_path, refactor_owed):
    owed = tmp_path / "owed.md"
    transform = "extract the shared parser across the other scripts"
    monkeypatch.setattr(sys, "stdin", io.StringIO(f"CANDIDATES: out-of-scope | {transform}\n"))
    assert refactor_owed.main(["append", str(owed), "step one", "a.sh"]) == 0

    code = refactor_owed.main(["render", str(owed)])
    lines = capsys.readouterr().out.splitlines()
    heads = [i for i, l in enumerate(lines) if l.startswith("### ") and "out-of-scope" in l.lower()]
    after = lines[heads[0] + 1:] if heads else []
    section = after[:next((i for i, l in enumerate(after) if l.startswith("### ")), len(after))]
    assert (code, [l for l in lines if l == "### step one"], [l for l in section if transform in l],
            sum(transform in l for l in lines)) == (0, [], [f"- {transform}"], 1)
