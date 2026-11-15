# veri/ — interface index

The Python half of veri's scripts: each `<name>.sh` in `skills/tdd/scripts/` is a `/bin/sh` shim that execs
`veri/<name>.py`. Modules import their siblings flat (`import git`, `from ledger import ledger_path`) because they
run as scripts; a module that must also load as `veri.x` uses `try: from x import … except ImportError: from .x import …`.
`entry.run(main, argv)` is the one `__main__` path: it turns an uncaught exception into exit 2. Exit codes 0/1/2/3 are
the API; they are defined in the root `CLAUDE.md`.

This file indexes the **shared modules**: those imported by two or more other modules here. A test
(`tests/py/unit/test_veri_interface_index.py`, a tree audit: `make test` runs it, `make unit` does not) fails when one lacks a section, when a section names a module that is not
shared, when a module reads a sibling's underscore name, or when a module has no docstring. Under each heading are the
names other modules use. Related names share a line where the list would otherwise pass about twelve lines.

## add_ledger_step
- `added_file(path)`: the sibling `-added.md` path of a ledger file.
- `main(argv)`: exit code of add-ledger-step.sh; 2 with the usage on bad arguments.

## blocked_by
- `blockers(body, repo)`: the issue numbers under `## Blocked by`, as `#<n>` or `repo`'s issue URL.
- `add(body, new)`: `body` with `- #<new>` listed under that heading.

## build_verify_prompt
- `build(step_arg, fast_cmd, phase, spec_arg, test_path, …)`: the rendered verifier prompt; a refusal (usage on stderr, exit 2) for bad arguments.
- `INTERFACE_PHASES`: the phases of an interface change (`expand`, `cover-new`, `migrate`, `contract-a`, `contract-b`).
- `expand_includes(text, prompts, chain=())`: `text` with every `{{INCLUDE:x}}` partial inlined; raises `IncludeRefused` for a missing or self-including partial.
- `spec_text_of(path)`: the spec file's bytes, `b""` when unreadable. `has_heading(text, heading)`: whether `## <heading>` is a line of the bytes.
- `refuse(message=None)`: writes the message and the usage to stderr, returns 2.

## candidates
- `KEY`, `LINE`: the `CANDIDATES:` marker and the compiled pattern for the whole line.
- `CLASSES`: the four classes a candidate may name (`structural`, `cosmetic`, `test-only`, `out-of-scope`).
- `candidate(cls)`: a compiled pattern for a `CANDIDATES: <cls> | <text>` line.

## case_reader
- `is_test_file(name)`, `is_test_path(path)`, `is_go_test_file(name)`, `is_js_test_file(name, root="")`: whether a name or path is a Python, Go or JavaScript test file (bool).
- `cut_cases(text)`: `[(case name, source)]` of a test source; raises `UnclosedCase` when a JS call never closes.
- `old_cut_cases_all(text, call_form_only=False)`: the earlier cutter, kept for comparing old and new records.
- `defined_name(case, text, py_file, go_file)`: the def a case name resolves to, `None` if none. `defines_helper(name, text, py_file, go_file)`: bool.
- `live_titles(case, text)`: the titles in `text` that match a JS case, ignoring comments. `js_title_pattern(case)`: that compiled pattern.
- `cut_prefix(case)`: the case with its trailing `…`/`...` cut, `None` when it has none. `strip_param_suffix(name)`: the name without `[param]`.

## ci_on_pr
- `runs_on_pull_requests()`: True when `VERI_CI_ON_PR` is 1 or, unset, a workflow of the current directory triggers on `pull_request`; ValueError carrying the refusal on a bad value.
- `declared()`: `VERI_CI_ON_PR` as `"0"`, `"1"` or `""`; ValueError on anything else.
- `trigger_lines(text)`: generator of the lines of a workflow's `on:` block.

## classify_bail
- `CATEGORIES`: dict from a bail cause to `"system"` or `"process"`; an absent cause is unclassified.

## context_budget
- `START`: the initial `(context, armed)` state.
- `watch(state, lines, budget)`: `(state, readings, exceeded)` after `lines`, stopping at the line that exceeds `budget`.

## context_limits
- `context_limits()`: the list of `claude` options that limit what a veri session loads.

## detach
- `start(argv, stdin, stdout, stderr, xfsz=SIG_IGN)`: starts `argv` as leader of a new session and returns its pid without waiting.

## detect_test_command
- `resolved(tier, issue, root)`: the test command for a tier, `None` when none is found.
- `Answer(command)`: the exception that carries a found command out of the search; `answer_from_file(path, marker)` raises it from a file's lines.

## entry
- `run(main, argv)`: `sys.exit(exit_code(main, argv))`; `--help` prints the module's `USAGE`, an uncaught exception prints one line and exits 2, a broken pipe exits quietly.
- `write(stream, text, *, before=True, after=True, end="\n")`: writes str or bytes to the stream's binary buffer, flushing before and after by default.
- `refusal(main, exc)`: the one-line `<shim>: <Type>: <reason> (at file:line)` text for an exception.
- `silence_stdout()`: points fd 1 at `/dev/null`; ignores failure.
- `refuse(*lines, usage=None, prefix="")`: writes each str/bytes line (prefixed) and then the usage to stderr; returns 2. The one way to refuse.
- `to_contract(code)`: the code when it is 0, 1, 2 or 3, else 2.

## event
- `mark(directory, context, event, fields=(), ts=None)`: appends an event to the run journal; returns 0, or 2 after printing the refusal on any exception.
- `append(directory, context, event, fields=(), ts=None)`: the same without the catch; returns 2 for an empty event name or a bad `structural-pass`.
- `context(environ)`: the run's context fields (issue, step, …) read from an environment.
- `line(args, context, ts, awake)`, `awake_reading()`, `toplevel()`: the JSON line (bytes); the uptime reading (bytes, or an int exit code on a failed clock); the repo top (`""` outside one).
- `journal_path(clone, issue)`: the path of the shared journal, `None` when the clone's config is unreadable. `state_labels(event, issue)`: mirrors a bail, resume or start onto the issue's labels.

## event_log
- `path(run)`: the journal of a run directory, `<run>/.tdd/events.jsonl`.
- `events(run, *kinds, skip_unreadable=False, errors="replace")`: the events of those kinds (all when none), in order; `[]` when the run has no journal; ValueError on an unreadable line unless skipped.
- `last(run, kind)`: the last event of a kind, or `None`.
- `read_events(path, skip_unreadable=False, mark_unreadable=False, errors="replace")`: one dict per non-blank line of an `events.jsonl`; `skip_unreadable` drops lines that are not a JSON object, `mark_unreadable` keeps them as `None`.
- `usage_totals(events)`: `(dollars, tokens)` summed over the `usage` events.
- `append_bytes(path, data)`: appends bytes to a file; raises OSError.
- `run_keeping_journal(run)`: calls `run()` and puts the earlier `.tdd/events.jsonl` content back if it no longer starts with it; returns what `run()` returned.

## extract_result
- `extract(data)`: the text of the last report-bearing `result` record of a stream-json log, newline-terminated; `data` unchanged when it has no result.

## frozen_record
The record of a step's frozen tests (`.tdd/tests-frozen-<key>.record`) and its pass marker.
- `record_path(step)`, `pass_marker_path(step)`, `step_key(step)`: paths under `.tdd/` and the 16-hex key of a step.
- `recorded_cases(step)`: the case names recorded, an empty set when the record is unreadable. `is_marked(records)`: True for a `format: 2` record.
- `body_digest(body)`, `body_line(name, case, body)`, `helpers_line(name, case, digest)`, `case_lines(name, case, body)`, `format_line()`: build record lines.
- `body_record(line)`, `digest_entry(line)`, `helper_records(records)`: parse them (`None` for a line of another kind).
- `write_record(path, out, opener=open)`: True, or False after a stderr message on OSError. `rewrite_records(earlier, rewrite, opener=open)`: rewrites earlier steps' records through `rewrite`.
- `work_tree_hash()`: git tree hash of the work tree outside `.tdd/`, `""` when git fails.
- `write_pass_marker(step, tree)`, `remove_pass_marker(step)`, `pass_marker_current(text)`: write, drop (never raises), and check (bool) the marker against HEAD and the tree.

## full_tier_time
- `main_tree(start)`: the main working tree above `start`. `record_path()`: `<main tree>/.tdd/full-tier-time.json`.
- `read_times(record)`: `{command: seconds}`; ValueError or OSError when the file is not a valid record.

## git
- `git(*args, **kwargs)`: `subprocess.run(["git", *args], **kwargs)`; the CompletedProcess, never raises on a non-zero exit.
- `symref_default(answer)`: the default branch named in `ls-remote --symref` output, `None` when absent.
- `out(*args, cwd=None)`: stdout as str, trailing newlines stripped; raises `GitFailed` on a non-zero exit or a missing git.
- `ok(*args, cwd=None)`: whether the command exited 0; never raises.
- `default_branch(cwd=None, remote=True)`: the default branch name, `None` when it cannot be told; `remote=False` never touches the network. A fallback is the caller's to write.

## github
Every GitHub call goes through `gh`; `VERI_GH_DRIVER` picks the route. A failed call raises `NoAnswer(answer, detail="")`.
- `gh_issue_view(number, field)`, `gh_issue_list(*args)`, `gh_list(path, *args)`, `gh_rest_list(path, empty)`, `gh_json(fixture, path, *args)`, `gh_json_page(...)`: reads; return text, or parsed pages for the `*_list`/`_json` forms.
- `gh_issue_create(title, body, *labels)`, `gh_issue_edit(number, body_file)`, `gh_issue_comment(number, body)`: writes.
- `gh_issue_add_label(number, label)`, `gh_issue_remove_label(number, label)` (a 404 is fine), `gh_label_ensure(label)` (already existing is fine), `gh_label_create(name)`, `gh_api_add_label(path, name)`: label operations.
- `gh_api(path, stderr=None)`, `gh_api_delete(path)`, `gh_probe(*args)`, `run_gh(*args, stderr=None)`: raw `CompletedProcess` results; `run_gh` waits and retries while `gh` is not installed.
- `gh_pr_ready(number, head_sha="")`, `gh_pr_diff_names(number)`: mark a draft PR ready, list the paths of a PR.
- `rate_limit_reset(run=subprocess.run)`: the epoch second the core rate limit resets, `None` when unreadable. `wait_seconds(name, default, least)`: an int tunable, NoAnswer when invalid. `PARKED_HEADING`: the `### ⏸ Parked` heading.

## grade_prose
- `main(argv)`: grades a prose unit and returns an exit code (2 on bad arguments); `--owed` and `--convert` are modes.
- `signature(path, unit)`: the sha256 that stamps a graded unit. `unit_text(unit)`, `read(file)`, `graded_path(unit)`: the unit's text, a file's text, its `GRADED` file path.
- `modern_python_dir()`: the PATH directory holding a Python 3.12+ `python3` plus a trailing separator, `""` when none.

## growth
- `growth(records, baseline=None)`: tokens of context a session grew since its first usage record (or `baseline`), `None` when it has none.

## issue_worktree
- `remote_issue_branch(issue)`: the `origin` branch named `<issue>-*`, `""` when none, `None` when `ls-remote` fails.
- `ancestors()`: the pids from this process up to pid 1.

## js_tests
- `CALL`: regular-expression source that matches the opening of a JS `it(`/`test(` call.

## json_documents
- `documents(text, strict=True)`: the JSON documents in `text`, in order; raises `json.JSONDecodeError` on a malformed one.
- `items(text, strict=True)`: the elements of every document, as one list.

## launch_floor
- `bash_refusal(prefix)`: 0 when bash is 5+, else writes the refusal to stderr and returns its exit code.
- `python_refusal(prefix)`: the same for the Python floor. `python_floor()`: the floor as `major.minor` read from `lib/venv-python.sh`.

## leaf
- `launch(name, prompt, *args, env=None)`: runs the leaf through `supervise.sh`; the CompletedProcess with stdout captured.

## leaf_log
- `result_records(lines)`: every `{"type":"result", …}` record among a leaf log's lines, in order.

## leaf_model
- `resolve(name)`: the model for a leaf, `None` when the name is invalid or the model has whitespace (message on stderr).
- `leaf_model(name)`: the same as a string; `""` where `resolve` gives `None`.
- `env_value(key)`: the tunable's value, `""` when unset or only whitespace.

## leaf_role
- `leaf_role(name)`: dict of `VERI_ACTOR`, `VERI_PHASE`, `VERI_ATTEMPT`; `None` after a stderr message for a bad name.
- `is_revise(name)`: True for `revise-*` and `develop-exhausted`.

## ledger
The ledger is a checkbox list; steps carry `⟦…⟧` markers and `⟂` phase marks.
- Reading: `read_ledger(path)`, `read_ledger_stdin()` (text; OSError), `decode_ledger(data)`, `ledger_items(text)`, `ledger_steps(text)` (records of `(index, state, kind, pending, added, criterion, text)`), `items_at(rev, path)` (OSError when git cannot show it).
- Writing: `replace_ledger(path, data)` (OSError), `rewrite_ledger(path, text)` (None on success), `ledger_tick(text, matcher, pending=False)`, `ledger_mark_phase(text, matcher, phase, owed=False)` (ValueError when the step lacks the phase), `ledger_clear_pending(text, matcher)`: the last three return `(changed, text)`.
- A step: `listed_phases`, `next_phase`, `unphased`, `trailing_markers`, `unit_of` (str/list/None), `carries_mark(text, name)`, `is_added`, `is_human_owed`, `is_skill_edit`, `handed_out(record)`: predicates and parts of its text.
- Building and checking: `new_step(text, criterion)`, `multi_tag_refusal(steps)` (`""` if fine), `receipt_refusal(ledger_file)`, `ledger_path(run_dir, issue)`.
- Constants: `STEP_RE`, `ITEM_RE`, `KIND_RE`, `CRITERION_RE`, `CRITERION_TAG`, `ADDED_MARK`, `PENDING_MARK`, `OPEN_STEP`, `TICKED_STEP`.

## markdown_sections
- `fenced_lines(text)`: a list of bools, True for each line inside a code fence (fence lines included).
- `section(text, heading, bare=False)`: the lines from `heading` to the next heading of the same or higher level; raises StopIteration when `heading` is absent.

## paths
- `scripts_of(file)`: the `scripts/` directory above a file of `veri/`, `..` resolved after following symlinks.
- `resolved_scripts_of(file)`: the same with the file's symlinks resolved first.
- `inside_scripts(file, where=None)`: whether `where` (default: the current directory) is that scripts directory or inside it.

## pid_file
- `number_in(file)`: the number on a pid file's first line, `None` when missing or malformed.
- `live_conductor(path)`: the pid of the live conductor recorded in `path`, else `None`; `not_live_reason(path)` says why. `recorded_alive(path)`, `recorded_started(path)`, `start_recorded(file)`, `start_matches(file, pid)`: parts of that check. `record(path, pid)` writes a pid file.
- `conductors()`: `[(pid, issue)]` of running `run_conductor.py` processes from `ps`. `conductor_processes()`, `starting_runs(root)`, `runs_with_directory(root)`: issues of running conductors by tree.
- `ps_field(field, pid)`: a `ps` column, `None` when the pid is gone. `cwd_of(pid)` (via `lsof`), `is_inside(cwd, root)`, `detached(pid)`, `supervising(pid, name)`: probes of a process.

## pinned_scripts
- `make_snapshot()`: a new empty snapshot directory. `write_snapshot_marker(snapshot, worktree)`: names its worktree.
- `snapshot_gone(recorded)`, `snapshot_made_for(recorded, worktree)`: bool checks of a recorded path.

## popen_command
- `command_words(args)`: the argv list a `Popen` `args` names. `command_basename(args)`: the first word's basename, `""` for none.

## preserve_attempt
- `preserve(repo, issue, step, phase, attempt, mark="", env=None)`: saves the work tree as a commit under `refs/veri/attempts/…` without touching the branch; returns 0, 1 (stderr message) when the ref or leaf files cannot be written, or a failed git step's code.

## prose_owed
- `owed_listed(path="REQUIREMENTS.md")`: `(owed, orphans)`, with `owed` the `(list, unit)` pairs whose graded signature is stale.

## renamed_case
- `renamed_to(name, old_source, new_source, taken)`: the case of `new_source` with the same text as `name` but another name, else `None`.
- `renamed_and_changed_to(name, old_source, new_source, taken)`: the case with the same def line but another name and a changed body.

## replaces_case
- `parse(step)`: `(case names, suite)` of the clause, `None` when unreadable.
- `is_replaces_case_step(step)`: bool. `quote_of(step)`: the quote character of its names. `refusal(step)`: the reason a step's clause is malformed, `None` when fine.

## report
- `report_read(text, keys, *, optional_space=False, terminated_only=False)`: `{key: value}` for the `KEY: value` lines of a leaf report.

## requirements
- `lists(path="REQUIREMENTS.md")`: the REQUIREMENTS.md files that exist. `tracked(name)`: git-tracked files of that name; RuntimeError when `git ls-files` fails.
- `listed_units(path)`, `claims(path, unit)`: the units a list names; a unit's rows as `<id>\t<requirement>` lines (ValueError `path:line: reason` on a malformed table).
- `read_lines(path)`, `requirements_lines(lines)`: a file's lines; `(heading, line)` pairs of its `## Requirements` section.
- `split_cells(line)`, `table_cells(line)`: a table row's cells. `well_formed_row_id(row_id)`: bool. `malformed_row_id(lines)`: the first bad id, `None` when fine.

## role_state
- `state_path(tree, role, lane=None)`: `.tdd/role-<role>[-<lane>].state` under `tree`. `read(path)`: text, `None` when missing.
- `append(path, text)`, `now()`: append (written through a temp file and renamed); the stamp. `refusal(path, lines, stamp)`: why a reset request is refused, `None` when allowed.

## run_activity
- `activity(run, closed=False)`: an `Activity` (frozen dataclass: `state`, `detail`, `phase`, `actor`, `leaf`, `elapsed_seconds`, `attempts`, `dollars`, `tokens`, `pr`, `bail_phase`, `classification`, `stop_mode`, `cause`) for the run directory; `state` is one of `running`, `stale`, `done`, `stopped`, `bailed`, `refused`, `closed`.
- `state(run)`: just that state word. No journal reads as `running`; a dead pid with no end mark is `stale`.

## run_dir
Where a run lives on disk; the module docstring draws the layout. Paths are str and nothing but `main_tree` touches the disk.
- `main_tree(cwd=None, *, missing=)`: the repository's main working tree; when git cannot name one it raises `NoMainTree`, or returns `missing` (any value, `""` included) if the caller gave one.
- `main_file(main, name)`: `<main>/.tdd/<name>`. `worktrees(main)`: `<main>/.tdd/wt`. `worktree(main, issue)`: the run of an issue.
- `run_file(run, name)`: `<run>/.tdd/<name>`. `issue_file(run, issue, suffix="")`: `<run>/.tdd/issue-<n><suffix>`. `ledger(run, issue)`: the run's ledger.

## run_end
- `run_end(run_dir)`: `(ended, cause, standing mark)` for a run, from its events.
- `latest_result(path)`: `(launched, latest result record or None)` of a conductor log. `conductor_log(run_dir, issue)`: its path.

## run_verdict
- `SCRIPTS`: the scripts directory. `takes_a_value(word)`: True for the options `--step`, `--fast-cmd`, `--supersede-base`.

## session_env
- `strip_session_env(env)`: removes the Claude Code session variables, and values carrying a session id, from `env`.

## skill_edit_guard
- `main(argv)`: exit code of skill-edit-guard.sh, 2 on a bad base or a missing unit. `list_path(unit)`: the unit's `REQUIREMENTS.md`.

## solvable_issues
- `solvable(label, priority="priority", repo=None)`: `(exit code, issue numbers)` in selection order; code 2 when the listing is unreadable.
- `solvable_in_scope()`: the same for the configured scope. `priority_label()`: the label, `None` when set but empty.

## status
- `json_document(scope=None, read_states=True)`: `(exit code, --json document)`. `run_activity(run, as_json=False, closed=False)`: renders one run's `run_activity.activity` as its text line or `--json` object.
- `read_role_state(role, lane=None)`: the role's state lines, `None` when missing.

## stop_modes
- `STOP_MODES`: `("at-ledger", "at-leaf", "now")`. `stop_mode_known(mode)`: bool. `modes_named()`: the modes as a phrase.

## suite_mode
- `run(script, variable)`: prints `ci` or `local` and returns 0; 2 with a message on a bad knob or a bad `VERI_CI_ON_PR`.

## tests_frozen
- `differing_tests()`: test files changed against HEAD; raises OSError when git cannot list.
- `is_diff_checked(line)`: bool for a `⟦diff-checked⟧` step. `rerecord_earlier(ledger, step)`, `rerecord_committed(step, root)`: re-record earlier steps' frozen cases; `rerecord_earlier` returns 3 for a step that is not diff-checked, 2 on an unreadable ledger or outside a repo.

## timed_n_format
- `parse(text)`: `(n, expiry epoch)` from `<n> until <ISO-8601>`; ValueError when malformed.

## tunables
The one reader of `VERI_*` and related environment variables.
- `read(name, default="", unless_empty=None)`: the value as a string. `read_bytes(name, default=b"")`: as bytes.
- `resolve(name)`: `(value, None)`, or `(None, (raw, must_be))` for a bad value; the typed `TABLE` entries only. `TABLE`: name to `Tunable(parser, default, must_be)`. `tokens(raw)`: int, ValueError otherwise.
- One default per name: a name in `TABLE` (refusing readers, one-line refusal) or `DEFAULTED` (readers keep their own refusal text: the budgets, the model knobs, `VERI_LABEL`, `VERI_DISPATCH_RETRY_SLEEP`, `VERI_GH_REFUSAL_RETRIES`, ...) states its default and parse once. `default(name)`, `parses(name, raw)`, `get(name, unless_empty=False)` (the default when unset; `unless_empty=True` also when set but empty), `set_but_empty(name)`. A reader of such a name passes no literal default: `test_tunable_defaults_audit.py` fails when one does, bar the exemptions it lists by name (`VERI_NO_VERDICT_RETRIES` in `verify.py`/`grade_prose.py`, whose parses of `010` disagree; `VERI_LABEL` in `status.py`). A name read at two defaults (`VERI_POLL`, `VERI_MISSING_REROUTE_BUDGET`) is in neither table.
- `environment()`, `with_values(**values)`, `without(name)`, `pop(name, default="")`: a copy of the environment, with values set or removed; pop mutates it.
- `lane_of(opt_in)`: the lane of a label, `None` for a plain one. `taken_label(opt_in)`: `taken:<lane or main>`. `venv_dir()`: `VERI_VENV` or `~/.veri-tools/venv`.
