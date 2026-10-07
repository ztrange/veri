"""In-process cases for veri/comment_class.py, the module comment-class.sh is a shim over."""
import importlib
import io
import pathlib
import re
import sys

SCRIPTS = pathlib.Path(__file__).resolve().parents[2]
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


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


CLASS_3_LINES = """\
build-develop-prompt:## Bug
build-develop-prompt:### What happened
build-develop-prompt:### Expected
build-develop-prompt:### Steps to reproduce
build-develop-prompt:### Environment
build-verify-prompt:# Plan for #426
build-verify-prompt:# Plan for #439
build-verify-prompt:## Bug
build-verify-prompt:### What happened
build-verify-prompt:### Expected
build-verify-prompt:### Steps to reproduce
build-verify-prompt:### Environment
capture-spec:## What happened
capture-spec:## Expected
capture-spec:## Steps to reproduce
capture-spec:## Environment
capture-spec:## Acceptance criteria
capture-spec:## What to build
capture-spec:## Acceptance criteria
dashboard:# Plan for #$2 — $3
dashboard:## What to build
dashboard:# Plan for #51 — lamps hum
dashboard:# Plan for #77 — a kettle boils
invisible-work:#!/bin/sh
no-awk-v-patterns:#!/usr/bin/env bash
no-awk-v-patterns:#!/usr/bin/env bash
no-awk-v-patterns:#!/usr/bin/env bash
no-awk-v-patterns:#!/usr/bin/env bash
no-awk-v-patterns:#!/usr/bin/env bash
no-awk-v-patterns:#!/usr/bin/env bash
no-awk-v-patterns:#!/usr/bin/env bash
no-awk-v-patterns:# an unrelated line inserted above the exempt site
no-awk-v-patterns:# and another
orchestrate:# A stopped conductor must be stopped by a signal, not by its writes failing, so this stub
orchestrate:# IGNORES SIGPIPE — the state CI's Linux was observed in, where a write to the closed stream
orchestrate:# came back as plain \\`echo: I/O error\\` and the conductor ran on. On this Mac SIGPIPE is fatal
orchestrate:# and would end the stub whatever orchestrate.sh did, so without this line the cases below
orchestrate:# cannot go red here at all, and the regression they exist for is only visible on CI. This is
orchestrate:# a stub imitating a platform, not a suite repairing its own pipeline (#422).
parallel-conductors:#!/bin/sh
refactor-owed:### step 2
refactor-owed:### step 2
run-verdict:#!/bin/sh
run-verdict:# Stub verifier: record the argv handed to it, one argument per line, and answer like a
run-verdict:# verifier that passed — what this case reads is the record, not the verdict.
run-verdict:#!/bin/sh
run-verdict:# Stub verifier: copy the phase's reason file, as it stands now, into the record this case
run-verdict:# reads — an unreadable or absent file records as nothing, which is the same answer as a
run-verdict:# cleared one and the answer this case wants.
skill-refactor-pending:## The scripts (this skill's `scripts/` directory)
skill-refactor-pending:## The scripts (this skill's `scripts/` directory)
solvable-issues:#!/bin/sh
status:# Plan for #7 — widgets spin when clicked
unit/emitted-text:## What to build
unit/emitted-text:## Acceptance criteria
unit/emitted-text:## Bug
unit/emitted-text:## Acceptance criteria
unit/emitted-text:## Refactor
unit/emitted-text:# Plan for #1 — fixed
"""


def test_main_sweeps_the_scripts_lib_and_suites_to_empty_sweepable_reports_no_cited_issue_and_unchanged_class_3_lines(capsys):
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
    suites = (
        sorted(tests.glob("*.sh"))
        + sorted((tests / "unit").glob("*.sh"))
        + sorted(tests.glob("fixtures/*/*.sh"))
        + [tests / "unit-guard" / "git", tests / "offline" / "gh"]
    )
    code_3, found_3 = by_class(3, suites)
    class_3 = "".join(
        f"{str(p.relative_to(tests)).removesuffix('.test.sh')}:{text(p, n)}\n" for p, n in found_3
    )

    assert {
        "the sweepable report is empty for metrics.sh, event.sh and harvest-usage.sh":
            sweep("metrics.sh", "event.sh", "harvest-usage.sh"),
        "the sweepable report is empty for supervise.sh, run-leaf.sh, detach-leaf.sh, wait-leaf.sh and run-verdict.sh":
            sweep("supervise.sh", "run-leaf.sh", "detach-leaf.sh", "wait-leaf.sh", "run-verdict.sh"),
        "the sweepable report is empty for issue-worktree.sh, verify.sh, parse-verdict.sh and extract-result.sh":
            sweep("issue-worktree.sh", "verify.sh", "parse-verdict.sh", "extract-result.sh"),
        "the sweepable report is empty for detect-test-command.sh, solvable-issues.sh and session-cost.sh":
            sweep("detect-test-command.sh", "solvable-issues.sh", "session-cost.sh"),
        "the sweepable report is empty for build-develop-prompt.sh, build-verify-prompt.sh, run-conductor.sh, stop-run.sh and preserve-attempt.sh":
            sweep("build-develop-prompt.sh", "build-verify-prompt.sh", "run-conductor.sh", "stop-run.sh",
                  "preserve-attempt.sh"),
        "the sweepable report is empty for leaf-timeout.sh, ensure-run-state-ignored.sh, orchestrate.sh, parallel-conductors.sh, workqueue.sh, push-branch.sh, refactor-triage.sh, invisible-work.sh, over-budget.sh, run-suite.sh, leaf-model.sh and leaf-launchable.sh":
            sweep("leaf-timeout.sh", "ensure-run-state-ignored.sh", "orchestrate.sh", "parallel-conductors.sh",
                  "workqueue.sh", "push-branch.sh", "refactor-triage.sh", "invisible-work.sh", "over-budget.sh",
                  "run-suite.sh", "leaf-model.sh", "leaf-launchable.sh"),
        "the sweepable report is empty for every scripts/*.sh, the classifier itself included": classify("--sweepable", *scripts),
        "the sweepable report is empty for every shell file under scripts/lib/": classify("--sweepable", *libs),
        "no comment line in scripts/*.sh or scripts/lib/*.sh, the contract header included, cites an issue number": (code, cited),
        "the text of every class 3 line in the suites is unchanged, in its file and in its order": (code_3, class_3),
    } == {
        "the sweepable report is empty for metrics.sh, event.sh and harvest-usage.sh": (0, ""),
        "the sweepable report is empty for supervise.sh, run-leaf.sh, detach-leaf.sh, wait-leaf.sh and run-verdict.sh": (0, ""),
        "the sweepable report is empty for issue-worktree.sh, verify.sh, parse-verdict.sh and extract-result.sh": (0, ""),
        "the sweepable report is empty for detect-test-command.sh, solvable-issues.sh and session-cost.sh": (0, ""),
        "the sweepable report is empty for build-develop-prompt.sh, build-verify-prompt.sh, run-conductor.sh, stop-run.sh and preserve-attempt.sh": (0, ""),
        "the sweepable report is empty for leaf-timeout.sh, ensure-run-state-ignored.sh, orchestrate.sh, parallel-conductors.sh, workqueue.sh, push-branch.sh, refactor-triage.sh, invisible-work.sh, over-budget.sh, run-suite.sh, leaf-model.sh and leaf-launchable.sh": (0, ""),
        "the sweepable report is empty for every scripts/*.sh, the classifier itself included": (0, ""),
        "the sweepable report is empty for every shell file under scripts/lib/": (0, ""),
        "no comment line in scripts/*.sh or scripts/lib/*.sh, the contract header included, cites an issue number": (0, ""),
        "the text of every class 3 line in the suites is unchanged, in its file and in its order": (0, CLASS_3_LINES),
    }


def test_main_sweeps_the_top_level_suites_and_the_skill_suites_to_empty_sweepable_reports(capsys):
    comment_class = importlib.import_module("veri.comment_class")
    tests = SCRIPTS / "tests"

    def sweep(*patterns, keep=lambda p: True):
        files = [p for pattern in patterns for p in sorted(tests.glob(pattern)) if keep(p)]
        code = comment_class.main(["--sweepable", *(str(p) for p in files)])
        return code, capsys.readouterr().out

    assert {
        "the sweepable report is empty for every top-level tests/*.sh whose name starts with a or b":
            sweep("[ab]*.sh"),
        "the sweepable report is empty for every top-level tests/*.sh whose name starts with c or d":
            sweep("[cd]*.sh"),
        "the sweepable report is empty for every top-level tests/*.sh whose name starts with e through j":
            sweep("[e-j]*.sh"),
        "the sweepable report is empty for every top-level tests/*.sh whose name starts with k through m":
            sweep("[k-m]*.sh"),
        "the sweepable report is empty for every top-level tests/*.sh whose name starts with n through r":
            sweep("[n-r]*.sh"),
        "the sweepable report is empty for the supervisor's two suites, tests/supervise*.test.sh":
            sweep("supervise*.test.sh"),
        "the sweepable report is empty for every top-level tests/*.sh whose name starts with s, other than the skill-* and supervise* files":
            sweep("s*.sh", keep=lambda p: not p.name.startswith(("skill-", "supervise"))),
        "the sweepable report is empty for every top-level tests/*.sh whose name starts with t through z":
            sweep("[t-z]*.sh"),
        "the sweepable report is empty for every tests/skill-*.test.sh whose name after skill- starts with a through l":
            sweep("skill-[a-l]*.test.sh"),
        "the sweepable report is empty for every tests/skill-*.test.sh whose name after skill- starts with m through z":
            sweep("skill-[m-z]*.test.sh"),
    } == {
        "the sweepable report is empty for every top-level tests/*.sh whose name starts with a or b": (0, ""),
        "the sweepable report is empty for every top-level tests/*.sh whose name starts with c or d": (0, ""),
        "the sweepable report is empty for every top-level tests/*.sh whose name starts with e through j": (0, ""),
        "the sweepable report is empty for every top-level tests/*.sh whose name starts with k through m": (0, ""),
        "the sweepable report is empty for every top-level tests/*.sh whose name starts with n through r": (0, ""),
        "the sweepable report is empty for the supervisor's two suites, tests/supervise*.test.sh": (0, ""),
        "the sweepable report is empty for every top-level tests/*.sh whose name starts with s, other than the skill-* and supervise* files": (0, ""),
        "the sweepable report is empty for every top-level tests/*.sh whose name starts with t through z": (0, ""),
        "the sweepable report is empty for every tests/skill-*.test.sh whose name after skill- starts with a through l": (0, ""),
        "the sweepable report is empty for every tests/skill-*.test.sh whose name after skill- starts with m through z": (0, ""),
    }


def test_main_sweeps_the_unit_fixture_guard_and_offline_suites_to_empty_sweepable_reports(capsys):
    comment_class = importlib.import_module("veri.comment_class")
    tests = SCRIPTS / "tests"

    def sweep(*patterns, keep=lambda p: True):
        files = [p for pattern in patterns for p in sorted(tests.glob(pattern)) if keep(p)]
        code = comment_class.main(["--sweepable", *(str(p) for p in files)])
        return code, capsys.readouterr().out

    names = ["ledger", "red-divergence", "run-affordable", "step-budget", "step-cost", "stop-requested"]

    assert {
        "the sweepable report is empty for every tests/unit/*.sh whose name starts with c through e, other than comment-class.test.sh":
            sweep("unit/[c-e]*.sh", keep=lambda p: p.name != "comment-class.test.sh"),
        **{
            f"the sweepable report is empty for tests/unit/{name}.test.sh": sweep(f"unit/{name}.test.sh")
            for name in names
        },
        "the sweepable report is empty for every tests/unit/*.sh whose name starts with m through p":
            sweep("unit/[m-p]*.sh"),
        "the sweepable report is empty for every shell file under tests/fixtures/, and for tests/unit-guard/git and tests/offline/gh":
            sweep("fixtures/*/*.sh", "unit-guard/git", "offline/gh"),
        "the sweepable report is empty for tests/unit/comment-class.test.sh, the case labels of its own sweepable-report cases included":
            sweep("unit/comment-class.test.sh"),
    } == {
        "the sweepable report is empty for every tests/unit/*.sh whose name starts with c through e, other than comment-class.test.sh": (0, ""),
        **{f"the sweepable report is empty for tests/unit/{name}.test.sh": (0, "") for name in names},
        "the sweepable report is empty for every tests/unit/*.sh whose name starts with m through p": (0, ""),
        "the sweepable report is empty for every shell file under tests/fixtures/, and for tests/unit-guard/git and tests/offline/gh": (0, ""),
        "the sweepable report is empty for tests/unit/comment-class.test.sh, the case labels of its own sweepable-report cases included": (0, ""),
    }


def test_main_sweeps_cover_outcome_test_sh_and_its_1089_nul_cases_to_an_empty_sweepable_report(capsys):
    comment_class = importlib.import_module("veri.comment_class")
    suite = SCRIPTS / "tests" / "unit" / "cover-outcome.test.sh"
    code = comment_class.main(["--sweepable", str(suite)])
    assert (code, capsys.readouterr().out) == (0, "")


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
