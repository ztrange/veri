# veri/ — interface index

The Python half of veri's scripts: each `<name>.sh` in `skills/tdd/scripts/` is a `/bin/sh` shim that execs
`veri/<name>.py`. Modules import their siblings flat (`import git`, `from ledger import ledger_path`) because they
run as scripts, and never relatively or as `veri.x`, with no `try/except ImportError` fallback: tests name a module `veri.x`
but get the same object as flat `x` (the finder in `tests/py/conftest.py`). `tests/py/unit/test_flat_sibling_imports.py`
(a tree audit) fails otherwise. The pytest leg and its plugins are test plumbing and live outside `veri/`, in
`skills/tdd/scripts/tests/leg/` (#4051).
`entry.run(main, argv)` is the one `__main__` path: it turns an uncaught exception into exit 2. Exit codes 0/1/2/3 are
the API; they are defined in the root `CLAUDE.md`.

This file indexes `veri/` by **group**, then by module. Within a group, the entry modules (each with a
`<name>.sh` shim) and the modules nothing shares are listed in one line each; the **shared modules** (imported by
two or more other modules here) also have a `## <module>` section naming what other modules use. A test
(`tests/py/unit/test_veri_interface_index.py`, a tree audit: `make test` runs it, `make unit` does not) fails when a
module is in no group or in two, when a listed name does not exist, when a shared module lacks a section or a section
sits outside its module's group, when a group imports against the directions below, when a module reads a sibling's
underscore name, or when a module has no docstring. Related names share a line where the list would otherwise pass
about twelve lines.

# Groups

- **Foundations**: What every module stands on: the one `__main__` path and exit contract, script paths, the `VERI_*` tunables, git, starting a process detached, the bash and Python floors, the session environment, JSON/Markdown reading, the reading of a leaf report's `KEY:` lines and the reading of test and requirements sources, and the redaction of secrets from text veri hands GitHub.
- **Run state and journal**: Where a run lives on disk, its journal of events and its pin files and mutation record, whether it is live, stuck or ended, and how it is stopped.
- **Ledger and plan**: The ledger of a run: reading its steps and finding the next one to do, growing, dropping and reordering them, the replaces-case steps, and checks of the plan itself. Ticking a step is in Frozen tests and case history (`tick_ledger` imports `tests_frozen`, which this group may not).
- **Leaf launch and supervision**: How a leaf is launched through the supervisor, detached, waited for and timed, and how its stream log is read.
- **Prompts and leaf reports**: What a leaf is told (the prompt builders) and what it answers (the `KEY: value` report and the readers of each leaf's report).
- **Verdicts and verification**: The verifier and adjudicator legs: run the blind verifier, parse its verdict, compare rejects, adjudicate an exit 2.
- **Budgets and cost**: The budgets (steps, time, refactor, context, affordability) and what leaves cost.
- **Veri's own test runner**: How veri's own suite runs (`make test`, `make unit`, `make profile`): what the pytest leg shares with the launches, the bytecode cache, the one-full-run lock, the fast-tier admission guard and the per-case profiler.
- **Target suites and tiers**: Choosing and running the suites of the project veri works on: finding its test commands, the suites a change affects, timed, baseline, branch and rebased-tip runs, flakes, reruns and mutation probes.
- **Frozen tests and case history**: The tests-frozen rule: recording and checking that a step's tests are not changed afterwards, ticking a ledger step (which re-records the earlier steps' cases), routing a rejected pin or wrong test, and the git history of cases.
- **GitHub and issues**: gh access, issue selection (solvable, parked, blocked), claiming and releasing issues, specs captured from issues and ticking an issue's criteria.
- **Branch, PR and merge**: Worktrees, pushing a branch, readying and merging the pull request, waiting for CI.
- **Prose grading and requirements**: Graded prose: the Requirements rows of a unit, grading them with a leaf, the prose still owed grading and the skill-edit step.
- **Conductors and operator tools**: The conductor loop, parallel conductors, lanes and the operator's views (status, metrics, reports).

Directions the tree obeys (checked by the same test; every group states what it may import except Conductors and operator tools, which may import any group and which nothing imports):

- Foundations imports only: nothing
- Run state and journal imports only: Foundations
- Ledger and plan imports only: Foundations; Run state and journal
- Leaf launch and supervision imports only: Foundations; Run state and journal; Ledger and plan; Target suites and tiers; Veri's own test runner; Frozen tests and case history
- Prompts and leaf reports imports only: Foundations; Run state and journal; Ledger and plan; Leaf launch and supervision; Target suites and tiers
- Verdicts and verification imports only: Foundations; Run state and journal; Ledger and plan; Leaf launch and supervision; Prompts and leaf reports; Target suites and tiers
- Veri's own test runner imports only: Foundations; Run state and journal
- Target suites and tiers imports only: Foundations; Run state and journal; Veri's own test runner
- Budgets and cost imports only: Foundations; Run state and journal
- Frozen tests and case history imports only: Foundations; Run state and journal; Ledger and plan
- GitHub and issues imports only: Foundations; Run state and journal; Ledger and plan; Target suites and tiers
- Branch, PR and merge imports only: Foundations; Run state and journal; Ledger and plan; Target suites and tiers; GitHub and issues
- Prose grading and requirements imports only: Foundations; Run state and journal; Ledger and plan; Leaf launch and supervision; GitHub and issues
- Nothing imports Conductors and operator tools

### Refusing

A refusal is exit 2 with its words on stderr. `entry.refuse(*lines, usage=None, prefix="")` is the shared way to write one and the call for a new script: about 100 calls in 23 modules (counted 2026-11-15). It is not the only way, and no audit checks the choice: about 98 sites in 80 modules write their `USAGE` to stderr themselves (`print(USAGE, file=sys.stderr)`, `entry.write(sys.stderr, USAGE)`), and a script whose refusal bytes a test pins keeps its own spelling, since `refuse` writes through the binary buffer and flushes around each line where `print` does not. A script that takes no arguments calls `entry.no_arguments(argv, USAGE)` first; `tests/py/unit/test_zero_argument_modules_refuse_an_argument.py` fails for a module whose `USAGE` shows no argument and whose `main` neither calls it nor tests `argv` itself.

### Adding a script

An ungraded checklist; each step names the audit that fails when it is skipped (run it with `make test TESTS=…`).

1. `veri/<name>.py`: a module docstring, `USAGE`, `main(argv)`, and `entry.run(main, argv)` as the one `__main__` path; sibling imports flat. A script that takes no argument calls `entry.no_arguments(argv, USAGE)` (see "Refusing"). Audits: `tests/py/unit/test_veri_interface_index.py` (docstring), `tests/py/unit/test_flat_sibling_imports.py`, `tests/py/unit/test_shims.py` (`entry_bypass_problems`: `__main__` goes through `entry.run`), `tests/py/unit/test_zero_argument_modules_refuse_an_argument.py`; and `tests/py/unit/test_entry_start_cost.py` when the module is `entry` (no costly stdlib import at its top).
2. `<name>.sh`: the canonical `/bin/sh` shim over that module, no Python in it, executable. Audit: `tests/py/unit/test_shims.py` (`shim_problems`, and the executable bit).
3. The shim's `# Usage:` header agrees with `USAGE`, and its flags are in the SCRIPTS.md synopsis. Audits: `tests/py/unit/test_shim_usage_matches_module.py`, `tests/py/unit/test_skill_reference_usage.py`.
4. `--help` prints `USAGE` and exits 0 (`entry.run` does it). Audits: `tests/py/unit/test_every_shim_module_answers_help.py` (every shim-fronted module declares `USAGE`; `--help` exits 0, prints usage, starts no process), `tests/py/unit/test_help_flag.py`, `tests/py/unit/test_operator_scripts_help_guard.py`.
5. The catalogue: a bullet for `$S/<name>.sh` in `skills/tdd/SCRIPTS.md` and its SC row in `skills/tdd/REQUIREMENTS.md` (both graded prose). Audit: `tests/py/unit/test_scripts_md_rows.py` (a script left out is named in its `UNCATALOGUED` ratchet).
6. This file: the script's line in its group, a `## <module>` section once two other modules import it (every name a sibling uses listed there, and every listed call with the parameters the module defines), and the group's direction still obeyed. Audits: `tests/py/unit/test_veri_interface_index.py`, `tests/py/unit/test_index_names_match_use.py`.
7. A `VERI_*` read goes through `tunables.get(name)` with no literal default, and the name's one default sits in `tunables.TUNABLES`. Audits: `tests/py/unit/test_tunable_defaults_audit.py` (every `VERI_*` name, in the table or not), `tests/py/unit/test_tunable_reads.py`.
8. Tests in `tests/py/unit/test_<name>.py`: no process, no repo listing; a case that starts a process carries `@pytest.mark.process("<boundary>")`, one that lists a repo directory `@pytest.mark.tree_audit("<sweep>")`. A tree audit reads the sources through the shared `tests_py_index` and `veri_modules_index` fixtures. Audits: `tests/py/test_fast_tier_guard.py` (placement), `tests/py/unit/test_process_mark.py` with conftest's collection check (marks), `tests/py/unit/test_tree_index_guard.py` (the fixtures).
9. The test side's map: which tier and marks, which helper module or fixture fakes a process, a repository, the dispatch world or GitHub, and which audits check a test file. See `tests/py/README.md`; its index audit is `tests/py/unit/test_tests_py_readme.py`.

#### Stated, not audited

Rules this file states that no audit enforces; they rely on review.

- Siblings are imported with no `try/except ImportError` fallback: `test_flat_sibling_imports.py` checks the import forms only (no site on 2026-11-15).
- `entry.refuse` is the call for a new refusal (see "Refusing"); no audit counts which form a script uses.
- Exit codes 1 and 2 are never collapsed: a clean negative is not a plan that failed to produce an answer.
- A module's one-line description, a section's prose and a group's description say what the code does. The audits check names, parameter lists and group membership, not sentences.
- A group's description names the concerns its modules hold; moving a module between groups needs its imports to obey the directions above, which the audit does check.

# Foundations

What every module stands on: the one `__main__` path and exit contract, script paths, the `VERI_*` tunables, git, starting a process detached, the bash and Python floors, the session environment, JSON/Markdown reading, the reading of a leaf report's `KEY:` lines and the reading of test and requirements sources. Builds on no other group; every other group may build on it.

- `fused`: what a fused script shares: an inner call from this skill's scripts directory, printed with its exit code, a `Stop` at the first call that is not clean, its `stopped at` line, and the settled `key=value` file.
- `report.sh`: read `KEY: value` lines off a leaf report.
- `requirements.sh`: the prose units and requirement rows of a file.
- `stack-branch.sh`: the stack branch a repository's `CLAUDE.md` names (`veri: stack branch: <name>`), refused when it cannot be one.

## case_reader
- `is_test_file(name)`, `is_test_path(path)`, `is_go_test_file(name)`, `is_js_test_file(name, root="")`: whether a name or path is a Python, Go or JavaScript test file (bool). `JS_EXT`: the regex source matching a JavaScript or TypeScript file's extension.
- `cut_cases(text)`: `[(case name, source)]` of a test source, a JS case cut at its call's closing paren past its strings, comments and regex literals (a `/` after a name other than `return`, a number, `)` or `]`, or with no closing `/` on its line, divides); raises `UnclosedCase` when a JS call never closes.
- `old_cut_cases_all(text, call_form_only=False)`: the earlier cutter, kept for comparing old and new records.
- `defined_name(case, text, py_file, go_file)`: the def a case name resolves to, `None` if none. `defines_helper(name, text, py_file, go_file)`: bool.
- `live_titles(case, text)`: the titles in `text` that match a JS case, ignoring comments. `js_title_pattern(case)`: that compiled pattern.
- `cut_prefix(case)`: the case with its trailing `…`/`...` cut, `None` when it has none. `strip_param_suffix(name)`: the name without `[param]`.
- `file_defines(path, case, classes=(), any_title=False)`: whether the test file at `path` defines `case` (a Python or Go def, a live JS title, a `.test.sh` `name=`); with `classes`, only a Python file whose class chain defines it; with `any_title`, any live JS title `case`'s pattern matches, so a name cut at `…` resolves to the longer title (bool).

## detach
- `start(argv, stdin, stdout, stderr, xfsz=SIG_IGN)`: starts `argv` as leader of a new session and returns its pid without waiting.

## entry
- `exit_code(main, argv, on_broken_pipe=silence_stdout)`: the code `run` exits with, returned instead (pytest_leg's `launch` records the bytecode cache after it).
- `run(main, argv)`: `sys.exit(exit_code(main, argv))`; `--help` prints the module's `USAGE`, an uncaught exception prints one line and exits 2, a broken pipe exits quietly.
- `write(stream, text, *, before=True, after=True, end="\n")`: writes str or bytes to the stream's binary buffer, flushing before and after by default.
- `refusal(main, exc)`: the one-line `<shim>: <Type>: <reason> (at file:line)` text for an exception.
- `silence_stdout()`: points fd 1 at `/dev/null`; ignores failure.
- `refuse(*lines, usage=None, prefix="")`: writes each str/bytes line (prefixed) and then the usage to stderr; returns 2. The shared way to refuse, not the only one (see "Refusing" below).
- `no_arguments(argv, usage)`: for a script that takes none, `None` when `argv` is empty, else refuses (2) naming the first argument, then the usage.
- `to_contract(code)`: the code when it is 0, 1, 2 or 3, else 2.
- `whole_number(text, minimum=1)`: the int of `text` when it is ASCII digits only (leading zeros allowed; no sign, space or non-ASCII digit) and at least `minimum`, else `None`.

## fused
What a fused script after preflight shares (PRD 027 FC1-FC4, FC10, FC14).
- `script(name)`: `name` in this skill's own scripts directory.
- `run_script(name, *args, cwd=None, env=None, stdin=None, out=None, err=None, run=subprocess.run)`: one process's `(code, stdout, stderr)`, printing nothing; `call` prints around it.
- `label(name, *args)`: the call as one line, a newline inside an argument written `\n`.
- `call(name, *args, **kw)`: one process (`stdin`, `out` and `err` redirections, a `run` such as `github.bounded`), printing a line naming the call and its exit code, then its stdout, and passing its stderr through. `checked(where, name, *args, ok=(0,), **kw)`: `call`, raising `Stop` on an exit outside `ok`; its stdout otherwise. `shown(name, *args, out=None, err=None, stdin=None, **_)`: the line naming a call, with its redirections. `run_script(name, *args, cwd=None, env=None, stdin=None, out=None, err=None, run=subprocess.run)`: `(code, stdout, stderr)` of one process, printing nothing.
- `quiet()`: a context within which `call` prints only the line naming each call, never its stdout (`revise.sh`, PRD 038.9 RVS14).
- `Stop(where, what, code)`: the first outcome that is not clean. `stopped(stop)`: prints its `stopped at <where> <what>` line; the exit code, the inner code when neither 0 nor 3, else 1.
- `conductor(wt)`: `{"pid", "started"}` as `<wt>/.tdd/conductor.pid` names them, `None` without one: the conductor a wait record is written for (FC7).
- `settle(wt, n, name, lines)`: writes `.tdd/issue-<n>-<name>` and prints its lines; 0. `read_settled(path)`: its `{key: value}`; OSError when unreadable. `read_lines(lines)`: the `{key: value}` of a settled file's lines. `settled_file(wt, n, name)`: that file's path.
- The fused halves of a step (PRD 027.4-027.6): `entry(argv, name, run)`, their main (usage and 2, the `stopped at` line on a `Stop`, `waiting on <name>` and 3 on a `Waiting(name)`, a wait whose slice ran out); `step_env(n, step, **more)` and `mark(where, wt, n, step, *fields, **more)`, the run context and a conductor mark.
- `launch(where, wt, name, command, *args, env, out, err, clear=())`: a leaf under *Launching a leaf* (FC8). `wait(wt, n, owner, name, rejected_step=None)`: `wait-leaf.sh`, raising on 3, else the leaf's code with the wait record removed, or, with `rejected_step`, moved to owner `<owner>-rejected` naming that step on a `verdict-<phase>` exit 1, for `revise.sh` to hand back (PRD 038.9). `save_wait`/`load_wait(wt, n, owner, …)`: the wait record `.tdd/issue-<n>-<owner>-wait` (`wait_record(wt, n, owner)` its path), discarded under another conductor (FC5-FC7).
- `report(where, wt, path, *keys, every=False)`: a leaf's report lines through `extract-result.sh`, printing none of it (FC2). `changed_paths(where, wt)`: each changed or untracked file, one by one (`git status --porcelain --untracked-files=all`), a rename by its new path.

## git
- `git(*args, **kwargs)`: `subprocess.run(["git", *args], **kwargs)`; the CompletedProcess, never raises on a non-zero exit.
- `symref_default(answer)`: the default branch named in `ls-remote --symref` output, `None` when absent.
- `out(*args, cwd=None)`: stdout as str, trailing newlines stripped; raises `GitFailed` on a non-zero exit or a missing git.
- `ok(*args, cwd=None)`: whether the command exited 0; never raises.
- `default_branch(cwd=None, remote=True)`: the default branch name, `None` when it cannot be told; `remote=False` never touches the network. A fallback is the caller's to write.
- `network(*args, cwd=None, limit_name="VERI_GIT_NETWORK_TIMEOUT")`: a git call that talks to a remote, text captured, in a session of its own; at the limit its whole process group is killed and it answers a `TimedOut` (a CompletedProcess, exit 124, stderr naming the call and the limit). A bad limit or a git that cannot start answers exit 2. Never raises. `github.bounded_group` is the same bound for a caller that may import `github`; this one is for the Foundations and Run state modules that may not.

## json_documents
- `documents(text, strict=True)`: the JSON documents in `text`, in order; raises `json.JSONDecodeError` on a malformed one.
- `items(text, strict=True)`: the elements of every document, as one list.

## js_tests
- `CALL`: regular-expression source that matches the opening of a JS `it(`/`test(` call.

## launch_floor
- `bash_refusal(prefix)`: 0 when bash is 5+, else writes the refusal to stderr and returns its exit code.
- `python_refusal(prefix)`: the same for the Python floor. `python_floor()`: the floor as `major.minor` read from `lib/venv-python.sh`.

## markdown_sections
- `fenced_lines(text)`: a list of bools, True for each line inside a code fence (fence lines included).
- `unfenced(text)`: `[(index, line)]` for each line outside a code fence; the question-file readers (`record_answer`, `status`) find their headings with it.

## paths
- `SCRIPTS`: the scripts directory of the veri modules, defined once here.
- `scripts_of(file)`: the `scripts/` directory above a file of `veri/`, `..` resolved after following symlinks.
- `resolved_scripts_of(file)`: the same with the file's symlinks resolved first.
- `inside_scripts(file, where=None)`: whether `where` (default: the current directory) is that scripts directory or inside it.

## popen_command
- `command_words(args)`: the argv list a `Popen` `args` names. `command_basename(args)`: the first word's basename, `""` for none.

## redaction
- `listed_names()`: the names `VERI_REDACT_VARS` lists, its default when it names none; `run-leaf.sh` warns, naming each, when `VERI_LEAF_ENV` passes one to a leaf.
- `redact(text)`: `text` with `[redacted]` for every match of `gh[pousr]_[A-Za-z0-9]{36,}`, `github_pat_[A-Za-z0-9_]{22,}`, `sk-ant-[A-Za-z0-9_-]{20,}` and `AKIA[0-9A-Z]{16}`, and every occurrence of the value (8 characters or more) of a variable `VERI_REDACT_VARS` names, as is and as a JSON string escapes it (default `GH_TOKEN GITHUB_TOKEN ANTHROPIC_API_KEY CLAUDE_CODE_OAUTH_TOKEN`; set but empty or blank, the default too: value redaction cannot be turned off). Every shape and value is matched on the text joined across its split points: a line break or its JSON escape (`\n`, `\r`), with the blanks and one backslash before it and the next line's indent and markdown prefixes (`> `, `- `, `* `, `+ `, `# `, nested) and a gh CI log's `<job>\t<step>\t<ISO timestamp>Z ` or a bare ISO timestamp, or a zero-width character (U+200B, U+200C, U+200D, U+FEFF, U+00AD); the text from a match's first character to its last is replaced, the split points inside it included, so a secret split anywhere is replaced whole. A token that ends a line takes nothing of the next line with it when it has its documented length (`gh[pousr]_` 36, `github_pat_` 82, `AKIA` 16 characters after the prefix, a listed value exactly), while an `sk-ant-` key, whose length varies, may take up to 101 minus its own length of the next line's first characters. A token glued to the next is two; a base64 or base64url run that decodes to one is replaced whole, and adjacent ones read as one `[redacted]`. One pass over the text: a 1 MB body takes well under a second. Text with nothing to redact comes back unchanged. `bounded` passes every argument of a `gh` command line, and the `input` it hands `gh` on stdin (str or bytes), through it, and a file the command line hands `gh` (`--input <file>`, `--body-file <file>`, their `=` forms, `-F`/`--field <field>=@<file>` and the glued `-F<field>=@<file>`, `--field=<field>=@<file>`) whose contents hold something to redact is handed as a redacted copy in a private directory (`mkdtemp`, mode 0700) removed after the call, the file itself unchanged. `run_records` passes every string it carries through it too. So every comment, issue title and body, and PR body veri hands `gh` is redacted; `test_github_redaction.py`'s ratchet fails on a `gh` command line named anywhere else.

## renamed_case
- `renamed_to(name, old_source, new_source, taken)`: the case of `new_source` with the same text as `name` but another name, else `None`.
- `renamed_and_changed_to(name, old_source, new_source, taken)`: the case with the same def line but another name and a changed body.

## report
- `report_read(text, keys, *, optional_space=False, terminated_only=False)`: `{key: value}` for the `KEY: value` lines of a leaf report.
- `report_values(text, key, *, occurrence="every", space="required", bullet=False, splitlines=False, strip=False)`: the values of `text`'s `key:` lines (str or bytes), each reader's own rule as options: `occurrence` `first`, `last` (value or None) or `every` (list); `space` `required`, `optional` or `kept` (a bare prefix, nothing removed); `bullet` lets a `- ` or `* ` precede the key; `splitlines` splits as `str.splitlines` rather than on `\n`; `strip` strips each line first.

## requirements
- `lists(path="REQUIREMENTS.md")`: the REQUIREMENTS.md files that exist. `tracked(name)`: git-tracked files of that name; RuntimeError when `git ls-files` fails.
- `listed_units(path)`, `claims(path, unit)`: the units a list names; a unit's rows as `<id>\t<requirement>` lines (ValueError `path:line: reason` on a malformed table).
- `read_lines(path)`, `requirements_lines(lines)`: a file's lines; `(heading, line)` pairs of its `## Requirements` section.
- `parsed_once()`: a context manager inside which each list is read and fence-parsed once (`headings` and `claims` share it); the memo ends with the block. Not reentrant.
- `split_cells(line)`, `table_cells(line)`: a table row's cells. `well_formed_row_id(row_id)`: bool. `malformed_row_id(lines)`: the first bad id, `None` when fine.
- `list_path(unit)`: the `REQUIREMENTS.md` beside a unit.

## session_env
- `strip_session_env(env)`: removes the Claude Code session variables, and values carrying a session id, from `env`.

## stack_branch
- `named(root, remote=True)`: the stack branch `<root>/CLAUDE.md` names, `None` when it names none; raises `Refused` (stack-branch.sh's exit 2, its text naming the line) for an empty name, the default branch, or a name `git check-ref-format --branch` refuses. With `remote=False` the default branch is read from `refs/remotes/origin/HEAD` alone, asking origin nothing (`queued_merge`'s offline join).
- `run_base(root=None, remote=True)`: `(branch, stacked)`, the one answer to which branch a run is cut from, rebased onto and diffed against: the stack only when the run's cut recorded it in `<root>/.tdd/issue-<n>-base` (written by `issue-worktree.sh`) and it is still the named stack, else `git.default_branch(root, remote)` exactly as without a stack; raises `Refused` for a garbled or outdated record, naming both.
- `ahead(root=".")`: `(stack, default, commits)`, the named stack, the default branch and `origin/<default>..origin/<stack>` as `[(sha, subject)]` oldest first, read after a fetch of origin; `commits` empty when origin has no stack; `None` when no stack is named; `Refused` (exit 2 to its callers) for a name that cannot be a stack, a fetch with no answer, a default branch told two ways or not on origin, or a failed log. `stack-pr.sh`'s and `stack-green.sh`'s range.
- `recorded_base(root)`: `(path, text)` of the one `<root>/.tdd/issue-<n>-base` a stacked cut recorded, `None` when there is none; `Refused` when there are several.

## tunables
The one reader of `VERI_*` and related environment variables.
- `read(name, default="", unless_empty=None)`: the value as a string. `read_bytes(name, default=b"")`: as bytes.
- `TUNABLES`: name to `Tunable(parse, default, refusal=None)`, every tunable once. `TABLE`: the entries that state a `refusal`. `tokens(raw)`: int, ValueError otherwise.
- Two verbs over the one table. `get(name, unless_empty=False)`: the value, its default when unset (`unless_empty=True` also when set but empty); for readers that refuse in their own words (the budgets, the model knobs, `VERI_LABEL`, `VERI_DISPATCH_RETRY_SLEEP`, `VERI_GH_REFUSAL_RETRIES`, ...). `resolve(name)`: `(value, None)`, or `(None, (raw, refusal))` for a bad value; the `TABLE` entries only (KeyError otherwise). Also `default(name)`, `parses(name, raw)`, `is_set(name)` (in the environment at all, empty included: how a retired name such as the old absolute growth knob is refused), `get_bytes(name, unless_empty=False)` (`get`, as bytes). A reader of any `VERI_*` name passes no literal default: `test_tunable_defaults_audit.py` fails when one does, bar the sites its `EXEMPT` dict names, a reason each; read that dict, this file does not copy it. Its kinds: a name read at two defaults (not in `TUNABLES`) and the run-context fields the conductor exports.
- `environment()`, `with_values(**values)`, `without(name)`, `pop(name, default="")`: a copy of the environment, with values set or removed; pop mutates it.
- `lane_of(opt_in)`: the lane of a label, `None` for a plain one. `taken_label(opt_in)`: `taken:<lane or main>`. `venv_dir()`: `VERI_VENV` or `~/.veri-tools/venv`. `claude_bin()`: `CLAUDE_BIN`, `claude` when unset or empty.

Every key of `TUNABLES`, its `default(name)` (`""` is the empty string, after which a reader may compute its own fallback, such as a path under `~`), and what a bad value is told: the entry's `refusal`, or "its readers' own words" when it states none. `tests/py/unit/test_tunables_prose_table.py` fails when this table and `TUNABLES` disagree.

| Name | Default | A bad value is told |
|---|---|---|
| `REVISE_BUDGET` | `2` | a whole number |
| `VERI_ADJUDICATE_BUDGET` | `2` | its readers' own words |
| `VERI_AUTHOR_LABEL` | `author-read` | its readers' own words |
| `VERI_BASELINE_FULL_TIER` | `reuse` | run or reuse |
| `VERI_BRANCH_SUITE` | `local` | local or ci |
| `VERI_CALLER_DIR` | `.` | its readers' own words |
| `VERI_CI_FLAKE_RERUNS` | `1` | a whole number |
| `VERI_TEST_QUALITY_FIXES` | `1` | a whole number |
| `VERI_CI_HEAD_WAIT` | `600` | its readers' own words |
| `VERI_CI_NO_RUN_WAIT` | `600` | its readers' own words |
| `VERI_CI_QUEUE_WAIT` | `3600` | its readers' own words |
| `VERI_CI_RETRY_BACKOFF` | `1` | its readers' own words |
| `VERI_COMMENT_CHUNK` | `25` | a whole number >= 1 |
| `VERI_CONDUCTOR_CTX_BUDGET` | `120000` | a whole number of tokens |
| `VERI_DISPATCH_OVERLAP_POLL` | `60` | its readers' own words |
| `VERI_DISPATCH_RETRY_SLEEP` | `5` | its readers' own words |
| `VERI_DISPATCH_STALL` | `3600` | its readers' own words |
| `VERI_EFFORT_VERIFIER` | "" | its readers' own words |
| `VERI_FETCH_RETRY_SLEEP` | `1` | its readers' own words |
| `VERI_FULL_TIER_MAX_AGE_DAYS` | `7` | a whole number of days >= 1 |
| `VERI_GH_DRIVER` | `rest` | its readers' own words |
| `VERI_GH_REFUSAL_RETRIES` | `3` | its readers' own words |
| `VERI_GH_REFUSAL_SLEEP` | `60` | its readers' own words |
| `VERI_GH_TIMEOUT` | `300` | its readers' own words |
| `VERI_GITHUB_OUTAGE_MIN` | `30` | its readers' own words |
| `VERI_GITHUB_STATUS_POLL` | `300` | its readers' own words |
| `VERI_GITHUB_STATUS_TIMEOUT` | `15` | its readers' own words |
| `VERI_GITHUB_STATUS_URL` | `https://www.githubstatus.com` | its readers' own words |
| `VERI_GIT_NETWORK_TIMEOUT` | `600` | its readers' own words |
| `VERI_HEARTBEAT` | `180` | its readers' own words |
| `VERI_ISSUE_REFACTOR_BUDGET` | `10` | its readers' own words |
| `VERI_KILL_POLL` | `0.1` | a non-negative number |
| `VERI_LABEL` | `ready-for-agent` | its readers' own words |
| `VERI_LEAF_ENV` | "" | its readers' own words |
| `VERI_LINT_TIMEOUT` | `1800` | its readers' own words |
| `VERI_MACHINE_NAME` | "" | never: any value is the machine name the pointer comment shows; empty shows `unnamed machine`, and the host name is never read |
| `VERI_MAX_ISSUES` | "" | its readers' own words |
| `VERI_MERGE_LOCK_POLL` | `30` | its readers' own words |
| `VERI_MERGE_LOCK_WAIT` | `1800` | its readers' own words |
| `VERI_MERGE_SETTLE_READS` | `10` | its readers' own words |
| `VERI_MERGE_SETTLE_SLEEP` | `3` | its readers' own words |
| `VERI_MIN_FREE_GB` | `20` | its readers' own words |
| `VERI_MISSING_REROUTE_BUDGET` | `3` | its readers' own words |
| `VERI_PLAN_TOUCHING_CASES` | `100` | its readers' own words |
| `VERI_MODEL` | "" | its readers' own words |
| `VERI_MODEL_ADJUDICATOR` | `opus` | its readers' own words |
| `VERI_MODEL_CONDUCTOR` | `opus` | its readers' own words |
| `VERI_MODEL_DEVELOPER` | `sonnet` | its readers' own words |
| `VERI_MODEL_REVISE` | `opus` | its readers' own words |
| `VERI_MODEL_REVISE_GREEN` | "" | its readers' own words |
| `VERI_MODEL_VERIFIER` | `sonnet` | its readers' own words |
| `VERI_MUTATION_ADDRESS_DOMAIN` | "" | its readers' own words |
| `VERI_NEW_SKILL` | "" | its readers' own words |
| `VERI_NO_VERDICT_RETRIES` | `1` | its readers' own words |
| `VERI_PAGE_RETRIES` | `3` | its readers' own words |
| `VERI_PAGE_RETRY_SLEEP` | `2` | its readers' own words |
| `VERI_PARALLEL` | `1` | its readers' own words |
| `VERI_PRIORITY_LABEL` | `priority` | its readers' own words |
| `VERI_PROFILE_THRESHOLD` | `1` | its readers' own words |
| `VERI_PYCACHE` | "" | its readers' own words |
| `VERI_PYTEST_IDLE` | `1200` | its readers' own words |
| `VERI_PYTEST_LEGS` | "" | its readers' own words |
| `VERI_PYTEST_WAITERS` | "" | its readers' own words |
| `VERI_QUEUE_POLLS` | `3` | its readers' own words |
| `VERI_CONDUCTOR_TEST_WORKERS` | `2` | its readers' own words |
| `VERI_TEST_BUDGET_TTL` | `3600` | its readers' own words |
| `VERI_TEST_CEILING_FILE` | "" | its readers' own words |
| `VERI_TEST_CAP_FILE` | "" | its readers' own words |
| `VERI_TEST_LOAD_FILE` | "" | its readers' own words |
| `VERI_TEST_TIMEOUTS_FILE` | "" | its readers' own words |
| `VERI_LOAD_WINDOW` | `600` | its readers' own words |
| `VERI_TEST_BUDGET_DIR` | "" | its readers' own words |
| `VERI_PYTEST_WORKERS` | "" | its readers' own words |
| `VERI_REBASED_TIP_SUITE` | `local` | local or ci |
| `VERI_RECHECK_PERMISSIONS` | `0` | its readers' own words |
| `VERI_REFACTOR_BUDGET` | `5` | its readers' own words |
| `VERI_REDACT_VARS` | `GH_TOKEN GITHUB_TOKEN ANTHROPIC_API_KEY CLAUDE_CODE_OAUTH_TOKEN` | its readers' own words |
| `VERI_RESET_GROWTH_CONDUCTOR` | `30000` | a whole number of tokens >= 1 |
| `VERI_RUN_BUDGET` | `120` | its readers' own words |
| `VERI_RUN_TIMEOUT` | `14400` | its readers' own words |
| `VERI_SELF_UPDATE` | "" | its readers' own words |
| `VERI_SESSION_TRANSCRIPTS` | "" | its readers' own words |
| `VERI_SETUP_THRESHOLD` | `3` | its readers' own words |
| `VERI_SKILL_EDIT_BUDGET` | `3` | its readers' own words |
| `VERI_SKIP_VERIFY` | "" | its readers' own words |
| `VERI_SLEEP_GAP` | `900` | its readers' own words |
| `VERI_SLICE_COMMITS` | `100` | its readers' own words |
| `VERI_SNAPSHOT_MAX_AGE` | `60` | its readers' own words |
| `VERI_STEP_BUDGET` | `12` | its readers' own words |
| `VERI_STEP_GROWTH_PERCENT` | `50` | its readers' own words |
| `VERI_STOP_KILL_GRACE` | `5` | its readers' own words |
| `VERI_STUCK_RETRIES` | `1` | its readers' own words |
| `VERI_SURROUND_MUTANTS` | `5` | a whole number >= 1 |
| `VERI_TEST_LOCK` | "" | its readers' own words |
| `VERI_TIME_WARN_RATIO` | `1.5` | its readers' own words |
| `VERI_TIMEOUT` | `900` | its readers' own words |
| `VERI_TOOL_FAST_WAIT` | `900` | its readers' own words |
| `VERI_TOOL_IDLE` | `600` | its readers' own words |
| `VERI_TOOL_RETRY_SLEEP` | `15` | its readers' own words |
| `VERI_TOOL_SLOW_SLEEP` | `900` | its readers' own words |
| `VERI_TOOL_WAIT` | `3600` | its readers' own words |
| `VERI_UNIT_BUDGET` | `10` | its readers' own words |
| `VERI_WATCH_QUEUE_INTERVAL` | `60` | its readers' own words |
| `VERI_WORKQUEUE_LOCK_WAIT` | `30` | its readers' own words |

# Run state and journal

Where a run lives on disk, its journal of events and its pin files and mutation record, whether it is live, stuck or ended, and how it is stopped. Builds on Foundations only.

- `bail.sh`: bail a run in one call, `BAIL.md` sub-steps 1–7, printing sub-step 8's report.
- `classify-bail.sh`: label a bail as a process or a system failure.
- `ensure-run-state-ignored.sh`: keep the run's `.tdd/` state git-ignored.
- `event.sh`: append one event to a run's journal.
- `event_table`: the one table of every event veri emits, its keys, which are required and each key's format (`EVENTS`, the run context's in `CONTEXT`); `format(event, key)` and `valid(event, key, value)` read it; imports no veri module.
- `journal_schema`: what JOURNAL.md's table documents per event kind (keys, and their formats with `formats`/`context_formats`), and the literal kinds and fields writer calls pass, found with `ast`.
- `journal_sample`: prints `fixtures/journal/sample.jsonl`, one invented line per event `event_table` declares, every key carried, built through `event.line`.
- `pinned-scripts.sh`: the directory of a run's pinned scripts.
- `run_records`: a run's records (its journal lines, skill pin and timeout pin) carried on origin's `refs/veri/runs/<n>`, a commit on no branch.
- `run_pins`: a run's per-issue pin files (skip-verify list, conductor model, launch environment, baseline full-tier mode) and the `.tdd/.gitignore` seed, written and read in one place.
- `stop-reason.sh`: why a run stopped.
- `stop-requested.sh`: whether a stop is requested.
- `stop-run.sh`: request a run's stop.

## classify_bail
- `CATEGORIES`: dict from a bail cause to `"system"` or `"process"`; an absent cause is unclassified.

## event
- `mark(directory, context, event, fields=(), ts=None)`: appends an event to the run journal; returns 0, or 2 after printing the refusal on any exception.
- `append(directory, context, event, fields=(), ts=None)`: the same without the catch; returns 2 for an empty event name or a bad `structural-pass`, and, under `VERI_EVENT_STRICT=1`, for an event or a value `event_table` does not allow (`strict_refusal(args, context)` says why).
- `context(environ)`: the run's context fields (issue, step, …) read from an environment.
- `stage(name, body, directory="", run_context=None)`: runs `body()` (it returns an exit code) as stage `name`, a `stage-start` line before it and a `stage-end` line (`status`, whole `secs`) after it on every exit, a raise being status 2 and raised on, and a code outside 0 to 3 status 2 (the code returned unchanged); a line whose write exits the process (a short journal write) is dropped, never the body's code; returns the body's code whatever the writes did (`run_context` defaults to `context(os.environ)`, its issue `VERI_STATE_LABEL_ISSUE` when `VERI_ISSUE` is unset); a directory with no `.tdd/` runs the body unmarked.
- `line(args, context, ts, awake)`, `awake_reading()`, `toplevel()`: the JSON line (bytes); the uptime reading (bytes, or an int exit code on a failed clock); the repo top (`""` outside one).
- `common_dir(clone)`: the git common directory of a clone or linked worktree, read from its `.git` without a process; OSError when unreadable.
- `journals(who="status.sh")`: `(path, events)` of every shared journal beside the main tree's, sorted by path; a torn line is skipped and said on stderr as `<who>: skipped torn line <path>:<n>`. `run_name(path)`: the run a journal's path names, `#<n>`. `state_labels(event, issue)`: mirrors a bail, resume or start onto the issue's labels.

## event_log
- `path(run)`: the journal of a run directory, `<run>/.tdd/events.jsonl`.
- `events(run, *kinds, skip_unreadable=False, errors="replace")`: the events of those kinds (all when none), in order; `[]` when the run has no journal; ValueError on an unreadable line unless skipped.
- `last(run, kind, **tolerance)`: the last event of a kind, or `None`; `tolerance` is `events`' `skip_unreadable` and `errors`.
- `read_events(path, skip_unreadable=False, mark_unreadable=False, errors="replace")`: one dict per non-blank line of an `events.jsonl`; `skip_unreadable` drops lines that are not a JSON object, `mark_unreadable` keeps them as `None`.
- `usage_totals(events)`: `(dollars, tokens)` summed over the `usage` events.
- `append_bytes(path, data)`: appends bytes to a file; raises OSError.
- `run_keeping_journal(run)`: calls `run()` and puts the earlier `.tdd/events.jsonl` content back if it no longer starts with it; returns what `run()` returned.

## event_table
- `EVENTS`, `CONTEXT_KEYS`: the table and the run context's string keys; `keys(event)`, `required(event)`: an event's keys in order and the required subset.
- `format(event, key)`: `(format, empty allowed)`, the format a `FORMATS` name or a tuple of values; `valid(event, key, value)`: whether a value matches it; `stated(event, key)`: the format in `JOURNAL.md`'s words.
- `declaring(event, key)`: the table line to write to declare `key` for `event` (`event` None: the `CONTEXT` line).

## mutation_record
The mutation record `.tdd/issue-<n>-mutations.md`: its name and its entry format (`<name> <size>\n<value>\n` fields, a blank line closing each entry, `old`/`new`/`context` base64-encoded under `<name>-b64`).
- `path(run, issue)`: the record of an issue. `of_ledger(ledger_path)`: the record beside a ledger file. `is_record(name)`: whether a basename is `issue-<digits>-mutations.md`. `number(record_path)`: the issue number in its name.
- `paths(run="")`: the records present, sorted, relative when `run` is empty. `snapshot(run="")`: `{path: bytes}` of them.
- `format_record(fields)`: the text of one entry from (name, value) pairs. `append(record_path, fields)`: add one entry to a record.
- `records(text)`: `[{name: value}]`, text fields decoded. `chunks(text)`: `[(raw, fields)]`, each entry's exact text with the blank lines after it and its undecoded fields; raises `MalformedRecord` (a `ValueError` whose `header` is the bad line).
- `stale_pins(run, issue)`: `[(file, first line of old)]` per unretired entry of `<run>`'s record whose `old` text its file under `<run>` no longer holds; a missing record or file adds nothing (`run_finished`, `queued_merge`).

## pid_file
- `number_in(file)`: the number on a pid file's first line, `None` when missing or malformed.
- `live_conductor(path)`: the pid of the live conductor recorded in `path`, else `None`; `not_live_reason(path)` says why. `recorded_alive(path)`, `recorded_started(path)`, `start_recorded(file)`, `start_matches(file, pid)`: parts of that check. `record(path, pid, atomic=False)` writes a pid file (`<pid>\n<start time>\n`, or `<pid>\n` when `ps` gives none) and returns the text it wrote, in place, or with `atomic=True` by renaming a temporary file (the workqueue holder); it is the one writer of that form, `conductor.pid` and `.tdd/workqueue.lock/holder` included.
- `conductors()`: `[(pid, issue)]` of running `run_conductor.py` processes from `ps`. `conductor_processes()`, `starting_runs(root)`, `runs_with_directory(root)`: issues of running conductors by tree.
- The one reader of the machine's process table (ps, pgrep, lsof); a caller keeps its own liveness rule and asks for the table. `listing(*, quiet=False)`: `ps -axo pid=,command=` text (`quiet` drops ps's stderr). `argument_lines()`: `ps -axo args=` text, raises `CalledProcessError` on a failing ps. `same_start(started, pid)`: whether `started` is the pid's start time as `ps -o lstart=` prints it under `LC_ALL=C` and `TZ=UTC`, or, read again only when that differs, under the caller's own environment (an older snapshot's text), the read `caller_start(pid)` makes (`None` when ps cannot read it); `started_utc(pid)`: the start time text `ps -o lstart=` prints under `LC_ALL=C TZ=UTC`, stripped, `""` for an unknown pid. `pids_matching(pattern)`: the pids `pgrep -f` prints. `commands_of(pids)`: `ps -p <pids> -o pid=,command=` text. A machine without the tool raises `FileNotFoundError` from each of these, except `ps_field` (`False`). `merge_lock` reads ps itself because it runs from queued_merge's release copy, which holds only `RELEASE_FILES`.
- `ps_field(field, pid)`: a `ps` column, `None` when the pid is gone. `ancestors()`: the pids from this process up to pid 1. `cwd_of(pid)` (via `lsof`), `is_inside(cwd, root)`, `detached(pid)`, `supervising(pid, name)`: probes of a process.
- `conductor_alive(start)`: whether the conductor a `conductor-start` event names is still that process: its `pid` answers kill 0 and its `started` is the pid's start time (`same_start`).

## pinned_scripts
- `make_snapshot()`: a new empty snapshot directory. `write_snapshot_marker(snapshot, worktree)`: names its worktree. A snapshot's directory name starts `SNAPSHOT_PREFIX`.
- `snapshot_gone(recorded)`, `snapshot_made_for(recorded, worktree)`: bool checks of a recorded path.
- `snapshot_digest(snapshot)`: a sorted list of `(path, token)` tuples, one per entry of a snapshot, the marker included: a directory as `directory`, a file by its content and owner executable bit, a symlink by its target; raises on what it cannot read, on a FIFO, socket or device (never opened), on a file with a second hard link and on a name holding a line break or a control character. `digest_text(entries)`, `parse_digest(text)`: its file form, one JSON list; the read raises `ValueError` on any other text. `first_change(recorded, snapshot)`: the first entry that differs from recorded entries, or that they name twice, joined to the snapshot, or `None`.
- `make_read_only(tree)`: takes the write bits off every file and directory of a snapshot. `remove_tree(tree)`: gives the owner read, write and search on each directory (a mode-000 one included), then removes the tree (raises on what it cannot remove, and, touching nothing, on a tree that is not a real directory). `copy_writable(source, destination)`: the recovery copy, writable. Each changes a mode through a descriptor, never through a symlink.

## restart_marker
A run's `.tdd/restart-pending` marker, which says a conductor restart is in flight.
- `claim(run, pid)`: write `<pid>\n` (not atomic). `clear(run)`: remove it, `FileNotFoundError` when absent.
- `in_flight(run, *, unreadable)`: whether a live restarter holds the marker. Missing, a dead pid or an impossibly large one: `False`; a live pid: `True`. A marker that cannot say (empty, non-digit, undecodable, unopenable, probe denied) answers `unreadable`, which every caller names: dispatch passes `True`, comment and watch_runs `False`.

## run_activity
- `activity(run, closed=False)`: an Activity (frozen dataclass: `state`, `detail`, `phase`, `actor`, `leaf`, `elapsed_seconds`, `attempts`, `dollars`, `tokens`, `pr`, `bail_phase`, `classification`, `stop_mode`, `cause`) for the run directory; `state` is one of `running`, `stale`, `done`, `stopped`, `bailed`, `refused`, `closed`.
- `state(run)`: just that state word. No journal reads as `running`; a dead pid with no end mark is `stale`.

## run_dir
Where a run lives on disk; the module docstring draws the layout. Paths are str and nothing but `main_tree`, `main_tree_from_files` and `worktree_root_from_files` touches the disk.
- `main_tree(cwd=None, *, missing=)`: the repository's main working tree; when git cannot name one it raises `NoMainTree`, or returns `missing` (any value, `""` included) if the caller gave one.
- `main_tree_from_files(start=None)`: the same tree found by reading `.git` files, starting no process: walks up from `start` (default cwd) to the first `.git`; a linked worktree's `.git` file leads through its `commondir` to the main tree; no `.git` answers `start`; OSError when a linked gitdir has no `commondir`.
- `worktree_root_from_files(start=None)`: the working tree holding `start` (default cwd), a linked worktree's own root included: the first directory up from it with a `.git`, starting no process; `start` itself when none. `record_answer` redacts it as `<repo>` beside the main tree.
- `main_file(main, name)`: `<main>/.tdd/<name>`. `worktrees(main)`: `<main>/.tdd/wt`. `worktree(main, issue)`: the run of an issue. `main_of_worktree(run)`: the main tree a `<main>/.tdd/wt/<n>` directory sits under, from the layout alone, `None` for any other directory. `branch_issue(name)`: the issue a run's branch `tdd/<n>-<slug>` names, `None` for any other name.
- `run_file(run, name)`: `<run>/.tdd/<name>`. `issue_file(run, issue, suffix="")`: `<run>/.tdd/issue-<n><suffix>`. `ledger(run, issue)`: the run's ledger.

## run_pins
The pin files a launch records under `.tdd/` as `issue-<n>-<name>`; each pin's writer and reader sit together. The hard-timeout pin is `leaf_timeout`'s.
- `write_skip_verify(root, issue, listed)`, `skip_verify(issue, *roots, unreadable_raises=False)`: the VERI_SKIP_VERIFY list; an unreadable pin answers `None`, or raises its `OSError` with `unreadable_raises`; the read answers the stripped text of the first root holding the pin, `None` when none does.
- `write_conductor_model(root, issue, model)`, `conductor_model(issue, *roots)`: the conductor's model, read the same way.
- `write_launch_env(root, issue, environment)`, `launch_env(issue, root)`: the `VERI_*` environment a restart relaunches with (VERI_NEW_SKILL left out); the read is `{name: value}`, `None` when the run recorded none.
- `write_baseline_full_tier(root, issue, mode)`, `baseline_full_tier(issue, root)`: the baseline full-tier mode, `None` when unpinned.
- `write_snapshot_digest(root, issue, digest)`, `snapshot_digest(issue, root)`, at the suffix `SNAPSHOT_DIGEST`: the digest of the launch's skill snapshot, as written; `None` when none was recorded, other `OSError`s raised.
- `write_branch_base(root, issue, sha)`, `branch_base(issue, root)`, at the suffix `BRANCH_BASE`: the run's branch base, `<sha>\n`, written by `preflight` in the main working tree when a fresh run's branch is cut (its `.tdd/` made when missing) and read back, stripped, on a resume (restored from origin's `refs/veri/runs/<n>` when the main tree has none and the carried sha is hex and an ancestor of HEAD); `OSError` (`FileNotFoundError` when none was recorded) raised.
- `gitignore_seed()`: the bytes a run's `.tdd/.gitignore` is seeded with, derived from the pin suffixes the module names.

## run_records
A run's records on origin's `refs/veri/runs/<n>`: a commit with no parent holding `.tdd/events.jsonl` (the issue's lines and those naming no issue), `.tdd/issue-<n>-skill-commit`, `.tdd/issue-<n>-timeout` and `.tdd/issue-<n>-branch-base`, each read from the run, else from the main tree it sits under, every string first passed through `redaction`'s redaction of token shapes and listed values (`[redacted]`), then redacted in two layers (the named spellings of the paths, the account name and the host names readably; then any string whose decoded, case-folded copy still holds one, whole, as `<redacted>`): only what a reader restores travels. git errors raise `git.GitFailed`.
- `ref(issue)`: the ref's name, `refs/veri/runs/<issue>`.
- `delete(issue, cwd)`: deletes the ref on origin, bounded by `VERI_GIT_NETWORK_TIMEOUT`; `None` when deleted, absent or with no origin, else the reason in one line. Never raises.
- `after_push()`: pushes the records of the issue the current branch `tdd/<n>-<slug>` names, replacing the ref; nothing on another branch; a failure is one stderr line, never raised.
- `read(issue, name, cwd)`: the text of `.tdd/<name>` in origin's ref, fetched into the clone at `cwd` under the same ref; `None` when origin, the ref or the file is missing.
- `redact_local(text, run, also=())`: `text` with the same two layers applied line by line for the run at `run`, each path in `also` written `<repo>` too (a line still leaking after the first is `<redacted>` whole, the other lines kept); `pr_body` passes every PR body it writes through it, and `github.published` every comment body veri posts.
- `PATH_START`, `PATH_END`: regular-expression sources for the boundary before and after a local path, so `/tmpfile` is no `/tmp`; `github.published` builds its pattern on them.

## run_end
- `run_end(run_dir)`: `(ended, cause, standing mark)` for a run, from its events. `standing_mark(events, ends=MARKS)`: the mark that ended the run, the last of `ends` no `resume` or `step-added` followed, `{}` when none stands; `MARKS`: the ending events, each to its cause.
- `latest_result(path)`: `(launched, latest result record or None)` of a conductor log. `conductor_log(run_dir, issue)`: its path.

## stop_modes
- `STOP_MODES`: `("at-ledger", "at-leaf", "now")`. `stop_mode_known(mode)`: bool. `modes_named()`: the modes as a phrase.

# Ledger and plan

The ledger of a run: reading its steps and finding the next one to do, growing, dropping and reordering them, the replaces-case steps, and checks of the plan itself. Ticking a step is in Frozen tests and case history (`tick_ledger` imports `tests_frozen`, which this group may not). Builds on Run state and journal and Foundations.

- `add-ledger-step.sh`: append a planned (`⟦added⟧`) step to the ledger.
- `clear-refactor-pending.sh`: remove a step's `⟂ refactor pending` mark.
- `criterion-finished.sh`: whether every step of an issue criterion is ticked.
- `drop-ledger-step.sh`: remove a step from the ledger.
- `ledger-growth.sh`: check the ledger stayed within `VERI_STEP_GROWTH_PERCENT` of the verified plan's steps. Migration: a run resumed on a new skill snapshot with the retired absolute knob still exported stops at preflight (exit 2), and a small plan that already grew under the old absolute cap may now fail `ledger-growth.sh` (exit 1).
- `ledger-steps.sh`: list the ledger's steps.
- `next-pending-refactor.sh`: the next step whose refactor is pending.
- `next-unchecked.sh`: the next unchecked step.
- `plan-reverify.sh`: check the plan is still the one verified.
- `preserve-attempt.sh`: save a leaf's uncommitted attempt aside.
- `reorder-ledger-steps.sh`: move a ledger step.
- `replaces-case-survivors.sh`: replaced cases that still exist.
- `resume-clean.sh`: discard a resumed run's uncommitted changes.
- `unreplaced-cases.sh`: bash cases a replaces-case step names with no pytest replacement.

## add_ledger_step
- `add(path, where, anchor, texts, *, criterion=None, planned=False)`: what `main` does once parsed, for an in-process caller: inserts `texts` after, before or instead of the one step holding `anchor`. Same exit codes (0 inserted, 1 budget spent or a clean negative, 2 refused) and same stderr as the script.

## issue_body
The one reading of a GitHub issue's markdown body: its `## <heading>` sections, acceptance criteria and blockers. Built on `markdown_sections.fenced_lines`; indexes count lines of `body.split("\n")`. It sits here because it reads the checkbox lines with `ledger.STEP_RE` and the GitHub modules may build on Ledger and plan.
- `CRITERIA`: the heading `## Acceptance criteria`, to hand `spans` (or `section`) for the criteria.
- `spans(body, heading, *, prefix=False)`: `[(start, end)]`, the content lines under each matching heading (start the line after it, end exclusive).
- `section(body, heading, *, prefix=False, occurrence="last")`: the text, `None` when the heading is absent. `occurrence` is `first`, `last` or `all`.
- `criteria(body, *, prefix=False, occurrence="last")`: `[(index, line)]`, the unfenced checkbox lines (`ledger.STEP_RE`) under `## Acceptance criteria`; the k-th criterion is `[k - 1]`.
- `blockers(body, repo)`: the issue numbers under the first `## Blocked by`, as `#<n>` or `https://github.com/<repo>/issues/<n>`; an empty `repo` reads any github.com issue URL as local.
- `add_blocker(body, new)`: `body` with `- #<new>` listed under `## Blocked by` (pinned by `test_coverage_blocker`: every section starting with it, every `None` line).

A heading matches when it equals the heading once stripped (CRLF and trailing whitespace tolerated; `prefix=True` also accepts a suffix); a heading inside a fenced block is none; a section ends at the next unfenced `# ` or `## `; the last occurrence wins unless `first` or `all` is asked. Callers: `blocked_by`, `report_cache`, `tick_issue_criterion`, `ledger_steps`, `add_ledger_step`, `refresh_spec`.

## next_pending_refactor
- `refactor_pending(record)`: the ledger record `next-pending-refactor.sh` prints, a checked step still carrying ` ⟂ refactor pending`.

## ledger
The ledger is a checkbox list; steps carry `⟦…⟧` markers and `⟂` phase marks.
- Reading: `read_ledger(path)`, `read_ledger_stdin()` (text; OSError), `decode_ledger(data)`, `ledger_items(text)`, `ledger_steps(text)` (one `Step` per step line, a named tuple `(number, state, kind, pending, added, criterion, text)`: `number` the 1-based position as a string, `state` `open` or `done`, `pending` `"1"` or `"0"`), `items_at(rev, path)` (OSError when git cannot show it).
- Writing: `replace_ledger(path, data)` (OSError), `rewrite_ledger(path, text)` (None on success), `ledger_tick(text, matcher, pending=False)`, `ledger_mark_phase(text, matcher, phase, owed=False)` (ValueError when the step lacks the phase), `ledger_mark_surround_short(text, matcher)` (`(None, text)` once the step carries ` ⟂ surround short`; ValueError when `surround` is not its next phase), `ledger_clear_pending(text, matcher)`, `tick_line(match)` (a `STEP_RE` match with its box ticked): the first three return `(changed, text)`.
- A step: `listed_phases`, `next_phase`, `unphased`, `trailing_markers`, `unit_of` (str/list/None), `carries_mark(text, name)`, `body(step)` (the text before its first ` ⟂ `), `is_added`, `is_human_owed`, `is_skill_edit`, `is_go_red`, `go_red_probe(step)` (`(file, old, new, case)` of a ⟦go-red⟧ step's probe, `None` without one), `is_retired(text)`, `handed_out(record)`: predicates and parts of its text. `same_step(one, other)`: two step texts name one step, equal once each drops its `⟦…⟧` marks and its trailing ` ⟂ ` suffix (PRD 038.1 SC3); the one comparison a fused stage makes of its record's step.
- Resolving a reference: `step_at(steps, reference, *, text_matches=same_text, by_index=False)` is the `Step` a step number or a step's text names, `None` for "no such step". By default digits are a 1-based position (`"01"` is step 1, never looked up as text); `by_index=True` takes only a step's own `number` string and then falls back to text; `text_matches(reference, text)` is the text rule (equal, the first match wins). `supervise` (equal text, and prefix text for `⟦ci-repair⟧`) and `preserve_attempt` (`by_index`, text or text without its criterion tag) call it.
- Building and checking: `new_step(text, criterion)`, `open_step_line(text)`, `retire_mark(reason)`, `multi_tag_refusal(steps)` (`""` if fine), `receipt_refusal(ledger_file)`, `ledger_path(run_dir, issue)` (a delegate of `run_dir.ledger`; only `wrong_test_route` calls it, deleted once PR #3792 lands), `added_file(path)` (the sibling `-added.md` path of a ledger file).
- Constants: `BEFORE_STATE_GREEN` (compiled pattern: a clause of a pin's reason that calls the before-state green; tick-ledger, pin-reject-route and the develop prompt read it), `REPIN_STEP` (the text a re-pin step opens with: pin-reject-route writes it, diff-step matches it to recheck from the re-armed step's `<green>~1`), `STEP_RE`, `ITEM_RE`, `KIND_RE`, `CRITERION_RE`, `CRITERION_TAG`, `ADDED_MARK`, `PENDING_MARK`, `OPEN_STEP`, `TICKED_STEP`, `GO_RED_MARK`, `INTERFACE_PHASES` (the phases of an interface change: `expand`, `cover-new`, `migrate`, `contract-a`, `contract-b`).

## ledger_steps
- `current_record(records)`: the current step of `ledger.ledger_steps` records (the first done step whose refactor is pending, else the first open step), `None` when there is none.
- `current_or_last_done_record(records)`: the step `ledger-steps.sh current-or-last-done` prints, the current step else the last done one, `None` when neither; `coverage_blocker` names it as the coverage issue's region.

## preserve_attempt
- `preserve(repo, issue, step, phase, attempt, mark="", env=None)`: saves the work tree as a commit under `refs/veri/attempts/…` without touching the branch; returns 0, 1 (stderr message) when the ref or leaf files cannot be written, or a failed git step's code.

## replaces_case
- `parse(step)`: `(case names, suite)` of the clause, `None` when unreadable.
- `is_replaces_case_step(step)`: bool. `quote_of(step)`: the quote character of its names. `refusal(step)`: the reason a step's clause is malformed, `None` when fine.

# Leaf launch and supervision

How a leaf is launched through the supervisor, detached, waited for and timed, and how its stream log is read. Builds on Run state and journal, Ledger and plan, Target suites and tiers, Veri's own test runner, Frozen tests and case history and Foundations.

- `detach-command.sh`: start a command detached and wait for it.
- `detach-leaf.sh`: launch a leaf detached.
- `diff-leaf-deviation.sh`: check a leaf's diff stayed within what its phase may change.
- `extract-result.sh`: pick the result record out of a leaf's stream log.
- `harvest-usage.sh`: turn a leaf log's usage into a `usage` event.
- `leaf-launchable.sh`: probe whether a leaf can launch here.
- `leaf-model.sh`: resolve the model a leaf runs on.
- `leaf-role.sh`: map a leaf's name to its role.
- `leaf-timeout.sh`: derive a leaf's hard timeout.
- `run-leaf.sh`: run one leaf.
- `supervise.sh`: the watchdog every leaf runs under.
- `wait-leaf.sh`: wait for a detached leaf's completion file.

## context_limits
- `context_limits(excludes=(), settings=None)`: the list of `claude` options that limit what a veri session loads; `excludes` adds `claudeMdExcludes` paths after the global `CLAUDE.md`, `settings` further keys of its one `--settings` object (`run_leaf` passes a caller's `--settings <json object>` there, as `verify` gives its write-ban hook).

## extract_result
- `extract(data)`: the text of the last report-bearing `result` record of a stream-json log, newline-terminated; `data` unchanged when it has no result.

## leaf
- `launch(name, prompt, *args, env=None)`: runs the leaf through `supervise.sh`; the CompletedProcess with stdout captured.

## leaf_log
- `result_records(lines)`: every `{"type":"result", …}` record among a leaf log's lines, in order.
- `result_text(line)`: the result string of the result record on one line (str or bytes), else `None`. `last_result_text(lines)`: the final one, else `None`.
- `cost(lines)`: dollars, `total_cost_usd` (missing or null counts 0) summed over the result records that carry a `result` field.
- `plain(number)`: the number as Python prints it, or as a plain decimal when that is exponent form (`1e-05` → `0.00001`), the text a journal's dollar figures are written in.

## leaf_timeout
- `settled(root, issue)`: the run's pinned hard timeout (`<root>/.tdd/issue-<issue>-timeout`) as the digits written, `None` when unpinned; raises `Malformed` (`path`, `text`, `not_a_number`) for a pin that is not a whole number of seconds >= 1.
- `pin_path(root, issue)`: that pin's path. `valid_pin(text)`: whether a pin's text is one `settled` accepts, the check `run_conductor` applies to a carried pin before restoring it.

## leaf_model
- `resolve(name)`: the model for a leaf, `None` when the name is invalid or the model has whitespace (message on stderr).
- `leaf_model(name)`: the same as a string; `""` where `resolve` gives `None`.
- `env_value(key)`: the tunable's value, `""` when unset or only whitespace.

## leaf_role
- `leaf_role(name)`: dict of `VERI_ACTOR`, `VERI_PHASE`, `VERI_ATTEMPT`; `None` after a stderr message for a bad name.
- `is_revise(name)`: True for `revise-*` and `develop-exhausted`.

# Prompts and leaf reports

What a leaf is told (the prompt builders) and what it answers (the `KEY: value` report and the readers of each leaf's report). Builds on Ledger and plan, Run state and journal, Leaf launch and supervision, Target suites and tiers (the run lines a prompt gives, `run_line`) and Foundations.

- `build-adjudicate-prompt.sh`: render the adjudicator leaf's prompt.
- `build-develop-prompt.sh`: render a developer leaf's prompt (red, green, refactor, revise).
- `build-verify-prompt.sh`: render the blind verifier's prompt.
- `cover-outcome.sh`: read a cover leaf's report on stdin.
- `near-duplicates.sh`: list the blocks a commit added that repeat code in the files it touched.
- `pin-target.sh`: read a pin leaf's target from its report.
- `quality_findings`: test-quality.sh: list the test files a run's range touched, and check and record the develop-test-quality leaf's `FINDING:` lines.
- `red-divergence.sh`: read a red leaf's report on stdin.
- `red-setup.sh`: record a verified Red's `SETUP:` count; name the run's worst step as a `testability` candidate.
- `refactor-owed.sh`: append, render and list refactor-owed items.
- `refactor-touched.sh`: the files a refactor leaf touched.
- `refactor-triage.sh`: read a refactor leaf's candidates.
- `seam-outcome.sh`: read a develop-seam leaf's report on stdin.
- `report_formats`: the terminal report formats a develop prompt declares, parsed from its text.
- `structural-predicate.sh`: read a predicate leaf's report on stdin.
- `suite-reported.sh`: read a suite's reported result.
- `tidy-first.sh`: read a green leaf's `TIDY_FIRST:` answer into the step it asks for.

## candidates
- `KEY`: the `CANDIDATES:` marker. `line(text)`: what follows it and any ASCII whitespace on one line (str or bytes), found through `report`; `None` for another line.
- `CLASSES`: the four classes a candidate may name (`structural`, `cosmetic`, `test-only`, `out-of-scope`).
- `candidate(text, cls)`: the text after the bar of a `CANDIDATES: <cls> | <text>` line, whitespace allowed around class and bar; `None` otherwise.

## prompt_template
- `read(path)`: the file's bytes without trailing newlines; raises OSError. `spec_text_of(path)`: the same, `b""` when unreadable.
- `has_heading(text, heading)`: whether `## <heading>` is a line of the bytes.
- `expand_includes(text, prompts, chain=())`: `text` with every `{{INCLUDE:x}}` partial inlined; raises `IncludeRefused` for a missing or self-including partial.
- `fill(text, pairs)`: `text` with each `{{NAME}}` replaced in order from `(name, value)` pairs; a callable value runs only while its placeholder is still in the text.

# Verdicts and verification

The verifier and adjudicator legs: run the blind verifier, parse its verdict, compare rejects, adjudicate an exit 2. Builds on Prompts and leaf reports, Leaf launch and supervision, Ledger and plan, Run state and journal, Target suites and tiers (whether the tree is veri's own, `run_line`) and Foundations.

- `adjudicate.sh`: budget and record commands of the exit-2 adjudication.
- `exhausted-outcome.sh`: transform a develop-exhausted leaf's outcome.
- `parse-adjudication.sh`: read the adjudicator's answer.
- `parse-verdict.sh`: read the verifier's `VERDICT:` line.
- `run-verdict.sh`: run a verifier and print its verdict.
- `same-reject.sh`: compare two rejects.
- `verify.sh`: run a verify leg and decide its verdict.
- `verifier_write_ban`: the PreToolUse hook command a verifier leaf's settings carry; blocks a `Write`, `Edit`, `MultiEdit` or `NotebookEdit` call (exit 2), lets any other through.
- `leaf_tree_guard`: snapshot the repository before a verifier leaf, report what the leaf changed and put it back; `start(args, **kwargs)` (a `subprocess.run` answering a 127 CompletedProcess when the program cannot start) and `git(*args, env=None)` (its stdout captured, stderr dropped) are the process boundary `verify` shares.

# Budgets and cost

The budgets (steps, time, refactor, context, affordability) and what leaves cost. Builds on Run state and journal and Foundations only.

- `context_budget`: the conductor context-budget rule parallel-conductors.sh stops a conductor by.
- `over-budget.sh`: whether a time budget is exceeded.
- `prices`: the price table and the helpers that read it.
- `refactor-budget.sh`: compare transforms applied with `VERI_REFACTOR_BUDGET`.
- `run-affordable.sh`: project whether the run's remaining steps are affordable.
- `step-budget.sh`: the step budgets.
- `step-cost.sh`: what a step spent on leaves, from `usage` events.
- `time-budget.sh`: the time budgets.

## prices
- `PRICES`: dollars per million tokens, by model family and rate (`input`, `cache_read`, `cache_write_5m`, `cache_write_1h`, `output`).
- `family(model)`: the `PRICES` key a model name falls under, `None` when none. `cache_write_tokens(usage)`: a usage's cache-write tokens by rate.

## growth
- `growth(records, baseline=None)`: tokens of context a session grew since its first usage record (or `baseline`), `None` when it has none.

# Veri's own test runner

How veri's own suite runs (`make test`, `make unit`, `make profile`): what the pytest leg shares with the launches, the bytecode cache, the one-full-run lock, the fast-tier admission guard and the per-case profiler. The leg's launcher and its plugins live in `skills/tdd/scripts/tests/leg/`. Builds on Foundations only.

- `content_mtimes`: run by CI before `make test`: sets each tracked file's mtime from its blob id, so a restored `.pyc` of unchanged content stays valid.
- `failed_cases`: the pytest leg's record plugin: keeps, in this process, the cases each session collected and how each one reported.
- `full_run_lock`: the one-full-run lock: at most one full `make test` runs per machine, and a waiter names the holder.
- `leg_tmpdir`: `PINNED_TMPDIR`, the TMPDIR the pytest leg pins before it starts; run-conductor's free-space check reads it too, so a run never imports the leg.
- `ceiling`: test-ceiling.sh's ramp: the highest test-worker count `make test` runs at with no case timeout, recorded in `~/.veri-test-ceiling`; `record_path()` names that file, and the pytest leg reads its line 1 as T, its worker budget. `cap_path()` names `~/.veri-test-cap` (`VERI_TEST_CAP_FILE`) and `read_cap()` returns its line 1 as `(cap, complaint)`: the cap the human set, which lowers T and the ramp's top, or no cap and a one-line complaint for a file it cannot use (PRD 036.11).
- `profile.sh`: per-case timing of suites.
- `pycache_prefix`: sets where this run reads and writes bytecode; a veri module's first line runs it before any veri import.
- `test_budget`: the lane budget's entries under `~/.veri-test-budget` (PRD 036.5), each lane's need and expiry, which every leg reads to narrow T.

## full_run_lock
- `acquire()`: take the lock (waiting for a holder, saying who holds it and marking the wait at `PYTEST_LEG_LOCK_WAIT_MARKER` with a file naming the waiter, its pid and start time in `pid_file.record`'s form; a supervisor ignores a marker whose waiter is no longer alive under that start time, while an empty one, an older leg's, still freezes its timers), record this pid and tree in the lock file and mark this process the holder in `PYTEST_LEG_FULL_LOCK_HOLDER`; returns a `Lock` whose `release()` empties the file and restores the variable.
- `held_by_ancestor()`: True when `PYTEST_LEG_FULL_LOCK_HOLDER` names the live pid the lock file records, so a nested run skips the lock. `enabled()`: False when `VERI_TEST_LOCK` is 0.
- `wait_marker(key)`: the path a waiting run marks its wait at. `legs_dir()`: the registry directory the lock file sits beside. `waiters_dir()`: where a leg waiting for T registers its wait.

## leg_tmpdir
- `PINNED_TMPDIR`: the TMPDIR the pytest leg pins before it starts, and a directory run-conductor's free-space check reads.

## ceiling
- `record_path()`: the ceiling record, `~/.veri-test-ceiling` (`VERI_TEST_CEILING_FILE`); the pytest leg reads its line 1 as T.
- `cap_path()`: the cap file, `~/.veri-test-cap` (`VERI_TEST_CAP_FILE`). `read_cap()`: `(cap, complaint)`, the cap the human set on its line 1, or no cap and a one-line complaint for a file it cannot use; the pytest leg lowers T to it.
- `read_idle(tier)`: the seconds of the record's `idle <tier> <seconds>` line, the tier's idle duration, or None when there is no such line or the record cannot be read; `timed-test-run.sh` journals a `test-stretch` event past twice it (PRD 036.10).

## test_budget
- `write(main_tree, lane, need)`: replaces the lane's entry for that main working tree whole (a temporary file renamed into place): `need` on line 1, now plus `VERI_TEST_BUDGET_TTL` seconds on line 2. `entry_name(main_tree, lane)`: `<lane>@<16 hex of the sha256 of the tree's real path>`.
- `unexpired_entries()`: `[(entry name, need)]` of the entries whose expiry is ahead; an unreadable or malformed one adds nothing, an expired one is removed. `unexpired()`: the same as `[(lane, need)]`, which the pytest leg sums into T.
- `leg()`: the pytest leg's module, loaded from `tests/leg/`, whose capacity and budget dispatch and role_state_cli read.

# Target suites and tiers

Choosing and running the suites of the project veri works on: finding its test commands, the suites a change affects, timed, baseline, branch and rebased-tip runs, flakes, reruns and mutation probes. Builds on Run state and journal and Foundations, and on Veri's own test runner for `ceiling`'s idle durations, which a timed run compares itself against (PRD 036.10).

- `affected-suites.sh`: the test suites a change touches.
- `baseline-full-tier.sh`: run and record the baseline full tier, and record or answer a green baseline preflight may skip.
- `branch-suite.sh`: print `ci` or `local`: where the branch's full suite runs.
- `detect-test-command.sh`: find the project's test commands.
- `full-tier-time.sh`: how long the full tier takes, from recorded runs.
- `mutation-parity.sh`: check the pairs of recorded mutations.
- `mutation-probe.sh`: apply a mutation, run a command, restore.
- `pin-fast-tier.sh`: run the fast tier over the tree a pin would commit.
- `rebased-tip-suite.sh`: print `ci` or `local`: where the rebased tip's suite runs.
- `rerun-alone.sh`: rerun each target of a red run alone.
- `stem_walk`: the whole-word stem walk outside veri's own tree: the files git does not ignore, and which of them name a path's stem.
- `suite-flakes.sh`: flaky targets across runs.
- `surround-mutants.sh`: run a legacy step's mutant table through `mutation-probe.sh`.
- `timed-test-run.sh`: run a test command, save its whole output under `.tdd/test-runs/`, print in its place a declared quiet command's own output (its exit 2 named a broken run), a foreign tree's `changed` run's exit code and last 20 lines, or else a bounded report, and journal one `test-run` event.

## ci_on_pr
- `runs_on_pull_requests()`: True when `declared` gives `"1"` or, `""`, a workflow of the current directory triggers on `pull_request`; ValueError carrying the refusal on a bad value.
- `declared(root=".")`: `VERI_CI_ON_PR` as `"0"` or `"1"`; when it is unset or empty, the `veri: ci on pr:` line of `root`'s `CLAUDE.md` as `"0"` or `"1"`, else `""`; ValueError naming the variable or the line on any other value. `queued_merge` passes its worktree; the other callers read the directory they run in.
- `trigger_lines(text)`: generator of the lines of a workflow's `on:` block (an `on:`, `"on":` or `'on':` key).
- `pull_request_trigger(text)`: True when a workflow's text holds a `pull_request` trigger, False when it was read in full and holds none (a JSON mapping, or a block YAML whose `on:` block was found), None when it was not read (no `on` key found: a flow-mapping root, empty contents); `wait_ci` fails closed on None.

## detect_test_command
- `resolved(tier, issue, root, claude_md=None)`: the test command for a tier, `None` when none is found; `claude_md`, when given, is the CLAUDE.md text read instead of `root`'s file, and only a line it declares answers (no tier is inferred from `root`'s other files).
- `Answer(command)`: the exception that carries a found command out of the search; `answer_from_file(path, marker)` raises it from a file's lines.
- `unwrapped(text)`, `SPACE`: the command a marker's rest names (a leading backtick span unwrapped), and the whitespace stripped before it; `answer_from(line, marker)`: raises `Answer` with the command one line declares after `marker`. `record_test_commands` reads a CLAUDE.md line as the detector does.

## run_line
- `own_tree(root=".")`: whether `root` is veri's own tree (`skills/tdd/scripts/tests/py` is a directory there).
- `own_tree_at(commit, root=".")`: whether `commit` is veri's own tree (it holds `skills/tdd/scripts/tests/py` as a directory); what `affected-suites.sh` decides by, at its range's base, and `run_lines` at its `branch_base` (#4263).
- `base_claude_md(root=".", branch_base="")`: `CLAUDE.md`'s bytes at `branch_base` (`b""` when that commit holds none), or `None` when nothing is read there; where `build-verify-prompt.sh` reads a lint-repair step's `veri: lint:` line (#4263).
- `full_line(root=".", branch_base="")`: the full test command a verifier is given (`{{FULL_CMD}}`): the repo's all-tier command, read as `run_lines` reads its lines, or `the test command` when it declares none (#4263).
- `run_lines(root=".", branch_base="")`: `(changed, one)` as bytes, the commands a leaf prompt gives for the test files `affected-suites.sh` printed and for a single test file: today's `make test TESTS="…"` text in veri's own tree, elsewhere the repo's `veri: one test file:` command once per path through `sh -c`, or its fast command when it declares none, its all-tier command only when it declares neither; a declared `veri: quiet test files:` command replaces the changed one, run once over every path. With `branch_base` (a hex commit name) and a `.git` in `root`, the CLAUDE.md lines, the quiet one included, are read as that commit holds them, never from the working tree, and only declared lines count, and whether `root` is veri's own tree is decided at that commit too (#4263); `BaseUnresolved` when git resolves no such commit.
- `quiet_prefix(root=".", claude_md=None)`: the argv prefix `["sh", "-c", '<quiet> "$@"', "sh"]` running the command the tree's `CLAUDE.md` declares as `veri: quiet test files: <quiet>` over the paths appended to it; `None` when it declares none (never the inferred default) or in veri's own tree. Given `claude_md` (a branch base's `CLAUDE.md` bytes, as `run_lines` reads it at `branch_base`), that text is read in place of the file (#4263).

## rerun_alone
- `named_targets(text)`: the test targets a red run's output names, in order, each once.
- `rerun(alone_cmd, red_file)`: rerun each named target alone; 0 after a `suite-flake` event when all pass, 1 when none is named or one stays red.

## suite_mode
- `run(script, variable)`: prints `ci` or `local` and returns 0; 2 with a message on a bad knob, a bad `VERI_CI_ON_PR` or a bad `veri: ci on pr:` line.

## stem_walk
- `stem(path)`: the path's basename without its last extension, `-` read as `_`.
- `tree_files()`: every file git does not ignore that exists, outside `.git`, `.tdd`, `.venv` and `node_modules`; raises `git.GitFailed` when the listing fails.
- `naming(stem_, paths)`: the paths among `paths` whose text holds `stem_` as a whole word, `-` and `_` alike; an unreadable file names nothing.
- `texts(paths)`: each readable path with its text, `-` read as `_`, so a caller matching many stems reads each file once.
- `naming_in(stems, texts_)`: the paths among `texts_` whose text holds any of `stems` as a whole word.

# Frozen tests and case history

The tests-frozen rule: recording and checking that a step's tests are not changed afterwards, ticking a ledger step (which re-records the earlier steps' cases), routing a rejected pin or wrong test, and the git history of cases. Builds on Ledger and plan, Run state and journal and Foundations.

- `case_identity`: when a case in the tree is the same case as a recorded one (moves, renames, refactors) and the digest of the helpers it calls; tests_frozen decides, this module only identifies.
- `case_history`: the git history queries tests_frozen's record policy asks; it decides, this module only looks.
- `pin-recheck.sh`: re-run the recorded pin mutations a range touches.
- `pin-reject-route.sh`: route a rejected pin to a ledger step.
- `production-frozen.sh`: whether production code changed in a range.
- `restore-production.sh`: restore production files changed against the frozen record.
- `tick-ledger.sh`: tick a ledger step, re-recording the earlier steps' frozen cases.
- `tests-frozen.sh`: record and check that a step's tests stay frozen.
- `transform-touches-tests.sh`: whether a transform touched tests.
- `wrong-test-route.sh`: route a wrong test to its repair.

## case_history
Every query runs in the current directory through `git.git`; a git failure becomes None, False or "" and only an unstartable git raises OSError.
- `toplevel()`: the working tree's root, `None` outside a repository. `has_rev(rev)`: bool. `current_branch()`: the abbreviated HEAD. `default_branch()`: origin's default branch as `refs/remotes/origin/HEAD` names it, asking no remote; raises `git.GitFailed` when it names none.
- `text_at(rev, path, quiet=False)`: the file's text at `rev`, `""` when git cannot show it. `cases_at(rev, path)`: `{case name: body}`; raises OSError when git cannot read `rev`.
- `revisions(path, since=None)`: shas of the commits that touched `path`, newest first. `subject(rev)`: its subject plus a newline.
- `changed_test_files()`: test files that differ from HEAD; raises OSError when a listing fails. `step_commits(step, issue)`, `commit_of(rev)`, `first_revision_with(needle, path)`: a step's own commits, a rev's sha, the oldest commit touching `needle`.

## frozen_record
The record of a step's frozen tests (`.tdd/tests-frozen-<key>.record`) and its pass marker.
- `record_path(step)`: the step's record file under `.tdd/`. The marker's path and the step's 16-hex key are this module's own; only tests read the marker's path, at this module.
- `recorded_cases(step)`: the case names recorded, an empty set when the record is unreadable. `is_marked(records)`: True for a `format: 2` record.
- `body_digest(body)`, `body_line(name, case, body)`, `helpers_line(name, case, digest)`, `case_lines(name, case, body)`, `format_line()`: build record lines.
- `body_record(line)`, `digest_entry(line)`, `helper_records(records)`: parse them (`None` for a line of another kind).
- `write_record(path, out, opener=open)`: True, or False after a stderr message on OSError. `rewrite_records(earlier, rewrite, opener=open)`: rewrites earlier steps' records through `rewrite`.
- `work_tree_hash()`: git tree hash of the work tree outside `.tdd/`, `""` when git fails.
- `write_pass_marker(step, tree)`, `remove_pass_marker(step)`, `pass_marker_current(text)`: write, drop (never raises), and check (bool) the marker against HEAD and the tree.

## tests_frozen
- `differing_tests()`: test files changed against HEAD; raises OSError when git cannot list.
- `record(record_file, files, step=None)`, `check(record_file, step=None)`: the `record` and `check` subcommands with explicit arguments; each returns the exit code (0, 1 or 2) and speaks as the CLI does. `step=None` records or checks the files given; with a step it also covers the test files that differ from HEAD.
- `is_diff_checked(line)`: bool for a `⟦diff-checked⟧` step. `rerecord_earlier(ledger, step)`, `rerecord_committed(step, root)`: re-record earlier steps' frozen cases; `rerecord_earlier` returns 3 for a step that is not diff-checked, 2 on an unreadable ledger or outside a repo.

# GitHub and issues

gh access, issue selection (solvable, parked, blocked), claiming and releasing issues, specs captured from issues and ticking an issue's criteria. Builds on Ledger and plan, Run state and journal, Target suites and tiers and Foundations.

- `capture-spec.sh`: capture an issue as a spec file.
- `coverage-blocker.sh`: file a coverage issue and block the refactor issue on it.
- `github-status.sh`: whether GitHub's status page has an incident, open long enough, on the components veri needs; `wait` blocks, polling, until none counts (exit 3: call again).
- `invisible-work.sh`: sweep for work not visible on its issue. A local branch not on origin is skipped only when its tip equals the head sha of a MERGED or CLOSED PR that used its name; otherwise it is reported under invariant 1, a reused name included.
- `issue-decisions.sh`: the decisions on an issue, oldest first, each marked `owner:` or `judge:`; a stranger's comment and veri's own are never one.
- `park-decision.sh`: the owner's answer to a park: the trusted comments after an issue's newest parked comment.
- `park-issue.sh`: park an issue with its cause and unblock.
- `parked-issues.sh`: list the parked issues, each with its blockers' state and whether its park's question is still unanswered.
- `pointer-comment.sh`: the issue's one `### 📍 Run state` comment, posted when it has none and edited in place otherwise.
- `record-answer.sh`: post the owner's answer to a question tied to an issue on that issue, once, local paths, host and account names redacted.
- `refactor-candidates.sh`: file the run's one candidates issue.
- `refresh-spec.sh`: re-capture an issue's spec.
- `release-issue.sh`: release a parked, bailed or refused issue.
- `release-covered.sh`: release the bailed refactor issue a coverage issue's title names (`Cover the behaviour #<m> refactors`).
- `report-cache.sh`: refresh the cached report data.
- `solvable-issues.sh`: list the issues a conductor may take, in band order.
- `tick-issue-criterion.sh`: tick a criterion on the issue.
- `unlabel-issue.sh`: remove the opt-in label from an issue.
- `workqueue.sh`: the work queue's subcommands. Taking the lock (`.tdd/workqueue.lock`) writes the taker's pid and start time to `.tdd/workqueue.lock/holder` (`pid_file.record`'s form), and release removes it with the directory; a take that gives up exits 2 with `could not take the lock <path>; holder <pid> alive`, `holder <pid> dead` (no such pid, or one started at another time than recorded) or `holder unrecorded`, and never takes the lock over. A holder write that fails releases the lock.

## blocked_by
- `blockers(body, repo)`: the issue numbers under `## Blocked by`, as `#<n>` or `repo`'s issue URL.
- `add(body, new)`: `body` with `- #<new>` listed under that heading.

## github
Every GitHub call goes through `gh`; `VERI_GH_DRIVER` picks the route. A failed call raises `NoAnswer(answer, detail="")`.
- `gh_issue_view(number, field)`, `gh_issue_list(*args)`, `gh_rest_list(path, empty)`, `gh_json(fixture, path, *args)`, `gh_json_page(...)`: reads; return text, or parsed pages for the `*_list`/`_json` forms. A `gh_json_page(...)` call with no gh arguments is a REST read of `path` (`gh api <path>`) under every driver.
- `gh_issue_create(title, body, *labels)`, `gh_issue_edit(number, body_file)`, `gh_issue_comment(number, body)`: writes.
- `published(text)`: `text` as a comment publishes it: `run_records.redact_local` for the run at the working directory (`<repo>`, `<tmp>`, `~`, `<host>`, `<user>`), then any other absolute local path (`/Users`, `/home`, `/tmp`, `/var/folders`, `/private`) replaced by `<path>`; every comment veri posts passes its body through it at the call, which `tests/py/unit/test_comment_choke_audit.py` enforces over every module under `veri/`.
- `authenticated_login()`: the login `gh` is authenticated as, read quietly; `NoAnswer` when it cannot be read.
- `trusted_comment(comment)`: whether a REST comment record may speak for a run (PRD 022.3): its `author_association` is `OWNER` or `COLLABORATOR`, or its `user.login` is the authenticated `gh` user's, that login, once read, kept for the process; a read that gets no answer is not kept, so the association alone answers that call and the next one reads again. Decided from the fields GitHub sets, never the body; a record whose author cannot be read is not trusted. Every reader of comments goes through it (`unit/test_comment_readers_trust.py`).
- `VERI_COMMENT_PREFIXES`: how every comment veri posts on an issue begins (its emoji headings and the needs-user note), so a reader of a human's answer skips veri's own; `unit/test_veri_comment_prefixes.py` fails on a posted heading it lacks.
- `author_association(record)`, `trusted_author(record, associations=TRUSTED_ASSOCIATIONS)`: a REST record's `author_association`, `unknown` when it cannot be read, and whether it is one of <associations>: the one author rule `trusted_comment` and selection share. `ISSUE_AUTHOR_ASSOCIATIONS` (`OWNER`, `MEMBER`, `COLLABORATOR`) is who may author a takeable issue (PRD 022.4); every lister of issues goes through it (`unit/test_issue_author_readers_trust.py`).
- `Pull.cross_repository`: whether a PR's head is in another repository (PRD 022.14), from `isCrossRepository` or REST `head.repo.full_name` against `base.repo.full_name`; a null head repository or a record saying neither reads as another. Every PR claim reader decides by it (`unit/test_pr_claim_readers_same_repository.py`).
- `rest_items(path)`, `issue_comments(number)`: every page of a REST list, or of an issue's comments, as records, gh's stderr captured and not echoed; `gh_comment_post(number, body)`, `gh_comment_edit(comment_id, body)`: a comment posted or replaced, likewise silent. Each failure is a `NoAnswer` whose `detail` is gh's stderr.
- `gh_issue_add_label(number, label)`, `gh_issue_remove_label(number, label)` (a 404 is fine), `gh_label_exists(label)` (False on a 404, `NoAnswer` on any other failure), `gh_label_ensure(label)` (already existing is fine), `gh_label_create(name)`, `gh_api_add_label(path, name)`: label operations.
- `gh_api(path, stderr=None)`, `gh_api_delete(path)`, `gh_run_rerun_failed(run_id)` (`gh run rerun <run_id> --failed`, stderr captured), `gh_probe(*args)`, `run_gh(*args, stderr=None)`: raw `CompletedProcess` results; `run_gh` waits and retries while `gh` is not installed. Every process `github` starts (`run_gh`, `gh_probe`, `rate_limit_reset`, `gh_pr_ready`'s `git ls-remote`, `push_dry_run`) is killed after `VERI_GH_TIMEOUT` seconds (default 300) and answered as that call failing: exit 124, with `<command>: no answer after <n>s (VERI_GH_TIMEOUT)` on the stream the caller captures, else on our stderr (`rate_limit_reset` then answers `None`). The `git ls-remote` is started in a session of its own and its whole process group is killed at the bound, so no `ssh` it started outlives it; a `gh` call is killed alone. A `VERI_GH_TIMEOUT` that is not a whole number of at least 1 is a `NoAnswer` with one stderr line naming it. Every argument of a `gh` command line `bounded` starts is first passed through `redaction.redact`, which `github` also exports as `redact`.
- `push_dry_run(refspec, env)`: `git push --dry-run --no-verify origin <refspec>` under `env`, in a process group of its own killed at `VERI_GH_TIMEOUT`, like `gh_pr_ready`'s `git ls-remote`; `ready-check.sh`'s `push dry-run` row.
- `bounded_group(argv, limit_name="VERI_GH_TIMEOUT", **kwargs)`: that group-killing bound for a caller's own child, the limit read from `limit_name` (queued_merge passes `VERI_GIT_NETWORK_TIMEOUT` for its git network calls) and named in the line; a call killed at the bound is answered as a `TimedOut`, a `CompletedProcess` with exit 124, so a caller tells it from a child that exited 124 itself.
- `gh_pr_ready(number, head_sha="")`, `gh_pr_diff_names(number)`: mark a draft PR ready, list the paths of a PR.
- `gh_pr_create(head, base, title, body)`: open a pull request from branch `head` against `base` (REST), answering its URL; a `NoAnswer` whose `detail` is gh's stderr on failure.
- `open_pulls(fields, state="open", head=None, limit=10000, repo=None)`: the pull requests as Pull records (`number`, `url`, `html_url`, `draft`, `head_ref`, `head_sha`, `body`, `state`, `labels`), the same whichever route or fixture (`prs.json`) answered. `draft` is `None` when the answer carried no flag (a record with both spellings reads `isDraft`); each caller spells its own default, `pr.draft is True`, `is not True` or `is False`. `fields` are the GraphQL `--json` fields, `limit=None` leaves gh's default. `open_pulls_text(...)` is the same read as text and `pulls_in(text)` the parse, for a caller deciding over a partial answer (`NoAnswer.answer`) or a list that is not JSON.
- `pull(url_or_number, repo=None)`: one pull request as a Pull record (adds `mergeable`), read over REST under every driver; `NoAnswer` with gh's stderr as `detail` (not echoed) when the read fails, `ValueError` on a non-JSON answer.
- `closed_issues(body, loose=False)`: the issue numbers (strings) a PR body closes with `Closes #n`, in order; `loose` reads `[Cc]loses #n` anywhere, as `status --recover` does.
- `joined_issues(base, repo=None)`: the issue numbers (ints) a `Closes #n` line names in the body of a pull request merged into `base` (a run that joined the stack branch); `NoAnswer` when GitHub gave none.
- `merged_pulls(base, repo=None)`: the pull requests merged into `base` as Pull records, a fork's kept with `cross_repository` True for the caller to decide; `joined_issues`' read. `pr_body_edit(number, body)`: replace a pull request's body over REST; `NoAnswer` when refused.
- `stack_pulls(head, base)`: the open pull requests from `head` to `base` as Pull records, at most `PULL_PAGES` REST pages, kept only when the answer itself names both refs and the head lives in the base repository (`head.repo.full_name` the base's and `head.label` `<owner>:<head>`; a fork's or a deleted fork's never); `NoAnswer` for a failed read, a page that is not a list of objects, or one past the bound. `pr_open(head, base, title, body)`: opens a ready (never draft) pull request from `head` to `base` and returns its html url; `NoAnswer` when the call fails or the answer names no pull request url. `stack-pr.sh`'s calls.
- `check_runs(sha)`: the check runs of a commit, read by sha, as `[(status, conclusion)]`, GitHub's `filter=latest` (a re-run counts by its latest attempt), every page until the answer's `total_count`, at most `CHECK_RUN_PAGES` pages; `ValueError` for a sha that is not hex, before any read; `NoAnswer` for a failed read, a garbled or short answer, or a total past the bound. `stack-green.sh`'s read.
- `workflow_runs(branch)`: the newest 100 workflow runs GitHub lists for a branch, one read, as `[(head_sha, html_url, status, conclusion, created_at, run_attempt, workflow_id)]`, kept only when the run's head repository is the repository it ran in (a fork's branch of the same name lists too); `NoAnswer` for a failed read or an answer not of the workflow-runs shape. `stack-red.sh`'s read.
- `run_attempt(run_id, attempt)`: `(status, conclusion)` of one attempt of a workflow run; `NoAnswer` for a bad run id or attempt (before any call), a failed read, or an answer not that attempt's record. `stack-red.sh`'s read of a re-run's previous attempt.
- `run_failed_log(run_id, attempt=None)`: the failed-job log of a workflow run (`gh run view <id> --log-failed`, `--attempt <n>` when given) as gh prints it; `NoAnswer` for a run id that is not a whole number, before any call, or a call that fails. `stack-culprit.sh`'s read.
- `rate_limit_reset(run=subprocess.run)`: the epoch second the core rate limit resets, `None` when unreadable. `refusal_retries()`: how many rate-limit refusals a read waits out (`VERI_GH_REFUSAL_RETRIES`); NoAnswer when invalid. `PARKED_HEADING`: the `### ⏸ Parked` heading.
- `refusal_kind(text)` and `NoAnswer.kind` (of its `detail`, else its `answer`): what kind of refusal gh's words describe, `"rate-limit"` (`rate limit`, a `Retry-After` or exhausted `X-RateLimit-Remaining` header), `"transient"` (`HTTP 5…`, `error connecting to api.github.com`) or `"refused"`; a rate limit outranks a transient marker. The one marker set: callers ask it and keep their own waiting policy, never matching stderr words themselves. `VERI_GH_REFUSAL_RETRIES` is spent inside `github`'s own reads (60 s sleeps) and again by `dispatch` (waits for the reset), each layer counting on its own.

## pointer_comment
- `mirror(issue, pushed_at=None)`: post or edit issue `issue`'s one `### 📍 Run state` comment from the current directory's branch, ledger and journal; `pushed_at` is the push just made, else the comment keeps its last one. Never changes its caller's exit code.
- `after_push()`: `mirror` for the issue the current branch `tdd/<n>-<slug>` names, stamped with the time now; nothing on another branch.

## solvable_issues
- `solvable(label, priority="priority", repo=None)`: `(exit code, issue numbers)` in selection order; code 2 when the listing is unreadable.
- `solvable_in_scope()`: the same for the configured scope. `priority_label()`: the label, `None` when set but empty.

## park_decision
- `own_words(body)`: a comment body without its quoted lines (`>`) and code fences, stripped; `""` when nothing else is left. The one reading of a human's own words in a comment: `issue_decisions` prints them as a decision, `parked_issues` counts them as the answer to a park's question.

# Branch, PR and merge

Worktrees, pushing a branch, readying and merging the pull request, waiting for CI. Builds on GitHub and issues, Ledger and plan, Run state and journal, Target suites and tiers and Foundations.

- `ci-flake.sh`: rerun alone the test targets a red CI run's failed log names, and re-run its failed jobs once when all pass.
- `ci_decision`: what a polled CI state means for `wait-ci.sh`, as a pure `decide()` (values in, a decision out).
- `ci_marks`: the `.tdd/ci-*` marks `wait-ci.sh` keeps for a head, with their file names and contents.
- `coupling.sh`: the pairs of same-extension code files, one changed in a range, that import or invoke each other, for the pull request body.
- `issue-worktree.sh`: create or reuse the worktree of an issue's run.
- `lint-repair.sh`: compose the redacted repair step a red lint gets.
- `merge-lock.sh`: take, release and gate on the merge lock.
- `merge_common`: the merge call, the settle-window read (`VERI_MERGE_SETTLE_READS`, `VERI_MERGE_SETTLE_SLEEP`) and the CI wait a landing makes, each taking the call it makes so the caller keeps its own process seam; the merge call's optional `driver` is used instead of `VERI_GH_DRIVER`, so a caller can demand `gh pr merge <pr> --rebase --match-head-commit <head>`.
- `pr-body.sh`: write a pull request's body.
- `pr-ready.sh`: mark a pull request ready.
- `push-branch.sh`: push the run's branch.
- `queued-merge.sh`: merge a pull request in turn and clean up; during an outage join offline (`--skip-suite` skips its gate), and `--local-green` lifts the local freeze.
- `record-test-commands.sh`: commit a project's test commands to its CLAUDE.md on the branch `veri-install` and open its pull request.
- `ready-check.sh`: the checks before a pull request is readied.
- `rebase-onto-default.sh`: rebase the branch onto the default branch; on a run's branch, re-record its branch base as the onto sha, already up to date included.
- `stack-carry.sh`: carry the stack onto the new default branch after a slice landed, by `rebase --onto` in a worktree of its own, pushed under a pinned lease only when a merge-tree check agrees with the new tip.
- `stack-culprit.sh`: name the issue whose end turned the stack red, and the cases it broke, by running them alone at each issue end in a worktree of its own.
- `stack-fix.sh`: push a fix worktree's reviewed hand fix on top of a red stack, once per culprit, after checking its bounds and running the named cases, the fast tier and `prose-owed.sh` at its HEAD.
- `stack-green.sh`: print the newest stack commit that ends an issue and that CI passed, where a slice may be cut.
- `stack-land.sh`: land the stack's tested cut on the default branch; any argument other than `--now` is exit 2 with its usage line.
- `stack-pr.sh`: print the one open pull request tracking the stack branch, opening it when none is.
- `stack-recover.sh`: after a GitHub outage, push each offline join's branch (its `Veri-Joined:` trailer) and then the stack under leases, confirm each joined pull request reads merged, delete the joined runs' remote branches and run records, and print the pushed tip and the tracking pull request.
- `stack-red.sh`: print CI's latest answer on the stack branch when it is red, which freezes joins; during an outage, `.tdd/stack-local-red` instead.
- `stack-revert.sh`: revert an issue's commits on the stack, its hand fix included, as one commit on the tip in a worktree of its own, and lift its join claim from the merged pull requests' bodies.
- `stack-tag.sh`: cut the tags of a landed slice, one annotated `vN.M` per issue whose commits in it include a `feat` or `fix`, on that issue's last commit on the default branch.
- `unwired.sh`: the non-test files a range adds that no other non-test file names, the gate before a pull request is readied.
- `wait-ci.sh`: wait for a pull request's CI.
- `worktree-setup.sh`: set up a worktree.

## ci_marks
- `load(run, key, head)`: the `Marks` a poll of `head` reads. `seconds(run, kind, key)`: a mark's number, None when absent or not one; `exists(run, kind, key)`.
- `record(run, kind, key, value)`, `remove(run, kind, key)`: write or drop one mark. `fresh_window(run, key)`: drop every mark of `key`, so the next wait records a fresh deadline.

## ci_flake
- `ANSI`: the pattern of the terminal colour codes a runner's text carries, stripped before a line is read. `runner_text(log)`: the runner's own text of a `gh run view --log-failed` log, gh's job and step prefixes and timestamps removed.

## merge_common
- `merge(gate, pr, repo, number, head, driver=None)`: the exit code of merging `pr` at `head` by rebase, each command run as `gate(*argv)`: `gh pr merge <pr> --rebase --match-head-commit <head>` under the `graphql` driver, the REST PUT under `rest`, the REST PUT after a failed `gh pr merge` under `auto`; `driver` overrides `VERI_GH_DRIVER`.
- `settle_window()`: `((reads, sleep), None)` from `VERI_MERGE_SETTLE_READS` and `VERI_MERGE_SETTLE_SLEEP`, or `(None, refusal)` when either is unusable. `settle(read, window, wait_first=False)`: the answers of `read()` over the window, ending at the first that `merged(pull)` (its `merged` is `True`).
- `ci_wait(wait)`: `wait()`'s exit code once it answers other than 3, calling it again on a 3.

## stack_culprit
- `verdict(code, output, case)`: what an alone run of a case says: `True` red (non-zero, with a failure line naming the case), `False` not red (exit 0), `ABSENT` (not found or not collected, its output matching `ABSENT_OUTPUT`), `None` no answer; the exit code alone never decides.
- `owners(subjects)`: per subject, oldest first, the issues its commit belongs to by KT5's subject rule (those it names, else the nearest earlier subject's).

## stack_fix
- `script(name, *args, limit=None)`: runs the sibling script `name`: `(exit code, stdout)`, its stderr passed through; with `limit` (a tunable's name, such as `NETWORK`, which is `VERI_GIT_NETWORK_TIMEOUT`) its process group is killed at that bound and the call answers 2.
- `NoAnswer`: no answer from git, GitHub or a script (exit 2). `Refused`: a bound not held (exit 1). Each one's message says why.
- `log(rev_range)`: the commits of a range, oldest first, as `[(sha, subject, [Stack-fix trailer values])]`. `tier_and_prose(top, say)`: the fast tier and `prose-owed.sh` at HEAD in `top`, `say` ending each message. `pushed(head, stack, onto)`: pushes `head` to `stack`, leased to `onto` and a fast-forward of it, read back after a push that did not answer 0. `comment(stack, default, issue, body, name)`: adds `body` once to the stack's tracking pull request and to the issue, a failure said on stderr prefixed `name`.

## stack_green
- `named(subject)`: the issue numbers a commit subject names in the parenthesised group or groups it ends with. `issue_ends(subjects)`: per subject, whether its commit is an issue end. `tested(runs)`: whether check runs `[(status, conclusion)]` call a commit tested. `ENDS_READ`: the newest issue ends read.

# Prose grading and requirements

Graded prose: the Requirements rows of a unit, grading them with a leaf, the prose still owed grading and the skill-edit step. Builds on Leaf launch and supervision, Ledger and plan, GitHub and issues, Run state and journal and Foundations.

- `grade-prose.sh`: grade a unit's requirements rows with a leaf.
- `graded-changed.sh`: whether graded prose changed in a range.
- `prose-owed.sh`: the graded prose still owed grading.
- `requirements-preflight.sh`: check an issue's requirements rows.
- `scope-check.sh`: checks of a plan's scope. It sits here, not in Ledger and plan, because its row-move check reads `GRADED` through `grade_prose`.
- `skill-drift.sh`: block when the skill drifted from the pinned snapshot.
- `skill-edit-guard.sh`: what a skill-edit author may change (`main(argv)`: 2 on a bad base or a missing unit).
- `skill-edit-step.sh`: run a skill-edit step's author.
- `stale-rows.sh`: requirements rows gone stale.

## grade_prose
- `grade_unit(path, unit, read=None)`: grades a prose unit, its file's text answered by its `read` argument (None: the working tree; `stale_rows` passes the default branch's), for `stale_rows` and `skill_edit_step`. Returns a `Grading` named tuple whose `code` is 0 PASS, 1 REJECT, 2 no answer; `verdict`, `failing` row ids, `lines`, `cost`, `grading_id`; its property `out` is what `grade-prose.sh` prints; on PASS it also signs `GRADED` and journals a `grading` event. The script itself takes `--owed`, `--convert` and `--signed <base>` as modes and exits 2 on bad arguments; `--signed` prints each unit the branch signed since `<base>`, decoded, beside its `REQUIREMENTS.md`, a line present at `<base>` left out, for the `DRAFT-PR.md` regrade block and `pr-prepare.sh`.
- The `GRADED` file's line grammar (fields split on a single space: unit, signature, date, grading id, grader-template prefix; the unit field with each `%` as `%25` and each space as `%20`, so a `file#heading` unit is one field) is read and written in this module alone, by graded_fields and graded_line (inverses), graded_lines and record_graded; `graded_changed` and `scope_check` read `GRADED` through `graded_lines(graded)` (`scope_check` finding the file with `graded_path`), which yields each line's decoded fields; `skill_edit_step` decodes a line's unit field with `graded_fields`, splitting the line itself on any whitespace.
- `signature(path, unit, text=None, units=None)`: the sha256 that stamps a graded unit, over `text` when given (the text a grade was made on) and the working tree's otherwise (a split whole-file unit's view of it; `units`, the listed units when the caller has read them), its rows and the grader model, plus the effort level when `grader.conf` has an `effort=` line; the model is the `model=` line's value wherever it sits in `grader.conf`. `unit_text(unit, reader=None)`, `graded_path(unit)`: the unit's text (read through `reader`, the working tree when `None`), its `GRADED` file path. A `file#heading` unit's text is its own text, up to the next unfenced heading line of any level; a heading matching no unfenced heading line, or several, raises ValueError naming the unit and the count. `claimed_headings(file, units=None)`: the headings of the listed `file#heading` units. `signed_text(unit, text, units=None)`: what a unit signs and the grader is shown, a split whole-file unit's view (its heading lines, then the text above the first heading and every unclaimed section's own text) or else `text`.
- `owed_listed(path="REQUIREMENTS.md")`: `(owed, orphans)`, with `owed` the `(list, unit)` pairs whose graded signature is stale; `prose_owed` imports it (`suite_red_resume` reads it as `prose_owed.owed_listed`). It lives here so `prose_owed` builds on `grade_prose` and not the reverse: `signer()` runs the tree's own `grade_prose.py` for the formula, so the stamp's functions stay in that one file.
- `listed_pairs(path)`: `(pairs, units)`, every `(list, unit)` pair the tracked lists name, `path` first, and the units alone; `prose_owed` reads the units to name each prompt file no list names (`(no rows)`).
- `modern_python_dir()`: the PATH directory holding a Python 3.12+ `python3` plus a trailing separator, `""` when none.

# Conductors and operator tools

The conductor loop, parallel conductors, lanes and the operator's views (status, metrics, reports). The top of the tree: no group builds on it.

- `comment.sh`: post the run's Done or Bail comment on the issue.
- `decision-log.sh`: record a judge's decision about no issue in `.tdd/decisions.jsonl` of the main working tree.
- `dispatch.sh`: the dev session's dispatch target and exits watch.
- `github-outage.sh`: the dev session's local mode during a GitHub outage: the outage file of held PRs, the merging list and the one detached status wait per main working tree, each verb under one lock; the status read runs in-process through `github_status`.
- `install-links.sh`: link veri's skills into a project.
- `metrics.sh`: a run's metrics report.
- `reject-breakdown.sh`: the verifier REJECTs of dated metrics reports per week, per phase and per reason class.
- `no-product-caller.sh`: scan for callers of a product name.
- `parallel-conductors.sh`: launch conductors in parallel up to the cap.
- `prd_report`: report.sh's renderer, run in-process.
- `preflight-refused.sh`: record that preflight refused an issue.
- `preflight.sh`: the checks before a run starts.
- `plan-publish.sh`: SKILL.md step 2's fixed tail once the plan is written, in one call.
- `run-start.sh`: SKILL.md step 1's fixed calls after preflight, in one call.
- `resume-start.sh`: RESUME.md sub-steps 1-4's fixed calls and the owed verify-plan launch, in one call.
- `fused_step`: the step helpers the fused halves share above `fused`.
- `seam_contract`: per record-writing stage, the keys the next stage reads that no committed fact holds.
- `red-half.sh`: a step's Red half on the FAILS path, in one call.
- `green-half.sh`: a step's Green half on the PASS path, in one call.
- `refactor-half.sh`: a step's first refactor pass, in one call.
- `step-close.sh`: a step's close-out after a passing verify-refactor, in one call.
- `seam-settle.sh`: after a stage done by hand, the record its script would have written.
- `run-step.sh`: a cycle step's four fused stages in one call, stopping at the first seam.
- `revise.sh`: REVISE.md's revise loop for one phase a verifier rejected, sliced like a fused half.
- `diff-step.sh`: a ⟦diff-checked⟧ step's clean path in one sliced call, ending on `step-tick.sh`.
- `go-red-step.sh`: a ⟦go-red⟧ step's one stage, a mutation probe on its named case, ending on `step-tick.sh`.
- `step-tick.sh`: the close of a step no cycle closes, in one call.
- `skill-edit-half.sh`: a ⟦skill-edit⟧ step's clean path in one call.
- `reroute.sh`: `wrong-test-route.sh`'s answer for the open step through the rerouted red, verify-red and the frozen-test re-record, sliced like a fused half.
- `branch-gate.sh`: the Draft PR step's branch suite, in one call.
- `pr-prepare.sh`: the Draft PR step's sub-step 1 up to the structural pass's skip, in one call.
- `pr-checks.sh`: the Draft PR step's sub-step 1 checks after `pr-prepare.sh`, in one call.
- `pr-ready-wait.sh`: closing and pushing the run's record, then readying its PR and its first CI wait, in one call.
- `run-pr.sh`: the Draft PR step's stages in one call, stopping at the title seam (`veri/run_pr.py`).
- `pr-finish.sh`: the refactor-owed render after a green first CI wait, in one call.
- `run-done.sh`: the run's done comment, in one call.
- `stop-settle.sh`: a stop, STOPPING.md steps 1–6, settled in one call.
- `reset-cost.sh`: what each recorded restart of a run's conductor cost, and the growth knob it calls for.
- `restart-conductor.sh`: stop and watch a conductor restart.
- `role-state.sh`: the dev session's recorded state.
- `role_state_cli`: role-state.sh's entry point: role_state's verbs, a written `set n` also writing the lane's test budget entry and printing the T it leaves; apart from role_state so that status never imports watch_runs.
- `run-conductor.sh`: launch one conductor on an issue.
- `run-finished.sh`: whether an issue's run finished.
- `script-help.sh`: look up a script's help.
- `status.sh`: the runs and scope totals view.
- `suite-red-resume.sh`: resume after a red suite.
- `timed_n_format`: the `<n> until <ISO-8601>` text of a timed-n line; role_state's reader and writer both parse it.
- `unreachable.sh`: walk reachability of the modules.
- `update-veri.sh`: update veri itself.
- `watch-runs.sh`: watch the runs of a queue.

## fused_step
- `inputs(name, n, *files)`: the settled preflight values and worktree once every input exists, else `None`, each missing one on stderr (FC15). `first_step(wt, n, chosen)`: the first ledger step a predicate takes.
- `cost_check(wt, step)`: *The step's cost check*, stopping at `cost-check`. `verify_switched_off(wt, n, phase)`: the run's pinned `VERI_SKIP_VERIFY` names the phase.
- `summary(step)`: the step's ledger text without its trailing markers, as a commit subject reads it (the #431/#437 rule).
- `branch_base(where, wt, n)`: the run's branch base as the conductor recorded it in the main working tree above `wt` (`run_pins`), each verdict launch's `--branch-base`; a record missing or unreadable is a `Stop` with exit 2 naming it (#4375).
- `green_tick(where, wt, n, rev)`: the newest ledger commit reachable from `rev` that changes a line other than a re-pin step's (`ledger.REPIN_STEP`), or `None`: the green tick of the step its re-pins re-arm, which `diff-step.sh`'s recheck base (#4511), `refactor-half.sh`'s touched files (#4510) and verify-refactor's `--step-green`, the bounds of its check 8 (#4544), read.
- `red_test_id(test_path, target)`: the Red case's id, `<target>` when it holds `::`, else `<test_path>::<target>`.
- `refresh(stage, wt, n, record, facts)`: `.tdd/issue-<n>-<record>` rewritten so each key of `facts` holds its committed source's value, one `record-refreshed` event of `stage` per rewritten key.
- `gain(stage, wt, n, record, key, values, step)`: one `<key>=<value>` line added to `.tdd/issue-<n>-<record>` per value it lacks, for a key a record may hold more than once (step-close's `uncovered_spec`, #4029), one `record-refreshed` event each.
- `read_by(stage, wt, n, step)`: the first stage of `seam_contract.READS[stage]` whose record names `step` by `ledger.same_step`, or `None`.
- `rejected(wt, n, stage, step)`: `(at, values)` of the stage's `<stage>-rejected` wait record when it names `step` by `ledger.same_step`, else `None`, a record naming another step or none removed (S1).
- `record(stage, wt, n, step, facts=())`: the record `read_by` names, its step and each `(key, value)` of `facts` refreshed from their committed sources, one `record-refreshed` event per rewritten key (PRD 038.1 SC1-SC4, SC8); `None`, the `seam=<stage> code=1 reason=record next=seam-settle.sh …` line printed for the first stage it reads, when no record it reads names the step. A missing record is the seam; one that cannot be read raises `OSError` (exit 2).
- `kind(line)`: a `FLAGS:` or `CANDIDATES:` value's class, its first word. `detail(line, last=False)`: what it names after its class, the text after the first `|` (the last with `last`).
- `verdict(wt)`: `(hash, flags)` from one read of `.tdd/verify-refactor.log`: its sha256 (`none` without one), the verdict a refactor-half file was settled after, and its `uncovered-spec` flags as `uncovered_spec=` values; every record naming `verdict_log=` takes both from it (#4029).

## green_half
- `run(n)`: green-half.sh's stage, which `seam-settle.sh green-half` runs through `fused.entry` to finish Green 3 from the wait record a revise.sh PASS re-saved with `revised` (#4551).
- `launch_verdict(where, n, wt, settled, step, values)`: verdict-green's launch, the one set of `run-verdict.sh` arguments green-half.sh and `revise.sh`'s re-verify share (PRD 038.9 RVS13).
- `rerouted_cases(wt, step)`: the cases the step's reroute events name, once each, in journal order, each event's `case` split into its cases, for `revise.sh`'s tests-frozen exemptions.

## red_half
- `refused(step)`: the step kinds of `REFUSED` a step is, whose Red is not red-half's (RH1), ⟦go-red⟧ by `ledger.is_go_red`, each stopping `run-step.sh` before any stage on `seam=none`.
- `launch_verdict(where, n, wt, settled, step, values)`: verdict-red's launch, the one set of `run-verdict.sh` arguments red-half.sh, `revise.sh`'s re-verify and `reroute.sh`'s verify-red share (PRD 038.9 RVS13, PRD 038.10 RRT10).

## seam_contract
- `CONTRACTS`: per record-writing stage (`red-half`, `green-half`, `refactor-half`), the keys of its record the next stage reads that no committed fact holds (PRD 038.1 SC5). `READS`: per reading stage (`green-half`, `revise`, `reroute`, `refactor-half`, `step-close`), the stages whose records it reads, in order (`refactor-half`: `green-half`, then `red-half` for a Green `green-half.sh` did not finish).
- `table()`: the contracts as `script-help.sh seam-settle.sh` prints them.

## pr_finish
- `close(wt, n, url)`: the run's record closed for PR `url` before it is readied: the `⟦full-suite⟧` ticks under `ci`, the `metrics-cut` mark (never `done`, which `pr-finish.sh` writes once CI's first wait is green), the metrics commit, the tree check and the push; `metrics.sh`'s exit code. `LEDGER`, `METRICS`: the ledger and metrics paths, `%s` for the issue.
- `pr_url(wt)`: the PR url read as `DRAFT-PR.md` sub-step 2 reads it, an empty answer a stop with exit 2. `stacked(name, wt, n)`: the run is stacked (`.tdd/issue-<n>-base`), named on stderr.
- `answered(where, ...)`: a git call whose failure is a stop with exit 2 (no answer). `gh_answered(where, ..., wt)`: a gh call whose failure is a stop with exit 2. `dirty(where, wt, left=())`: the changed paths but `left`, a failing `git status` exit 2.

## metrics
- `publish(target, issue, journal, ledger, run)`: writes the `metrics.sh --json` object of the journal at `journal` to `target`, renamed into place from a temporary file beside it; `run` is the run directory whose end, conductor log and pins the fold reads (`None`: the journal alone). `event` calls it for the published metrics file.
- `rendered(issue)`: `(code, report, stderr)` of the markdown report of the working directory's run.

## role_state
- `state_path(tree, role, lane=None)`: `.tdd/role-<role>[-<lane>].state` under `tree`.
- `read_lines(role, lane=None)`: the role's state lines in the main tree, `None` when missing.
- `State(lines)`: the grammar of the state file. `fields()` (every `key=value` line as a dict), `field(name)` (last `name=` value, `None`), `values(name)` (every `name=` value, in file order), `items(*kinds)` (raw item lines), `last_n()`, `timed_ns()` (`(value, expiry)` pairs), `override_numbers()`. A bad line raises `Malformed(kind, line)` (`kind` one of `n-missing`, `n`, `timed-n`, `override`); each caller words it.
- `run_verbs(argv, after_set_n=None)`, `USAGE`: role-state.sh's verbs and its usage line; after a written `set n`, it prints the line `after_set_n(path, n)` returns (role_state_cli's lane budget line).
- `STAMP`: the strftime format of the state file's stamps; reset_cost writes a restart's time in it.

## watch_runs
- `live_conductors()`: the issues whose conductor is live, running per status, starting or pid-filed; dispatch's slot count and role_state_cli's lane need read it.
- `solvable_issues()`: the solvable issues not running, through `solvable-issues.sh --not-running`; a failed read raises `QueueUnreadable`, whose `kind` is `github.refusal_kind` of its stderr.
- `wait()`: one poll interval's sleep.

## plan_publish
- `gh(where, *args, wt)`: one bounded, redacted `gh` call printed as an inner call, raising `Stop` at `where` on any exit but 0; its stdout otherwise.

## run_start
- `preflight_file(n)`: the settled file `preflight.sh` wrote for issue `<n>`, under its worktree when called from the main tree, else under this directory's `.tdd/`.

## status
- `json_document(scope=None, read_states=True)`: `(exit code, --json document)`.
