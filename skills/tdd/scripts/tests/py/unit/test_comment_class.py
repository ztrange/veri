"""In-process cases for veri/comment_class.py, the module comment-class.sh is a shim over."""
import collections
import importlib
import io
import pathlib
import pytest
import re
import sys

from conftest import SCRIPTS


def test_main_with_no_argument_returns_2_naming_its_usage(capsys):
    comment_class = importlib.import_module("veri.comment_class")

    refused = comment_class.main([])
    refusal = capsys.readouterr()

    assert (refused, refusal.out, refusal.err) == (2, "", "usage: comment-class.sh [--sweepable] <file>…\n")


def test_main_prints_each_hash_line_with_its_class_and_sweepable_keeps_classes_1_and_2_less_the_header(tmp_path, capsys):
    comment_class = importlib.import_module("veri.comment_class")
    script = tmp_path / "s.sh"
    script.write_text(
        "#!/bin/sh\n"
        "# a contract header\n"
        "echo one\n"
        "# a comment in code\n"
        "cat > out.txt <<EOF\n"
        "# written to a file\n"
        "EOF\n"
        "cat <<EOF\n"
        "# in any other heredoc\n"
        "EOF\n"
    )

    every = comment_class.main([str(script)])
    every_out = capsys.readouterr().out
    sweepable = comment_class.main(["--sweepable", str(script)])
    sweepable_out = capsys.readouterr().out

    assert (every, every_out, sweepable, sweepable_out) == (
        0,
        f"{script}:1:1\n{script}:2:1\n{script}:4:1\n{script}:6:2\n{script}:9:3\n",
        0,
        f"{script}:4:1\n{script}:6:2\n",
    )


def test_main_classes_a_heredoc_line_by_its_target_never_as_class_1_and_never_carries_a_heredoc_into_the_next_file(tmp_path, capsys):
    comment_class = importlib.import_module("veri.comment_class")
    fixtures = {
        "mixed": ("# a comment in code", "cat << EOF", "# a line in a heredoc", "EOF", "# a comment after the heredoc"),
        "open": ("cat <<EOF", "# a line in a heredoc"),
        "after": ("# a comment in code",),
        "delims": (
            "cat <<'EOF'", "# in a single-quoted heredoc", "EOF", 'cat <<"EOF"', "# in a double-quoted heredoc", "EOF",
            "cat <<-EOF", "# in a dash heredoc", "\tEOF", "cat <<< word", "# a comment after a here-string",
        ),
        "targets": (
            'cat > "$dir/fixture.txt" <<EOF', "# written to a file", "EOF", "claude -p <<EOF", "# sent to a model", "EOF",
            'prompt="$(cat <<EOF', "# held in a variable", "EOF", ')"', "cat <<EOF", "# printed to stdout", "EOF",
            "cat >&2 <<EOF", "# printed to stderr", "EOF",
        ),
        "fd-redirect": ("claude -p 2>/dev/null <<EOF", "# sent to a model with stderr discarded", "EOF"),
        "piped-tee": ('cat <<EOF | tee "$dir/fixture.txt"', "# written to a file through tee", "EOF"),
    }
    paths = {}
    for name, lines in fixtures.items():
        paths[name] = tmp_path / f"{name}.sh"
        paths[name].write_text("\n".join(lines) + "\n")

    def classify(*names):
        code = comment_class.main([str(paths[name]) for name in names])
        return code, capsys.readouterr().out

    p = {name: str(path) for name, path in paths.items()}
    assert {
        "mixed": classify("mixed"),
        "open-then-after": classify("open", "after"),
        "delims": classify("delims"),
        "targets": classify("targets"),
        "fd-redirect": classify("fd-redirect"),
        "piped-tee": classify("piped-tee"),
    } == {
        "mixed": (0, f"{p['mixed']}:1:1\n{p['mixed']}:3:3\n{p['mixed']}:5:1\n"),
        "open-then-after": (0, f"{p['open']}:2:3\n{p['after']}:1:1\n"),
        "delims": (0, f"{p['delims']}:2:3\n{p['delims']}:5:3\n{p['delims']}:8:3\n{p['delims']}:11:1\n"),
        "targets": (
            0,
            f"{p['targets']}:2:2\n{p['targets']}:5:3\n{p['targets']}:8:3\n{p['targets']}:12:3\n{p['targets']}:15:3\n",
        ),
        "fd-redirect": (0, f"{p['fd-redirect']}:2:3\n"),
        "piped-tee": (0, f"{p['piped-tee']}:2:2\n"),
    }


def test_main_classes_dd_and_sponge_writes_as_2_and_sweepable_drops_class_3_the_header_hazards_and_quoted_heredoc_operators(tmp_path, capsys):
    comment_class = importlib.import_module("veri.comment_class")
    header = (
        "#!/usr/bin/env bash", "# tool.sh — print its one argument.", "#", "# Usage: tool.sh <arg>",
        "# Exit: 0 printed, 2 bad arguments.", "set -uo pipefail", "",
        "# hazard: under set -u an unset name exits with the status of the previous command", 'echo "${1:-}"',
    )
    fixtures = {
        "piped-writers": (
            'cat <<EOF | dd of="$dir/fixture.txt"', "# written to a file through dd", "EOF",
            'cat <<EOF | sponge "$dir/fixture.txt"', "# written to a file through sponge", "EOF",
        ),
        "sweepable": (
            "# a comment in code", 'cat > "$dir/fixture.txt" <<EOF', "# written to a file", "EOF",
            "claude -p <<EOF", "# sent to a model", "EOF",
        ),
        "header-hazard": header,
        "header-then-code-comment": header + ("# print the argument, or nothing", 'echo "${1:-}"'),
        "quoted-heredoc-operator": (
            "got=\"$(cat \"$p\" 2>/dev/null || echo '<<no file>>')\"", "cat > \"$dir/stub\" <<'L'", "#!/bin/sh", "L",
        ),
        "double-quoted-heredoc-operator": ('echo "<<no file>>"', "cat > \"$dir/stub\" <<'L'", "#!/bin/sh", "L"),
    }
    p = {}
    for name, lines in fixtures.items():
        path = tmp_path / f"{name}.sh"
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        p[name] = str(path)

    def classify(*argv):
        code = comment_class.main(list(argv))
        return code, capsys.readouterr().out

    assert {
        "piped-writers": classify(p["piped-writers"]),
        "sweepable": classify("--sweepable", p["sweepable"]),
        "header-hazard": classify("--sweepable", p["header-hazard"]),
        "header-then-code-comment": classify("--sweepable", p["header-then-code-comment"]),
        "quoted-heredoc-operator": classify("--sweepable", p["quoted-heredoc-operator"]),
        "double-quoted-heredoc-operator": classify("--sweepable", p["double-quoted-heredoc-operator"]),
    } == {
        "piped-writers": (0, f"{p['piped-writers']}:2:2\n{p['piped-writers']}:5:2\n"),
        "sweepable": (0, f"{p['sweepable']}:1:1\n{p['sweepable']}:3:2\n"),
        "header-hazard": (0, ""),
        "header-then-code-comment": (0, f"{p['header-then-code-comment']}:10:1\n"),
        "quoted-heredoc-operator": (0, ""),
        "double-quoted-heredoc-operator": (0, ""),
    }


def test_main_skips_quoted_strings_and_the_heredoc_opening_hashbang_and_classes_md_writes_as_3(tmp_path, capsys):
    comment_class = importlib.import_module("veri.comment_class")
    fixtures = {
        "quoted": (
            "x='first", "# inside a single-quoted string", "last'", 'y="first', "# inside a double-quoted string",
            'last"', "# a comment in code",
        ),
        "quote-edges": (
            'a="say \\"hi', "# inside, after an escaped quote", 'bye"', "b=1 # it's a trailing comment",
            "# a comment after a trailing one", "echo c#'", "# inside, after a # inside a word", "'",
        ),
        "stub-writer": (
            "cat > stub <<'EOF'", "#!/bin/sh", "echo hi", "# a comment later in the body", "#!/bin/sh later in the body",
            "EOF",
        ),
        "md-writer": ('cat > "$dir/CLAUDE.md" <<EOF', "# a markdown heading", "EOF"),
        "md-tee": ('cat <<EOF | tee -a "$dir/SPEC.md"', "# a markdown heading", "EOF"),
        "md-dd": ('cat <<EOF | dd of="$dir/CLAUDE.md"', "# a markdown heading", "EOF"),
        "md-sponge": ('cat <<EOF | sponge "$dir/SPEC.md"', "# a markdown heading", "EOF"),
    }
    p = {}
    for name, lines in fixtures.items():
        path = tmp_path / f"{name}.sh"
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        p[name] = str(path)

    def classify(*argv):
        code = comment_class.main(list(argv))
        return code, capsys.readouterr().out

    assert {
        "quoted": classify(p["quoted"]),
        "quote-edges": classify(p["quote-edges"]),
        "stub-writer": classify("--sweepable", p["stub-writer"]),
        "md-writers": classify(p["md-writer"], p["md-tee"]),
        "md-piped-writers": classify(p["md-dd"], p["md-sponge"]),
    } == {
        "quoted": (0, f"{p['quoted']}:7:1\n"),
        "quote-edges": (0, f"{p['quote-edges']}:5:1\n"),
        "stub-writer": (0, f"{p['stub-writer']}:4:2\n{p['stub-writer']}:5:2\n"),
        "md-writers": (0, f"{p['md-writer']}:2:3\n{p['md-tee']}:2:3\n"),
        "md-piped-writers": (0, f"{p['md-dd']}:2:3\n{p['md-sponge']}:2:3\n"),
    }


def test_main_classes_md_variable_heredocs_as_3_drops_a_dash_heredoc_hashbang_and_reads_quotes_inside_command_substitutions(tmp_path, capsys):
    comment_class = importlib.import_module("veri.comment_class")
    fixtures = {
        "md-var": ('f="$dir/x.md"; cat > "$f" <<\'EOF\'', "# a markdown heading", "EOF"),
        "stub-writer-dash": ("cat > stub <<-'EOF'", "\t#!/bin/sh", "\techo hi", "\tEOF"),
        "quote-in-subst": ("x=\"$(echo 'a \"b')\"", "# a comment in code"),
        "subshell-in-subst": ("x=\"$( (cd /) && echo 'a \"b')\"", "# a comment in code"),
    }
    p = {}
    for name, lines in fixtures.items():
        path = tmp_path / f"{name}.sh"
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        p[name] = str(path)

    def classify(*argv):
        code = comment_class.main(list(argv))
        return code, capsys.readouterr().out

    assert {
        "md-var": classify(p["md-var"]),
        "stub-writer-dash": classify("--sweepable", p["stub-writer-dash"]),
        "quote-in-subst": classify(p["quote-in-subst"]),
        "subshell-in-subst": classify(p["subshell-in-subst"]),
    } == {
        "md-var": (0, f"{p['md-var']}:2:3\n"),
        "stub-writer-dash": (0, ""),
        "quote-in-subst": (0, f"{p['quote-in-subst']}:2:1\n"),
        "subshell-in-subst": (0, f"{p['subshell-in-subst']}:2:1\n"),
    }


@pytest.mark.tree_audit("every bash suite, script and lib under skills/tdd/scripts")
def test_main_sweeps_the_scripts_lib_and_suites_to_empty_sweepable_reports_no_cited_issue(capsys):
    comment_class = importlib.import_module("veri.comment_class")
    tests = SCRIPTS / "tests"

    def classify(*argv):
        code = comment_class.main([str(a) for a in argv])
        return code, capsys.readouterr().out

    def sweep(*names):
        return classify("--sweepable", *(SCRIPTS / n for n in names))

    def text(path, number):
        return path.read_bytes().decode("utf-8", "surrogateescape").split("\n")[number - 1]

    def by_class(cls, files):
        code, out = classify(*files)
        found = []
        for row in out.splitlines():
            name, number, got = row.rsplit(":", 2)
            if got == str(cls):
                found.append((pathlib.Path(name), int(number)))
        return code, found

    scripts = sorted(SCRIPTS.glob("*.sh"))
    libs = sorted((SCRIPTS / "lib").glob("*.sh"))
    code, comments = by_class(1, scripts + libs)
    cited = "".join(f"{p}:{n}: {text(p, n)}\n" for p, n in comments if re.search("#[0-9]", text(p, n)))

    assert {
        "the sweepable report is empty for metrics.sh, event.sh and harvest-usage.sh":
            sweep("metrics.sh", "event.sh", "harvest-usage.sh"),
        "the sweepable report is empty for supervise.sh, run-leaf.sh, detach-leaf.sh, wait-leaf.sh and run-verdict.sh":
            sweep("supervise.sh", "run-leaf.sh", "detach-leaf.sh", "wait-leaf.sh", "run-verdict.sh"),
        "the sweepable report is empty for issue-worktree.sh, verify.sh, parse-verdict.sh and extract-result.sh":
            sweep("issue-worktree.sh", "verify.sh", "parse-verdict.sh", "extract-result.sh"),
        "the sweepable report is empty for detect-test-command.sh, solvable-issues.sh and over-budget.sh":
            sweep("detect-test-command.sh", "solvable-issues.sh", "over-budget.sh"),
        "the sweepable report is empty for build-develop-prompt.sh, build-verify-prompt.sh, run-conductor.sh, stop-run.sh and preserve-attempt.sh":
            sweep("build-develop-prompt.sh", "build-verify-prompt.sh", "run-conductor.sh", "stop-run.sh",
                  "preserve-attempt.sh"),
        "the sweepable report is empty for leaf-timeout.sh, ensure-run-state-ignored.sh, orchestrate.sh, parallel-conductors.sh, workqueue.sh, push-branch.sh, refactor-triage.sh, invisible-work.sh, over-budget.sh, leaf-model.sh and leaf-launchable.sh":
            sweep("leaf-timeout.sh", "ensure-run-state-ignored.sh", "orchestrate.sh", "parallel-conductors.sh",
                  "workqueue.sh", "push-branch.sh", "refactor-triage.sh", "invisible-work.sh", "over-budget.sh",
                  "leaf-model.sh", "leaf-launchable.sh"),
        "the sweepable report is empty for every scripts/*.sh, the classifier itself included": classify("--sweepable", *scripts),
        "the sweepable report is empty for every shell file under scripts/lib/": classify("--sweepable", *libs),
        "no comment line in scripts/*.sh or scripts/lib/*.sh, the contract header included, cites an issue number": (code, cited),
    } == {
        "the sweepable report is empty for metrics.sh, event.sh and harvest-usage.sh": (0, ""),
        "the sweepable report is empty for supervise.sh, run-leaf.sh, detach-leaf.sh, wait-leaf.sh and run-verdict.sh": (0, ""),
        "the sweepable report is empty for issue-worktree.sh, verify.sh, parse-verdict.sh and extract-result.sh": (0, ""),
        "the sweepable report is empty for detect-test-command.sh, solvable-issues.sh and over-budget.sh": (0, ""),
        "the sweepable report is empty for build-develop-prompt.sh, build-verify-prompt.sh, run-conductor.sh, stop-run.sh and preserve-attempt.sh": (0, ""),
        "the sweepable report is empty for leaf-timeout.sh, ensure-run-state-ignored.sh, orchestrate.sh, parallel-conductors.sh, workqueue.sh, push-branch.sh, refactor-triage.sh, invisible-work.sh, over-budget.sh, leaf-model.sh and leaf-launchable.sh": (0, ""),
        "the sweepable report is empty for every scripts/*.sh, the classifier itself included": (0, ""),
        "the sweepable report is empty for every shell file under scripts/lib/": (0, ""),
        "no comment line in scripts/*.sh or scripts/lib/*.sh, the contract header included, cites an issue number": (0, ""),
    }


def test_main_keeps_awks_argument_handling_for_a_late_sweepable_an_empty_or_unopenable_file_stdin_and_an_assignment(tmp_path, monkeypatch, capsys):
    comment_class = importlib.import_module("veri.comment_class")
    monkeypatch.chdir(tmp_path)
    (tmp_path / "a.sh").write_text("# in a\n")
    (tmp_path / "later.sh").write_text("# in later\n")
    (tmp_path / "f=a.sh").write_text("# in an assignment-shaped name\n")

    def run(*argv, stdin=b""):
        monkeypatch.setattr(sys, "stdin", io.TextIOWrapper(io.BytesIO(stdin)))
        code = comment_class.main(list(argv))
        seen = capsys.readouterr()
        return code, seen.out, seen.err

    late_sweepable = run("a.sh", "--sweepable", "later.sh")[:2]
    empty_first = run("")
    unopenable = run("a.sh", "missing.sh", "later.sh")[:2]
    stdin = run("-", stdin=b"# from stdin\n")
    assignment = run("a.sh", "f=a.sh")

    assert (late_sweepable, empty_first, unopenable, stdin, assignment) == (
        (2, "a.sh:1:1\n"),
        (2, "", "usage: comment-class.sh [--sweepable] <file>…\n"),
        (2, "a.sh:1:1\n"),
        (0, "-:1:1\n", ""),
        (0, "a.sh:1:1\n", ""),
    )


def test_main_skips_an_empty_file_argument_after_the_first_as_awk_does(tmp_path, monkeypatch, capsys):
    comment_class = importlib.import_module("veri.comment_class")
    monkeypatch.chdir(tmp_path)
    (tmp_path / "a.sh").write_text("# in a\n")
    (tmp_path / "b.sh").write_text("# in b\n")

    code = comment_class.main(["a.sh", "", "b.sh"])
    seen = capsys.readouterr()

    assert (code, seen.out, seen.err) == (0, "a.sh:1:1\nb.sh:1:1\n", "")


def test_main_resets_md_variables_at_every_file_reads_bytes_that_are_not_utf8_and_matches_whitespace_as_ascii(tmp_path, monkeypatch, capsys):
    comment_class = importlib.import_module("veri.comment_class")
    monkeypatch.chdir(tmp_path)
    (tmp_path / "b.sh").write_text("f=/tmp/x.md\n")
    (tmp_path / "c.sh").write_text('cat > "$f" <<EOF\n# in c\nEOF\n')
    (tmp_path / "one.sh").write_text('f=/tmp/x.md\ncat > "$f" <<EOF\n# in one\nEOF\n')
    (tmp_path / "d.sh").write_bytes(b"echo \xff\xfe\n\xa0# after a non-breaking space\n# after\n")

    across = comment_class.main(["b.sh", "c.sh"])
    across_out = capsys.readouterr().out
    within = comment_class.main(["one.sh"])
    within_out = capsys.readouterr().out
    bytes_ = comment_class.main(["d.sh"])
    bytes_seen = capsys.readouterr()

    assert (across, across_out, within, within_out, bytes_, bytes_seen.out, bytes_seen.err) == (
        0, "c.sh:2:2\n", 0, "one.sh:3:3\n", 0, "d.sh:3:1\n", "",
    )


def test_cli_reports_a_comment_in_code_outside_any_heredoc_as_class_1_with_its_file_and_line(tmp_path, run_cli):
    comment_class = importlib.import_module("veri.comment_class")
    plain = tmp_path / "plain.sh"
    plain.write_text("echo one\n# a comment in code\necho two\n")

    answer = run_cli(comment_class, [str(plain)])

    assert answer == (0, f"{plain}:2:1\n", "")


def test_cli_with_no_argument_and_with_sweepable_alone_exits_2_with_empty_stdout_and_only_its_usage_line_on_stderr(run_cli):
    comment_class = importlib.import_module("veri.comment_class")

    answers = [run_cli(comment_class, argv) for argv in ([], ["--sweepable"])]

    assert answers == [(2, "", "usage: comment-class.sh [--sweepable] <file>…\n")] * 2


def header_lines(files):
    for path in files:
        lines = pathlib.Path(path).read_bytes().decode("utf-8", "surrogateescape").split("\n")
        header = bool(lines) and lines[0].startswith("#!")
        para, fresh = 0, True
        for number, line in enumerate(lines[1:], 2):
            if header and line == "#":
                fresh = True
                continue
            if not (header and line.startswith("#")):
                header = False
                continue
            if fresh:
                para += 1
            yield path, number, line, para if fresh else 0
            fresh = False


def header_citations(files):
    return "".join(f"{p}:{n}: {line}\n" for p, n, line, _ in header_lines(files) if re.search("#[0-9]", line))


def header_shapeless(files):
    return "".join(
        f"{p}:{n}: {line}\n"
        for p, n, line, para in header_lines(files)
        if para and para > 1 and not line.startswith(("# Contract under test", "# Run:", "#   "))
    )


def header_paths(*patterns, keep=lambda p: True):
    tests = SCRIPTS / "tests"
    return [p for pattern in patterns for p in sorted(tests.glob(pattern)) if keep(p)]


@pytest.mark.tree_audit("the leading header block of every top-level tests/[a-e]*.sh")
def test_cli_no_header_line_of_a_top_level_suite_from_a_through_e_cites_an_issue_number():
    assert header_citations(header_paths("[a-e]*.sh")) == ""


@pytest.mark.tree_audit("the leading header block of every top-level tests/[a-e]*.sh")
def test_cli_a_top_level_suite_header_from_a_through_e_holds_only_a_description_its_contract_block_and_its_run_line():
    assert header_shapeless(header_paths("[a-e]*.sh")) == ""


@pytest.mark.tree_audit("the leading header block of every top-level tests/[f-p]*.sh")
def test_cli_a_top_level_suite_header_from_f_through_p_carries_only_its_contract_and_cites_no_issue_number():
    files = header_paths("[f-p]*.sh")
    assert (header_citations(files), header_shapeless(files)) == ("", "")


@pytest.mark.tree_audit("the leading header block of every top-level tests/[q-z]*.sh other than skill-*")
def test_cli_a_top_level_suite_header_from_q_through_z_other_than_skill_files_carries_only_its_contract_and_cites_no_issue_number():
    files = header_paths("[q-z]*.sh", keep=lambda p: not p.name.startswith("skill-"))
    assert (header_citations(files), header_shapeless(files)) == ("", "")


@pytest.mark.tree_audit("the leading header block of every tests/skill-[m-z]*.test.sh")
def test_cli_a_skill_suite_header_from_m_through_z_carries_only_its_contract_and_cites_no_issue_number():
    files = header_paths("skill-[m-z]*.sh")
    assert (header_citations(files), header_shapeless(files)) == ("", "")
