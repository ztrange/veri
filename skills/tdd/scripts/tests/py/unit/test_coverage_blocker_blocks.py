"""In-process cases for veri/coverage_blocker.py: the body it writes names the new issue as a blocker."""
import importlib
import json
import pathlib

import pytest
from veri.blocked_by import blockers


@pytest.fixture
def coverage_blocker():
    return importlib.import_module("veri.coverage_blocker")


@pytest.fixture
def cover_report(tmp_path, monkeypatch):
    """The working directory moved to tmp_path, holding a cover report that says `COVERED: no` with no `MUTATION:` line (#3943)."""
    (tmp_path / ".tdd").mkdir(exist_ok=True)
    (tmp_path / ".tdd" / "develop-cover.out").write_text("COVERED: no\n")
    (tmp_path / ".tdd" / "issue-60.md").write_text("- [ ] Extract Method `parse` out of `veri/a.py:run`\n")
    monkeypatch.chdir(tmp_path)


@pytest.fixture(autouse=True)
def legacy_label(monkeypatch, coverage_blocker):
    """The repository has a `legacy` label unless a case says otherwise (#4109)."""
    monkeypatch.setattr(coverage_blocker, "gh_label_exists", lambda label: True, raising=False)


def test_main_1262_exits_0_with_the_new_issue_a_blocker_and_every_line_kept_when_the_body_has_no_blocked_by_heading(
        cover_report, monkeypatch, coverage_blocker):
    original = "## Problem\n\nx"
    written = {}

    def fake_edit(n, path):
        written[n] = pathlib.Path(path).read_text()

    monkeypatch.setattr(coverage_blocker, "gh_rest_list", lambda path: "[]")
    monkeypatch.setattr(coverage_blocker, "gh_issue_create",
                        lambda title, text, *extra, **fields: "https://github.com/owner/name/issues/77\n")
    monkeypatch.setattr(coverage_blocker, "gh_issue_view", lambda n, field: original)
    monkeypatch.setattr(coverage_blocker, "gh_issue_edit", fake_edit)

    code = coverage_blocker.main(["60"])

    body = written.get("60", "")
    assert (code, blockers(body, ""), all(line in body.split("\n") for line in original.split("\n"))) == (0, [77], True)


def test_main_1262_exits_0_with_the_new_issue_a_blocker_and_every_line_kept_when_the_blocked_by_heading_has_no_none_or_list_line(
        cover_report, monkeypatch, coverage_blocker):
    original = "## Problem\n\nx\n\n## Blocked by\n\nWaiting on the design.\n\n## Notes\n\ny"
    written = {}

    def fake_edit(n, path):
        written[n] = pathlib.Path(path).read_text()

    monkeypatch.setattr(coverage_blocker, "gh_rest_list", lambda path: "[]")
    monkeypatch.setattr(coverage_blocker, "gh_issue_create",
                        lambda title, text, *extra, **fields: "https://github.com/owner/name/issues/77\n")
    monkeypatch.setattr(coverage_blocker, "gh_issue_view", lambda n, field: original)
    monkeypatch.setattr(coverage_blocker, "gh_issue_edit", fake_edit)

    code = coverage_blocker.main(["60"])

    body = written.get("60", "")
    assert (code, blockers(body, ""), all(line in body.split("\n") for line in original.split("\n"))) == (0, [77], True)


def test_main_1262_exits_0_with_the_new_issue_a_blocker_and_every_line_kept_when_the_only_heading_is_blocked_by_with_a_colon(
        cover_report, monkeypatch, coverage_blocker):
    original = "## Problem\n\nx\n\n## Blocked by:\n\nWaiting on the design.\n\n## Notes\n\ny"
    written = {}

    def fake_edit(n, path):
        written[n] = pathlib.Path(path).read_text()

    monkeypatch.setattr(coverage_blocker, "gh_rest_list", lambda path: "[]")
    monkeypatch.setattr(coverage_blocker, "gh_issue_create",
                        lambda title, text, *extra, **fields: "https://github.com/owner/name/issues/77\n")
    monkeypatch.setattr(coverage_blocker, "gh_issue_view", lambda n, field: original)
    monkeypatch.setattr(coverage_blocker, "gh_issue_edit", fake_edit)

    code = coverage_blocker.main(["60"])

    body = written.get("60", "")
    assert (code, blockers(body, ""), all(line in body.split("\n") for line in original.split("\n"))) == (0, [77], True)


def test_main_1262_exits_0_with_the_new_issue_a_blocker_when_the_heading_carries_none_replaced_or_list_lines_kept(
        cover_report, monkeypatch, coverage_blocker):
    written = {}

    def fake_edit(n, path):
        written[n] = pathlib.Path(path).read_text()

    monkeypatch.setattr(coverage_blocker, "gh_rest_list", lambda path: "[]")
    monkeypatch.setattr(coverage_blocker, "gh_issue_create",
                        lambda title, text, *extra, **fields: "https://github.com/owner/name/issues/77\n")
    monkeypatch.setattr(coverage_blocker, "gh_issue_edit", fake_edit)

    seen = []
    for original, expected in (("## Problem\n\nx\n\n## Blocked by\n\nNone.\n\nTest command: make test", [77]),
                               ("## Problem\n\nx\n\n## Blocked by\n\n- #5\n- #6\n\nTest command: make test", [5, 6, 77])):
        monkeypatch.setattr(coverage_blocker, "gh_issue_view", lambda n, field, body=original: body)
        code = coverage_blocker.main(["60"])
        body = written.get("60", "")
        kept = [line for line in original.split("\n") if line != "None."]
        seen.append((code, sorted(blockers(body, "")), all(line in body.split("\n") for line in kept), expected))

    assert [(c, b, k) for c, b, k, _ in seen] == [(0, e, True) for *_, e in seen]


def test_main_1262_writes_nothing_exits_2_and_names_the_issue_on_stderr_when_the_create_answers_no_issue_number(
        cover_report, monkeypatch, capsys, coverage_blocker):
    edits = []

    monkeypatch.setattr(coverage_blocker, "gh_rest_list", lambda path: "[]")
    monkeypatch.setattr(coverage_blocker, "gh_issue_create", lambda title, text, *extra, **fields: "")
    monkeypatch.setattr(coverage_blocker, "gh_issue_view", lambda n, field: "## Problem\n\nx")
    monkeypatch.setattr(coverage_blocker, "gh_issue_edit", lambda n, path: edits.append(n))

    code = coverage_blocker.main(["60"])

    assert (code, edits, "60" in capsys.readouterr().err) == (2, [], True)


def test_main_1262_writes_nothing_and_exits_2_when_the_new_issue_is_numbered_but_the_body_it_would_write_still_reads_as_unblocked(
        cover_report, monkeypatch, capsys, coverage_blocker):
    edits = []

    monkeypatch.setattr(coverage_blocker, "gh_rest_list", lambda path: "[]")
    monkeypatch.setattr(coverage_blocker, "gh_issue_create",
                        lambda title, text, *extra, **fields: "https://github.com/owner/name/issues/77\n")
    monkeypatch.setattr(coverage_blocker, "gh_issue_view",
                        lambda n, field: "## Blocked by\n\nfoo\n\n## Blocked by\n\n- #5")
    monkeypatch.setattr(coverage_blocker, "gh_issue_edit", lambda n, path: edits.append(n))

    code = coverage_blocker.main(["60"])

    assert (code, edits, "60" in capsys.readouterr().err) == (2, [], True)


def test_main_1262_writes_the_blocker_directly_under_a_heading_followed_by_prose_and_keeps_every_byte_of_the_prose(
        cover_report, monkeypatch, coverage_blocker):
    written = {}

    def fake_edit(n, path):
        written[n] = pathlib.Path(path).read_text()

    monkeypatch.setattr(coverage_blocker, "gh_rest_list", lambda path: "[]")
    monkeypatch.setattr(coverage_blocker, "gh_issue_create",
                        lambda title, text, *extra, **fields: "https://github.com/owner/name/issues/77\n")
    monkeypatch.setattr(coverage_blocker, "gh_issue_view",
                        lambda n, field: "## Problem\n\nx\n\n## Blocked by\nWaiting on design.\n\n## Notes\n\ny")
    monkeypatch.setattr(coverage_blocker, "gh_issue_edit", fake_edit)

    code = coverage_blocker.main(["60"])

    assert (code, written.get("60")) == (
        0, "## Problem\n\nx\n\n## Blocked by\n- #77\nWaiting on design.\n\n## Notes\n\ny\n")


def test_main_3721_files_a_cover_issue_whose_body_opens_with_a_problem_heading_over_the_refusal_text(
        cover_report, monkeypatch, coverage_blocker):
    created = []

    monkeypatch.setattr(coverage_blocker, "gh_rest_list", lambda path: "[]")
    monkeypatch.setattr(coverage_blocker, "gh_issue_create",
                        lambda title, text, *extra, **fields: created.append(text) or "https://github.com/owner/name/issues/77\n")
    monkeypatch.setattr(coverage_blocker, "gh_issue_view", lambda n, field: "## Problem\n\nx")
    monkeypatch.setattr(coverage_blocker, "gh_issue_edit", lambda n, path: None)

    coverage_blocker.main(["60"])

    body = created[0] if created else ""
    lines = body.split("\n")
    assert (lines[0], "Refactor #60 refused" in "\n".join(lines[1:])) == ("## Problem", True)


def test_main_3721_files_a_cover_issue_with_an_acceptance_criterion_quoting_the_mutation_line_of_the_cover_report(
        monkeypatch, tmp_path, coverage_blocker):
    created = []
    mutation = "MUTATION: veri/status.py: recover_prs `if single.returncode != 0` -> `False`"
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "develop-cover.out").write_text("narration\nCOVERED: no\nCAUGHT_BY: NONE\n" + mutation + "\n")
    (tmp_path / ".tdd" / "issue-60.md").write_text("- [ ] Extract Method `parse` out of `veri/a.py:run`\n")
    monkeypatch.chdir(tmp_path)

    monkeypatch.setattr(coverage_blocker, "gh_rest_list", lambda path: "[]")
    monkeypatch.setattr(coverage_blocker, "gh_issue_create",
                        lambda title, text, *extra, **fields: created.append(text) or "https://github.com/owner/name/issues/77\n")
    monkeypatch.setattr(coverage_blocker, "gh_issue_view", lambda n, field: "## Problem\n\nx")
    monkeypatch.setattr(coverage_blocker, "gh_issue_edit", lambda n, path: None)

    coverage_blocker.main(["60"])

    body = created[0] if created else ""
    section = body.split("## Acceptance criteria", 1)[1] if "## Acceptance criteria" in body else ""
    criteria = [line for line in section.split("\n## ", 1)[0].split("\n") if line.startswith("- [ ]")]
    assert (len(criteria), len(criteria) == 1 and mutation in criteria[0]) == (1, True)


def test_main_3721_files_the_acceptance_criteria_section_only_when_the_cover_report_says_covered_no_with_a_mutation_line(
        monkeypatch, tmp_path, coverage_blocker):
    created = []
    mutation = "MUTATION: veri/status.py: recover_prs `if single.returncode != 0` -> `False`"
    reports = {
        "no-with-mutation": "COVERED: no\n" + mutation + "\n",
        "no-without-mutation": "COVERED: no\nCAUGHT_BY: NONE\n",
        "yes-with-mutation": "COVERED: yes\n" + mutation + "\n",
    }
    (tmp_path / ".tdd").mkdir()
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(coverage_blocker, "gh_rest_list", lambda path: "[]")
    monkeypatch.setattr(coverage_blocker, "gh_issue_create",
                        lambda title, text, *extra, **fields: created.append(text) or "https://github.com/owner/name/issues/77\n")
    monkeypatch.setattr(coverage_blocker, "gh_issue_view", lambda n, field: "## Problem\n\nx")
    monkeypatch.setattr(coverage_blocker, "gh_issue_edit", lambda n, path: None)

    has_section = {}
    for name, report in reports.items():
        created.clear()
        (tmp_path / ".tdd" / "develop-cover.out").write_text(report)
        (tmp_path / ".tdd" / "issue-60.md").write_text("- [ ] Extract Method `parse` out of `veri/a.py:run`\n")
        coverage_blocker.main(["60"])
        has_section[name] = bool(created) and "## Acceptance criteria" in created[0]

    assert has_section == {"no-with-mutation": True, "no-without-mutation": False, "yes-with-mutation": False}


def test_main_3721_files_an_acceptance_criterion_that_requires_a_case_going_red_under_the_quoted_mutation(
        monkeypatch, tmp_path, coverage_blocker):
    created = []
    mutation = "MUTATION: veri/status.py: recover_prs `if single.returncode != 0` -> `False`"
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "develop-cover.out").write_text("COVERED: no\n" + mutation + "\n")
    (tmp_path / ".tdd" / "issue-60.md").write_text("- [ ] Extract Method `parse` out of `veri/a.py:run`\n")
    monkeypatch.chdir(tmp_path)

    monkeypatch.setattr(coverage_blocker, "gh_rest_list", lambda path: "[]")
    monkeypatch.setattr(coverage_blocker, "gh_issue_create",
                        lambda title, text, *extra, **fields: created.append(text) or "https://github.com/owner/name/issues/77\n")
    monkeypatch.setattr(coverage_blocker, "gh_issue_view", lambda n, field: "## Problem\n\nx")
    monkeypatch.setattr(coverage_blocker, "gh_issue_edit", lambda n, path: None)

    coverage_blocker.main(["60"])

    body = created[0] if created else ""
    criteria = [line for line in body.split("\n") if line.startswith("- [ ]") and mutation in line]
    words = criteria[0].lower() if criteria else ""
    assert (len(criteria), "case" in words, "goes red" in words) == (1, True, True)


def test_main_3721_files_a_cover_issue_whose_blocked_by_section_holds_the_line_none(
        monkeypatch, tmp_path, coverage_blocker):
    created = []
    mutation = "MUTATION: veri/status.py: recover_prs `if single.returncode != 0` -> `False`"
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "develop-cover.out").write_text("COVERED: no\n" + mutation + "\n")
    (tmp_path / ".tdd" / "issue-60.md").write_text("- [ ] Extract Method `parse` out of `veri/a.py:run`\n")
    monkeypatch.chdir(tmp_path)

    monkeypatch.setattr(coverage_blocker, "gh_rest_list", lambda path: "[]")
    monkeypatch.setattr(coverage_blocker, "gh_issue_create",
                        lambda title, text, *extra, **fields: created.append(text) or "https://github.com/owner/name/issues/77\n")
    monkeypatch.setattr(coverage_blocker, "gh_issue_view", lambda n, field: "## Problem\n\nx")
    monkeypatch.setattr(coverage_blocker, "gh_issue_edit", lambda n, path: None)

    coverage_blocker.main(["60"])

    body = created[0] if created else ""
    section = body.split("\n## Blocked by\n", 1)[1] if "\n## Blocked by\n" in body else ""
    section_lines = [line for line in section.split("\n## ", 1)[0].split("\n") if line.strip()]
    assert section_lines == ["None."]


def test_main_3721_files_a_cover_issue_whose_last_line_is_the_test_command_of_the_all_tier(
        monkeypatch, tmp_path, coverage_blocker):
    created = []
    mutation = "MUTATION: veri/status.py: recover_prs `if single.returncode != 0` -> `False`"
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "develop-cover.out").write_text("COVERED: no\n" + mutation + "\n")
    (tmp_path / ".tdd" / "issue-60.md").write_text("- [ ] Extract Method `parse` out of `veri/a.py:run`\n")
    (tmp_path / "CLAUDE.md").write_text("veri: fast tests: `make quick`\nveri: all tests: `make everything`\n")
    monkeypatch.chdir(tmp_path)

    monkeypatch.setattr(coverage_blocker, "gh_rest_list", lambda path: "[]")
    monkeypatch.setattr(coverage_blocker, "gh_issue_create",
                        lambda title, text, *extra, **fields: created.append(text) or "https://github.com/owner/name/issues/77\n")
    monkeypatch.setattr(coverage_blocker, "gh_issue_view", lambda n, field: "## Problem\n\nx")
    monkeypatch.setattr(coverage_blocker, "gh_issue_edit", lambda n, path: None)

    coverage_blocker.main(["60"])

    body = created[0] if created else ""
    assert body.rstrip("\n").split("\n")[-1] == "Test command: make everything"


def test_main_3721_files_a_cover_issue_carrying_the_opt_in_label_of_the_run(
        monkeypatch, tmp_path, coverage_blocker):
    labels = []
    monkeypatch.setenv("VERI_LABEL", "ready-for-agent:mu")
    (tmp_path / ".tdd").mkdir()
    (tmp_path / ".tdd" / "develop-cover.out").write_text("COVERED: no\nMUTATION: veri/a.py: f `x` -> `y`\n")
    (tmp_path / ".tdd" / "issue-60.md").write_text("- [ ] Extract Method `parse` out of `veri/a.py:run`\n")
    monkeypatch.chdir(tmp_path)

    def fake_create(title, text, *extra, **fields):
        labels.extend(str(v) for v in (*extra, *fields.values()))
        return "https://github.com/owner/name/issues/77\n"

    monkeypatch.setattr(coverage_blocker, "gh_rest_list", lambda path: "[]")
    monkeypatch.setattr(coverage_blocker, "gh_issue_create", fake_create)
    monkeypatch.setattr(coverage_blocker, "gh_issue_add_label", lambda n, label: labels.append(label), raising=False)
    monkeypatch.setattr(coverage_blocker, "gh_issue_view", lambda n, field: "## Problem\n\nx")
    monkeypatch.setattr(coverage_blocker, "gh_issue_edit", lambda n, path: None)

    coverage_blocker.main(["60"])

    assert "ready-for-agent:mu" in labels


def test_main_3721_files_a_cover_issue_carrying_filed_by_the_lane_after_the_last_colon_of_the_label_or_main(
        cover_report, monkeypatch, tmp_path, coverage_blocker):
    monkeypatch.chdir(tmp_path)
    seen = {}
    current = []

    def fake_create(title, text, *extra, **fields):
        current.extend(str(v) for v in (*extra, *fields.values()))
        return "https://github.com/owner/name/issues/77\n"

    monkeypatch.setattr(coverage_blocker, "gh_rest_list", lambda path: "[]")
    monkeypatch.setattr(coverage_blocker, "gh_issue_create", fake_create)
    monkeypatch.setattr(coverage_blocker, "gh_issue_add_label", lambda n, label: current.append(label), raising=False)
    monkeypatch.setattr(coverage_blocker, "gh_issue_view", lambda n, field: "## Problem\n\nx")
    monkeypatch.setattr(coverage_blocker, "gh_issue_edit", lambda n, path: None)

    for label, lane in (("ready-for-agent:mu", "mu"), ("ready-for-agent", "main"), ("a:b:c", "c")):
        current.clear()
        monkeypatch.setenv("VERI_LABEL", label)
        coverage_blocker.main(["60"])
        seen[label] = "filed-by:" + lane in current

    assert seen == {"ready-for-agent:mu": True, "ready-for-agent": True, "a:b:c": True}


def _label_run(monkeypatch, tmp_path, coverage_blocker, report):
    labels = []
    (tmp_path / ".tdd").mkdir(parents=True, exist_ok=True)
    if report is not None:
        (tmp_path / ".tdd" / "develop-cover.out").write_text(report)
        (tmp_path / ".tdd" / "issue-60.md").write_text("- [ ] Extract Method `parse` out of `veri/a.py:run`\n")
    monkeypatch.chdir(tmp_path)

    def fake_create(title, text, *extra, **fields):
        labels.extend(str(v) for v in (*extra, *fields.values()))
        return "https://github.com/owner/name/issues/77\n"

    monkeypatch.setattr(coverage_blocker, "gh_rest_list", lambda path: "[]")
    monkeypatch.setattr(coverage_blocker, "gh_issue_create", fake_create)
    monkeypatch.setattr(coverage_blocker, "gh_issue_add_label", lambda n, label: labels.append(label), raising=False)
    monkeypatch.setattr(coverage_blocker, "gh_issue_view", lambda n, field: "## Problem\n\nx")
    monkeypatch.setattr(coverage_blocker, "gh_issue_edit", lambda n, path: None)
    coverage_blocker.main(["60"])
    return labels


def test_main_3721_files_a_cover_issue_carrying_ready_for_agent_when_veri_label_is_unset(
        monkeypatch, tmp_path, coverage_blocker):
    monkeypatch.delenv("VERI_LABEL", raising=False)

    labels = _label_run(monkeypatch, tmp_path, coverage_blocker, "COVERED: no\nMUTATION: veri/a.py: f `x` -> `y`\n")

    assert "ready-for-agent" in labels


def test_main_3721_files_a_cover_issue_without_the_opt_in_label_when_the_probe_gave_no_mutation_line(
        monkeypatch, tmp_path, coverage_blocker):
    monkeypatch.setenv("VERI_LABEL", "ready-for-agent:mu")

    labels = {name: _label_run(monkeypatch, tmp_path / name, coverage_blocker, report)
              for name, report in (("none", ""), ("nomut", "COVERED: no\nCAUGHT_BY: NONE\n"))}

    assert {k: ("ready-for-agent:mu" in v, "filed-by:mu" in v) for k, v in labels.items()} == {
        "none": (False, True), "nomut": (False, True)}


def test_main_4109_files_the_cover_issue_labelled_legacy_beside_the_opt_in_label_and_filed_by_the_lane(
        monkeypatch, tmp_path, coverage_blocker):
    monkeypatch.setenv("VERI_LABEL", "ready-for-agent:mu")

    labels = {name: _label_run(monkeypatch, tmp_path / name, coverage_blocker, report)
              for name, report in (("mut", "COVERED: no\nMUTATION: veri/a.py: f `x` -> `y`\n"), ("nomut", "COVERED: no\n"))}

    assert {k: sorted(v) for k, v in labels.items()} == {
        "mut": ["filed-by:mu", "legacy", "ready-for-agent:mu"], "nomut": ["filed-by:mu", "legacy"]}


LEDGER = ("# Plan for #60\n\n- [x] Extract Method `parse` out of `veri/a.py:run`\n"
          "- [ ] Inline Variable `tmp` in `veri/a.py:parse` ⟦criterion 2⟧\n- [ ] Rename `x` to `count`\n")


def _region_run(monkeypatch, tmp_path, coverage_blocker, ledger, open_issues="[]"):
    created = []
    (tmp_path / ".tdd").mkdir(parents=True, exist_ok=True)
    (tmp_path / ".tdd" / "develop-cover.out").write_text("COVERED: no\nMUTATION: veri/a.py: parse `x` -> `y`\n")
    if ledger is not None:
        (tmp_path / ".tdd" / "issue-60.md").write_text(ledger)
    monkeypatch.chdir(tmp_path)
    edited = []
    monkeypatch.setattr(coverage_blocker, "gh_rest_list", lambda path: open_issues)
    monkeypatch.setattr(coverage_blocker, "gh_issue_create",
                        lambda title, text, *extra, **fields: created.append(text) or "https://github.com/owner/name/issues/77\n")
    monkeypatch.setattr(coverage_blocker, "gh_issue_view", lambda n, field: "## Problem\n\nx")
    monkeypatch.setattr(coverage_blocker, "gh_issue_edit", lambda n, path: edited.append(n))
    return coverage_blocker.main(["60"]), created, edited


def _section(body, heading):
    return body.split("\n## " + heading + "\n", 1)[1].split("\n## ", 1)[0].strip("\n") if "\n## " + heading + "\n" in body else None


def test_main_4109_files_a_region_section_holding_the_refactor_steps_ledger_line_as_current_or_last_done_prints_it(
        monkeypatch, tmp_path, coverage_blocker):
    lines = {}
    for name, ledger in (("open", LEDGER), ("done", LEDGER.replace("- [ ]", "- [x]"))):
        code, created, _ = _region_run(monkeypatch, tmp_path / name, coverage_blocker, ledger)
        lines[name] = (code, _section(created[0], "Region") if created else None)

    assert lines == {"open": (0, "Inline Variable `tmp` in `veri/a.py:parse` ⟦criterion 2⟧"),
                     "done": (0, "Rename `x` to `count`")}


def test_main_4109_places_the_region_section_after_the_problem_and_before_the_acceptance_criteria(
        monkeypatch, tmp_path, coverage_blocker):
    _, created, _ = _region_run(monkeypatch, tmp_path, coverage_blocker, LEDGER)

    headings = [line for line in (created[0] if created else "").split("\n") if line.startswith("## ")]
    assert headings == ["## Problem", "## Region", "## Acceptance criteria", "## Blocked by"]


def test_main_4109_exits_2_filing_and_editing_nothing_naming_the_ledger_when_it_is_absent_or_holds_no_step(
        monkeypatch, tmp_path, coverage_blocker, capsys):
    seen = {}
    for name, ledger in (("absent", None), ("empty", "# Plan for #60\n")):
        code, created, edited = _region_run(monkeypatch, tmp_path / name, coverage_blocker, ledger)
        seen[name] = (code, created, edited, ".tdd/issue-60.md" in capsys.readouterr().err)

    assert seen == {"absent": (2, [], [], True), "empty": (2, [], [], True)}


def test_main_4109_blocks_on_an_old_shape_coverage_issue_already_open_with_the_title_without_relabelling_or_refiling_it(
        monkeypatch, tmp_path, coverage_blocker, capsys):
    looked_up = []
    monkeypatch.setattr(coverage_blocker, "gh_label_exists", lambda label: looked_up.append(label) or True)
    open_issues = json.dumps([{"title": "Cover the behaviour #60 refactors", "html_url": "https://github.com/owner/name/issues/55"}])

    code, created, edited = _region_run(monkeypatch, tmp_path, coverage_blocker, LEDGER, open_issues)

    assert (code, created, looked_up, edited, capsys.readouterr().out) == (
        0, [], [], ["60"], "https://github.com/owner/name/issues/55\n")
