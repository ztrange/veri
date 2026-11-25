"""In-process cases for veri/mutation_record.py, the owner of issue-<n>-mutations.md."""
import base64
import importlib

import pytest


def mr():
    return importlib.import_module("veri.mutation_record")


def b64(text):
    return base64.b64encode(text.encode()).decode()


def test_path_is_the_issues_mutations_file_in_the_runs_tdd_directory():
    assert mr().path("/r", 12) == "/r/.tdd/issue-12-mutations.md"


def test_of_ledger_swaps_the_ledgers_md_suffix_for_mutations_md():
    assert mr().of_ledger("/r/.tdd/issue-3.md") == "/r/.tdd/issue-3-mutations.md"


@pytest.mark.parametrize("name,expect", [
    ("issue-4-mutations.md", True),
    ("issue-45-mutations.md", True),
    ("issue--mutations.md", False),
    ("issue-4.md", False),
    ("issue-4-mutations.md.bak", False),
    ("x-issue-4-mutations.md", False),
])
def test_is_record_answers_for_the_basename_of_a_path(name, expect):
    assert mr().is_record("/any/dir/" + name) is expect


def test_number_is_the_issue_number_in_the_records_name():
    assert mr().number("/r/.tdd/issue-77-mutations.md") == "77"


def test_paths_lists_the_records_of_the_run_sorted_and_relative_when_the_run_is_empty(tmp_path, monkeypatch):
    (tmp_path / ".tdd").mkdir()
    for name in ("issue-2-mutations.md", "issue-10-mutations.md", "issue-2.md", "other"):
        (tmp_path / ".tdd" / name).write_text("x")
    monkeypatch.chdir(tmp_path)

    assert mr().paths() == [".tdd/issue-10-mutations.md", ".tdd/issue-2-mutations.md"]
    assert mr().paths(str(tmp_path)) == [str(tmp_path / ".tdd" / "issue-10-mutations.md"),
                                         str(tmp_path / ".tdd" / "issue-2-mutations.md")]


def test_snapshot_maps_each_records_path_to_its_bytes(tmp_path, monkeypatch):
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "issue-2-mutations.md").write_bytes(b"\xff raw\n")
    monkeypatch.chdir(tmp_path)

    assert mr().snapshot() == {".tdd/issue-2-mutations.md": b"\xff raw\n"}


def test_format_record_writes_name_size_value_lines_and_a_blank_terminator_encoding_text_fields():
    text = mr().format_record([("before", "abc1234"), ("old", "a\nb"), ("command", "t")])

    assert text == f"before 7\nabc1234\nold-b64 {len(b64('a' + chr(10) + 'b'))}\n{b64('a' + chr(10) + 'b')}\ncommand 1\nt\n\n"


def test_append_adds_one_record_to_the_end_of_the_file(tmp_path):
    record = tmp_path / "r.md"
    record.write_text("keep\n")

    mr().append(str(record), [("before", "abc1234")])

    assert record.read_text() == "keep\nbefore 7\nabc1234\n\n"


def test_records_parses_what_format_record_wrote_decoding_text_fields():
    text = (mr().format_record([("before", "abc1234"), ("old", "a\nb"), ("new", ""), ("command", "t x")])
            + mr().format_record([("file", "f.py"), ("context", "ctx")]))

    assert mr().records(text) == [
        {"before": "abc1234", "command": "t x", "old": "a\nb", "new": ""},
        {"file": "f.py", "context": "ctx"},
    ]


def test_records_skips_blank_lines_between_and_before_records():
    assert mr().records("\n\nfile 1\nf\n\n\n\nfile 1\ng\n\n") == [{"file": "f"}, {"file": "g"}]


def test_chunks_yield_each_records_raw_text_with_its_trailing_blank_lines_and_raw_fields():
    text = "file 1\nf\ncommand 2\nab\n\n\nfile 1\ng\n\n"

    assert mr().chunks(text) == [
        ("file 1\nf\ncommand 2\nab\n\n\n", {"file": "f", "command": "ab"}),
        ("file 1\ng\n\n", {"file": "g"}),
    ]
    assert "".join(raw for raw, _ in mr().chunks(text)) == text


def test_chunks_name_the_malformed_header_line():
    with pytest.raises(mr().MalformedRecord) as caught:
        mr().chunks("not a header\nx\n")

    assert caught.value.header == "not a header"
    assert isinstance(caught.value, ValueError)
