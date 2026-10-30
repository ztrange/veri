"""In-process cases for veri/fast_tier_guard.py, the fast tier's admission-bar guard."""
import functools
import importlib

import pytest

from conftest import SCRIPTS


def test_a_planted_test_file_starting_a_process_through_subprocess_is_named_by_file_and_line_and_a_clean_one_is_not(tmp_path):
    guard = importlib.import_module("veri.fast_tier_guard")
    offender = tmp_path / "test_offender.py"
    offender.write_text(
        "import subprocess\n"
        "\n"
        "def test_runs_a_process():\n"
        "    subprocess.run(['true'])\n"
    )
    clean = tmp_path / "test_clean.py"
    clean.write_text("def test_adds():\n    assert 1 + 1 == 2\n")

    found = guard.offences(tmp_path)

    assert [line.split(": ")[0] for line in found] == [f"{offender}:4"]


def test_a_planted_test_file_starting_a_process_through_an_imported_name_or_an_aliased_module_is_named_by_file_and_line(tmp_path):
    guard = importlib.import_module("veri.fast_tier_guard")
    imported = tmp_path / "test_imported_name.py"
    imported.write_text(
        "from subprocess import run\n"
        "\n"
        "def test_runs_a_process():\n"
        "    run(['true'])\n"
    )
    aliased = tmp_path / "test_aliased_module.py"
    aliased.write_text(
        "import subprocess as sp\n"
        "\n"
        "def test_runs_a_process():\n"
        "    sp.run(['true'])\n"
    )

    found = guard.offences(tmp_path)

    assert sorted(line.split(": ")[0] for line in found) == [f"{aliased}:4", f"{imported}:4"]


def test_a_planted_test_file_starting_a_process_through_os_system_os_exec_os_spawn_or_pty_is_named_by_file_and_line(tmp_path):
    guard = importlib.import_module("veri.fast_tier_guard")
    forms = {
        "test_os_system.py": ("os", "os.system('true')"),
        "test_os_exec.py": ("os", "os.execv('/bin/true', ['true'])"),
        "test_os_spawn.py": ("os", "os.spawnl(os.P_WAIT, '/bin/true', 'true')"),
        "test_pty.py": ("pty", "pty.spawn(['true'])"),
    }
    planted = []
    for name, (module, call) in forms.items():
        path = tmp_path / name
        path.write_text(
            f"import {module}\n"
            "\n"
            "def test_runs_a_process():\n"
            f"    {call}\n"
        )
        planted.append(f"{path}:4")

    found = guard.offences(tmp_path)

    assert sorted(line.split(": ")[0] for line in found) == sorted(planted)


@pytest.mark.parametrize(
    "import_line, call, named",
    [
        ("from os import system", "system('true')", "os.system"),
        ("import os as o", "o.system('true')", "os.system"),
        ("from pty import spawn", "spawn(['true'])", "pty.spawn"),
        ("import os", "os.popen('true')", "os.popen"),
        ("import os", "os.posix_spawn('/bin/true', ['true'], {})", "os.posix_spawn"),
    ],
)
def test_1641_a_planted_process_start_form_is_named_by_file_and_line_and_the_message_names_the_actual_call(tmp_path, import_line, call, named):
    guard = importlib.import_module("veri.fast_tier_guard")
    offender = tmp_path / "test_offender.py"
    offender.write_text(
        f"{import_line}\n"
        "\n"
        "def test_runs_a_process():\n"
        f"    {call}\n"
    )

    found = guard.offences(tmp_path)

    assert [line.split(": ")[0] for line in found] == [f"{offender}:4"]
    message = found[0].split(": ", 1)[1]
    assert named in message
    assert "through subprocess" not in message


def test_a_planted_test_file_calling_time_sleep_is_reported_as_a_sleep_offence_by_file_and_line(tmp_path):
    guard = importlib.import_module("veri.fast_tier_guard")
    offender = tmp_path / "test_sleeper.py"
    offender.write_text(
        "import time\n"
        "\n"
        "def test_waits():\n"
        "    time.sleep(1)\n"
    )

    found = guard.offences(tmp_path)

    assert [line.split(": ")[0] for line in found] == [f"{offender}:4"]
    assert "sleep" in found[0].split(": ", 1)[1]


def test_a_planted_test_file_opening_a_socket_is_reported_as_a_socket_offence_by_file_and_line(tmp_path):
    guard = importlib.import_module("veri.fast_tier_guard")
    offender = tmp_path / "test_networker.py"
    offender.write_text(
        "import socket\n"
        "\n"
        "def test_connects():\n"
        "    socket.create_connection(('localhost', 1))\n"
    )

    found = guard.offences(tmp_path)

    assert [line.split(": ")[0] for line in found] == [f"{offender}:4"]
    assert "socket" in found[0].split(": ", 1)[1]


def test_a_planted_test_file_opening_a_socket_or_sleeping_through_an_imported_name_or_an_aliased_module_is_reported_by_file_and_line(tmp_path):
    guard = importlib.import_module("veri.fast_tier_guard")
    forms = {
        "test_socket_imported.py": ("from socket import socket", "socket(), 'socket'"),
        "test_socket_aliased.py": ("import socket as s", "s.socket(), 'socket'"),
        "test_sleep_imported.py": ("from time import sleep", "sleep(1), 'sleep'"),
    }
    planted = {}
    for name, (import_line, call) in forms.items():
        path = tmp_path / name
        path.write_text(
            f"{import_line}\n"
            "\n"
            "def test_it():\n"
            f"    {call.split(', ')[0]}\n"
        )
        planted[f"{path}:4"] = call.split(", ")[1].strip("'")

    found = guard.offences(tmp_path)

    assert sorted(line.split(": ")[0] for line in found) == sorted(planted)
    for line in found:
        location, message = line.split(": ", 1)
        assert planted[location] in message


def test_a_planted_test_file_running_another_suite_through_pytest_main_or_a_named_suite_path_is_reported_as_a_nested_suite_by_file_and_line(tmp_path):
    guard = importlib.import_module("veri.fast_tier_guard")
    forms = {
        "test_pytest_main.py": ("import pytest", "pytest.main(['other'])"),
        "test_named_py_suite.py": ("", "run_it('tests/py/test_other.py')"),
        "test_named_sh_suite.py": ("", "run_it('tests/other.test.sh')"),
    }
    planted = []
    for name, (import_line, call) in forms.items():
        path = tmp_path / name
        path.write_text(
            f"{import_line}\n"
            "\n"
            "def test_it():\n"
            f"    {call}\n"
        )
        planted.append(f"{path}:4")

    found = guard.offences(tmp_path)

    assert sorted(line.split(": ")[0] for line in found) == sorted(planted)
    for line in found:
        assert "nested" in line.split(": ", 1)[1]


def test_1641_a_planted_test_file_passing_a_suite_path_as_a_keyword_argument_is_reported_as_a_nested_suite_by_file_and_line(tmp_path):
    guard = importlib.import_module("veri.fast_tier_guard")
    path = tmp_path / "test_keyword_suite.py"
    path.write_text(
        "def test_it():\n"
        "    run_it(path='tests/py/test_other.py')\n"
    )

    found = guard.offences(tmp_path)

    assert [line.split(": ")[0] for line in found] == [f"{path}:2"]
    assert "nested" in found[0].split(": ", 1)[1]


def test_2170_a_planted_test_file_only_building_a_path_object_from_a_test_file_name_is_not_reported_as_a_nested_suite(tmp_path):
    guard = importlib.import_module("veri.fast_tier_guard")
    (tmp_path / "test_path_only.py").write_text(
        "import pathlib\n"
        "\n"
        "def test_it():\n"
        "    assert pathlib.Path('test_planted.py').name == 'test_planted.py'\n"
    )

    assert guard.offences(tmp_path) == []


def test_an_offence_whose_file_and_line_the_exemption_table_lists_with_a_reason_is_not_reported_and_an_entry_with_an_empty_reason_is_refused_by_name(tmp_path):
    import pytest

    guard = importlib.import_module("veri.fast_tier_guard")
    exempt = tmp_path / "test_exempt.py"
    other = tmp_path / "test_other.py"
    for path in (exempt, other):
        path.write_text(
            "import time\n"
            "\n"
            "def test_waits():\n"
            "    time.sleep(1)\n"
        )

    found = guard.offences(tmp_path, {f"{exempt}:4": "waits on a fake clock"})

    assert [line.split(": ")[0] for line in found] == [f"{other}:4"]
    with pytest.raises(ValueError, match=f"{exempt}:4"):
        guard.offences(tmp_path, {f"{exempt}:4": ""})


def test_1641_an_exemption_keyed_by_a_path_relative_to_the_root_suppresses_its_offence_in_whatever_directory_the_tree_lives(tmp_path):
    guard = importlib.import_module("veri.fast_tier_guard")
    roots = [tmp_path / "mac" / "py", tmp_path / "ci" / "elsewhere" / "py"]
    for root in roots:
        (root / "unit").mkdir(parents=True)
        (root / "unit" / "test_waits.py").write_text("import time\n\ndef test_waits():\n    time.sleep(1)\n")

    found = [guard.offences(root, {"unit/test_waits.py:4": "waits on a fake clock"}) for root in roots]

    assert found == [[], []]


def test_1641_an_exemption_keyed_relative_to_tests_py_silences_its_offence_and_is_not_stale_over_the_tree_and_over_its_unit_subdirectory(tmp_path):
    guard = importlib.import_module("veri.fast_tier_guard")
    (tmp_path / "unit").mkdir()
    (tmp_path / "unit" / "test_waits.py").write_text("import time\n\ndef test_waits():\n    time.sleep(1)\n")
    exemptions = {"unit/test_waits.py:4": "waits on a fake clock"}

    found = [guard.offences(root, exemptions) for root in (tmp_path, tmp_path / "unit")]

    assert found == [[], []]


def test_1641_an_exemption_silences_only_the_offence_on_the_line_it_names_in_a_file_with_two(tmp_path):
    guard = importlib.import_module("veri.fast_tier_guard")
    waits = tmp_path / "test_waits.py"
    waits.write_text("import time\n\ndef test_waits():\n    time.sleep(1)\n    time.sleep(2)\n")

    found = guard.offences(tmp_path, {"test_waits.py:4": "waits on a fake clock"})

    assert [line.split(": ")[0] for line in found] == [f"{waits}:5"]


def test_1641_an_exemption_entry_whose_reason_is_only_whitespace_is_refused_by_name(tmp_path):
    guard = importlib.import_module("veri.fast_tier_guard")
    (tmp_path / "test_waits.py").write_text("import time\n\ndef test_waits():\n    time.sleep(1)\n")

    with pytest.raises(ValueError, match="test_waits.py:4"):
        guard.offences(tmp_path, {"test_waits.py:4": " \t\n"})


@pytest.mark.parametrize("reason", [None, 7, "", "  \t\n"], ids=["none", "number", "empty", "whitespace"])
def test_1641_an_exemption_entry_whose_reason_is_not_a_non_empty_string_is_refused_by_name(tmp_path, reason):
    guard = importlib.import_module("veri.fast_tier_guard")
    (tmp_path / "test_waits.py").write_text("import time\n\ndef test_waits():\n    time.sleep(1)\n")

    with pytest.raises(ValueError, match="test_waits.py:4"):
        guard.offences(tmp_path, {"test_waits.py:4": reason})


def test_1641_an_exemption_entry_that_matches_no_file_under_the_root_makes_the_guard_fail_naming_that_entry(tmp_path):
    guard = importlib.import_module("veri.fast_tier_guard")
    (tmp_path / "test_clean.py").write_text("def test_clean():\n    assert True\n")

    with pytest.raises(ValueError, match="unit/test_gone.py:4"):
        guard.offences(tmp_path, {"unit/test_gone.py:4": "waits on a fake clock"})


@functools.lru_cache(maxsize=None)
def _sweep(directory):
    """`guard.offences` over a real `directory` under no table, run once per session."""
    guard = importlib.import_module("veri.fast_tier_guard")
    return tuple(guard.offences(directory, {}))


def _under(directory, table):
    """`_sweep(directory)` judged against `table` as `guard.offences(directory, table)` would, without sweeping again."""
    guard = importlib.import_module("veri.fast_tier_guard")
    root, _ = guard._discover(directory, table)
    return [line for line in _sweep(directory) if not guard._exempt(line, root, table)]


def _real_table_audit(tmp_path):
    """The planted offences under `tmp_path`, by file and line, and the committed fast tier's offences under the real table.

    The scratch tree is judged against no table: the real one is keyed to files under tests/py/, and its stale check
    would refuse every entry over a tree that holds only the planted offender.
    """
    guard = importlib.import_module("veri.fast_tier_guard")
    offender = tmp_path / "test_offender.py"
    offender.write_text(
        "import time\n"
        "\n"
        "def test_waits():\n"
        "    time.sleep(1)\n"
    )

    planted = guard.offences(tmp_path, {})
    committed = _under(SCRIPTS / "tests" / "py" / "unit", guard.EXEMPTIONS)

    return [line.split(": ")[0] for line in planted], committed


@pytest.mark.tree_audit("every test_*.py under skills/tdd/scripts/tests/py/unit")
def test_the_guard_with_the_real_exemption_table_finds_no_offence_in_the_fast_tier_as_committed_and_names_a_planted_one_by_file_and_line(tmp_path):
    assert _real_table_audit(tmp_path) == ([f"{tmp_path / 'test_offender.py'}:4"], [])


@pytest.mark.tree_audit("every test_*.py under tests/py and tests/py/unit")
def test_1641_a_real_exemption_keyed_relative_to_tests_py_is_not_reported_stale_by_any_case_that_reads_the_real_table(tmp_path, monkeypatch):
    guard = importlib.import_module("veri.fast_tier_guard")
    assert (SCRIPTS / "tests" / "py" / "unit" / "test_add_ledger_step.py").is_file()
    monkeypatch.setattr(guard, "EXEMPTIONS", {"unit/test_add_ledger_step.py:1": "planted: a real-keyed entry no case may report stale"})

    assert (_real_table_audit(tmp_path), _misplaced(SCRIPTS / "tests" / "py")) == (([f"{tmp_path / 'test_offender.py'}:4"], []), [])


def test_the_shared_sweep_runs_guard_offences_once_per_real_directory_however_often_the_cases_request_it(monkeypatch, request):
    guard = importlib.import_module("veri.fast_tier_guard")
    swept = []
    monkeypatch.setattr(guard, "offences", lambda directory, table: swept.append(directory) or [])
    _sweep.cache_clear()
    request.addfinalizer(_sweep.cache_clear)
    tier = SCRIPTS / "tests" / "py"

    for directory in (tier / "unit", tier, tier / "unit", tier, tier / "unit"):
        _sweep(directory)

    assert sorted(swept) == sorted({tier, tier / "unit"})


def test_a_root_that_does_not_exist_is_refused_with_exit_2_and_a_stderr_line_naming_the_path_instead_of_reporting_no_offences(tmp_path, run_cli):
    guard = importlib.import_module("veri.fast_tier_guard")
    missing = tmp_path / "no-such-tier"

    code, stdout, stderr = run_cli(guard, [str(missing)])

    assert (code, stdout, str(missing) in stderr) == (2, "", True)


def test_offences_raises_instead_of_returning_an_empty_list_when_its_root_does_not_exist(tmp_path):
    guard = importlib.import_module("veri.fast_tier_guard")
    missing = tmp_path / "no-such-tier"

    with pytest.raises(Exception):
        guard.offences(missing)


def test_the_guards_command_line_on_a_missing_root_exits_2_with_the_refusal_line_offences_raising_produces_and_nothing_on_stdout(tmp_path, run_cli):
    guard = importlib.import_module("veri.fast_tier_guard")
    missing = tmp_path / "no-such-tier"

    code, stdout, stderr = run_cli(guard, [str(missing)])

    assert (code, stdout, len(stderr.splitlines()), stderr.startswith(f"fast-tier-guard.sh: NotADirectoryError: {missing}: no such directory")) == (2, "", 1, True)


def test_the_guards_command_line_prints_a_planted_offence_by_file_and_line_and_exits_1_and_exits_0_only_on_a_readable_root_with_none(tmp_path, run_cli):
    guard = importlib.import_module("veri.fast_tier_guard")
    dirty = tmp_path / "dirty"
    dirty.mkdir()
    offender = dirty / "test_offender.py"
    offender.write_text("import time\n\ndef test_waits():\n    time.sleep(1)\n")
    clean = tmp_path / "clean"
    clean.mkdir()
    (clean / "test_clean.py").write_text("def test_adds():\n    assert 1 + 1 == 2\n")

    dirty_code, dirty_out, _ = run_cli(guard, [str(dirty)])
    clean_code, clean_out, _ = run_cli(guard, [str(clean)])

    assert (dirty_code, dirty_out.startswith(f"{offender}:4: "), clean_code, clean_out) == (1, True, 0, "")



def test_a_root_that_is_a_regular_file_is_refused_by_offences_and_by_the_command_line_with_exit_2_naming_the_path(tmp_path, run_cli):
    guard = importlib.import_module("veri.fast_tier_guard")
    root = tmp_path / "tier"
    root.write_text("not a directory\n")

    with pytest.raises(NotADirectoryError):
        guard.offences(root)
    code, stdout, stderr = run_cli(guard, [str(root)])

    assert (code, stdout, str(root) in stderr) == (2, "", True)


def test_the_guards_command_line_prints_every_offence_by_file_and_line_and_exits_1(tmp_path, run_cli):
    guard = importlib.import_module("veri.fast_tier_guard")
    first = tmp_path / "test_a.py"
    first.write_text("import time\n\ndef test_waits():\n    time.sleep(1)\n")
    second = tmp_path / "test_b.py"
    second.write_text("import time\n\n\ndef test_waits():\n    time.sleep(1)\n")

    code, stdout, _ = run_cli(guard, [str(tmp_path)])

    assert (code, [line.split(": ")[0] for line in stdout.splitlines()]) == (1, [f"{first}:4", f"{second}:5"])

FROZEN_OUTSIDE_THE_TIER = ("test_events_jsonl_openers.py", "test_events_jsonl_openers_shapes.py",
                          "test_skill_refactor_readers.py", "test_skill_phased_readers.py",
                          "test_prose_listing_single_source.py")


def _misplaced(tier):
    """Criterion 1's placement rule over `tier` and its `unit/`, judged against no exemption table."""
    guard = importlib.import_module("veri.fast_tier_guard")
    named = {line.split(":")[0] for line in (_sweep(tier) if tier.is_relative_to(SCRIPTS) else guard.offences(tier, {}))}
    files = sorted(tier.glob("test_*.py")) + sorted((tier / "unit").glob("test_*.py"))
    return [
        f"{path.relative_to(tier)}: {'named by the guard, inside the tier' if str(path) in named else 'guard-clean, outside the tier'}"
        for path in files
        if (str(path) in named) == (path.parent.name == "unit")
        and str(path.relative_to(tier)) not in FROZEN_OUTSIDE_THE_TIER
    ]


@pytest.mark.tree_audit("every test_*.py under tests/py and tests/py/unit")
def test_every_guard_clean_pytest_file_lives_under_tests_py_unit_and_every_file_the_guard_names_stays_outside_it():
    assert _misplaced(SCRIPTS / "tests" / "py") == []


def test_the_placement_audit_still_names_an_offending_file_inside_the_tier_that_the_exemption_table_lists(tmp_path, monkeypatch):
    guard = importlib.import_module("veri.fast_tier_guard")
    (tmp_path / "unit").mkdir()
    offender = tmp_path / "unit" / "test_waits.py"
    offender.write_text("import time\n\ndef test_waits():\n    time.sleep(1)\n")
    monkeypatch.setattr(guard, "EXEMPTIONS", {f"{offender}:4": "planted: the audit must ignore this"})

    assert guard.offences(tmp_path, guard.EXEMPTIONS) == []
    assert _misplaced(tmp_path) == ["unit/test_waits.py: named by the guard, inside the tier"]


def test_the_veri_coord_and_veri_dev_lane_prose_suites_live_under_tests_py_unit_and_not_beside_it():
    tier = SCRIPTS / "tests" / "py"
    names = ("test_veri_coord_lane.py", "test_veri_dev_lane.py")
    assert [(name, (tier / name).is_file(), (tier / "unit" / name).is_file()) for name in names] == [
        (name, False, True) for name in names
    ]


def test_1668_the_comment_class_suite_whose_only_suite_looking_strings_are_prose_labels_lives_under_tests_py_unit_and_not_beside_it():
    tier = SCRIPTS / "tests" / "py"
    name = "test_comment_class.py"
    assert ((tier / name).is_file(), (tier / "unit" / name).is_file()) == (False, True)


def test_the_f9_prompt_retirements_suite_whose_cases_start_no_process_lives_under_tests_py_unit_and_not_beside_it():
    tier = SCRIPTS / "tests" / "py"
    name = "test_f9_prompt_retirements.py"
    assert ((tier / name).is_file(), (tier / "unit" / name).is_file()) == (False, True)


def test_1874_a_planted_test_file_building_a_subprocess_completed_process_is_not_reported_as_starting_a_process(tmp_path):
    guard = importlib.import_module("veri.fast_tier_guard")
    (tmp_path / "test_fake_result.py").write_text(
        "import subprocess\n"
        "\n"
        "def test_fakes_a_result():\n"
        "    return subprocess.CompletedProcess(['true'], 0)\n"
    )

    assert guard.offences(tmp_path) == []


def test_1668_a_planted_test_file_calling_pytest_main_with_a_list_naming_a_test_file_is_still_reported_as_running_a_nested_suite_by_file_and_line(tmp_path):
    guard = importlib.import_module("veri.fast_tier_guard")
    offender = tmp_path / "test_offender.py"
    offender.write_text(
        "import pytest\n"
        "\n"
        "def test_runs_a_suite():\n"
        "    pytest.main(['tests/py/test_other.py', '-q'])\n"
    )

    found = guard.offences(tmp_path)

    assert found == [f"{offender}:4: runs a nested suite"]


def test_1668_a_planted_test_file_calling_run_cli_with_an_argument_list_naming_a_test_file_is_still_reported_as_running_a_nested_suite_by_file_and_line(tmp_path):
    guard = importlib.import_module("veri.fast_tier_guard")
    offender = tmp_path / "test_offender.py"
    offender.write_text(
        "def test_runs_a_suite(run_cli):\n"
        "    run_cli('veri.runner', ['tests/py/test_other.py', '-q'])\n"
    )

    found = guard.offences(tmp_path)

    assert found == [f"{offender}:2: runs a nested suite"]


def test_1668_a_planted_test_file_calling_subprocess_run_with_arguments_naming_a_test_file_is_still_reported_by_file_and_line(tmp_path):
    guard = importlib.import_module("veri.fast_tier_guard")
    offender = tmp_path / "test_offender.py"
    offender.write_text(
        "import subprocess\n"
        "\n"
        "def test_runs_a_suite():\n"
        "    subprocess.run(['bash', 'tests/foo.test.sh'])\n"
    )

    found = guard.offences(tmp_path)

    assert [line.split(": ")[0] for line in found] == [f"{offender}:4"]


def test_1668_a_planted_test_file_calling_os_exec_with_arguments_naming_a_test_file_is_still_reported_by_file_and_line(tmp_path):
    guard = importlib.import_module("veri.fast_tier_guard")
    offender = tmp_path / "test_offender.py"
    offender.write_text(
        "import os\n"
        "\n"
        "def test_runs_a_suite():\n"
        "    os.execv('/bin/bash', ['bash', 'tests/foo.test.sh'])\n"
    )

    found = guard.offences(tmp_path)

    assert [line.split(": ")[0] for line in found] == [f"{offender}:4"]


def test_1668_a_planted_test_file_whose_only_call_passing_a_suite_named_string_is_to_a_function_it_defines_is_not_reported_as_running_a_nested_suite_while_an_undefined_run_it_is(tmp_path):
    guard = importlib.import_module("veri.fast_tier_guard")
    (tmp_path / "test_helper_call.py").write_text(
        "def says(label):\n"
        "    return label\n"
        "\n"
        "def test_names_a_path_in_prose():\n"
        "    says('that tests live in tests/py/test_<module>.py')\n"
        "    says('tests/foo.test.sh')\n"
    )
    offender = tmp_path / "test_undefined.py"
    offender.write_text(
        "def test_runs_a_suite():\n"
        "    run_it('tests/py/test_other.py')\n"
        "    run_it(path='tests/foo.test.sh')\n"
    )

    found = guard.offences(tmp_path)

    assert found == [f"{offender}:2: runs a nested suite", f"{offender}:3: runs a nested suite"]


def test_1668_a_planted_test_file_whose_only_call_passing_a_suite_named_string_is_to_an_imported_assertion_helper_is_not_reported_as_running_a_nested_suite(tmp_path):
    guard = importlib.import_module("veri.fast_tier_guard")
    (tmp_path / "test_assert_helper.py").write_text(
        "from shared import assert_says\n"
        "\n"
        "def test_names_a_path_in_prose():\n"
        "    assert_says([], 'that tests live in tests/py/test_<module>.py', r'tests/py/test_<module>\\.py')\n"
    )

    assert guard.offences(tmp_path) == []


def test_1668_a_planted_test_file_passing_a_bare_suite_path_to_an_imported_assertion_helper_is_not_reported_as_running_a_nested_suite(tmp_path):
    guard = importlib.import_module("veri.fast_tier_guard")
    (tmp_path / "test_assert_bare.py").write_text(
        "from shared import assert_names\n"
        "\n"
        "def test_names_a_suite():\n"
        "    assert_names('tests/py/test_x.py')\n"
    )

    assert guard.offences(tmp_path) == []


def test_1668_a_planted_test_file_passing_a_prose_string_holding_a_suite_path_next_to_other_words_to_a_helper_is_not_reported_as_running_a_nested_suite(tmp_path):
    guard = importlib.import_module("veri.fast_tier_guard")
    (tmp_path / "test_prose.py").write_text(
        "from shared import says\n"
        "\n"
        "def test_names_a_path_in_prose():\n"
        "    says([], \"that a ported script's tests live in tests/py/test_<module>.py\")\n"
        "    says([], 'the shell suite is tests/foo.test.sh')\n"
    )

    assert guard.offences(tmp_path) == []


def test_1668_a_planted_test_file_passing_a_regex_ending_in_backslash_dot_py_to_a_helper_is_not_reported_as_running_a_nested_suite(tmp_path):
    guard = importlib.import_module("veri.fast_tier_guard")
    (tmp_path / "test_regex.py").write_text(
        "from shared import says\n"
        "\n"
        "def test_names_a_path_in_a_regex():\n"
        "    says([], r\"tests/py/test_<module>\\.py\")\n"
    )

    assert guard.offences(tmp_path) == []


def test_1900_a_planted_test_file_passing_a_shell_command_running_a_pytest_suite_to_an_imported_helper_is_reported_as_running_a_nested_suite_by_file_and_line(tmp_path):
    guard = importlib.import_module("veri.fast_tier_guard")
    offender = tmp_path / "test_offender.py"
    offender.write_text(
        "from shared import sh\n"
        "\n"
        "def test_runs_a_suite():\n"
        "    sh(\"python3 -m pytest tests/py/test_x.py\")\n"
    )

    found = guard.offences(tmp_path)

    assert found == [f"{offender}:4: runs a nested suite"]


def test_1900_a_planted_test_file_passing_a_shell_command_running_a_bash_suite_to_an_imported_helper_is_reported_as_running_a_nested_suite_by_file_and_line(tmp_path):
    guard = importlib.import_module("veri.fast_tier_guard")
    offender = tmp_path / "test_offender.py"
    offender.write_text(
        "from shared import sh\n"
        "\n"
        "def test_runs_a_suite():\n"
        "    sh(\"bash skills/tdd/scripts/tests/foo.test.sh\")\n"
    )

    found = guard.offences(tmp_path)

    assert found == [f"{offender}:4: runs a nested suite"]


def test_1900_a_planted_test_file_passing_a_suite_path_containing_a_space_to_an_imported_helper_is_reported_as_running_a_nested_suite_while_a_prose_string_and_a_regex_beside_it_are_not(tmp_path):
    guard = importlib.import_module("veri.fast_tier_guard")
    offender = tmp_path / "test_offender.py"
    offender.write_text(
        "import re\n"
        "from shared import run_it, note\n"
        "\n"
        "def test_runs_a_suite():\n"
        "    note(\"see tests/py/test_x.py for details\")\n"
        "    re.compile(r\"\\btest_\\w+\\.py$\")\n"
        "    run_it(\"tests/py/my dir/test_x.py\")\n"
    )

    found = guard.offences(tmp_path)

    assert found == [f"{offender}:7: runs a nested suite"]


def test_a_planted_test_file_naming_a_bare_test_file_as_a_table_key_in_monkeypatch_setitem_is_not_reported_as_running_a_nested_suite(tmp_path):
    guard = importlib.import_module("veri.fast_tier_guard")
    (tmp_path / "test_keyed.py").write_text(
        "import conftest\n"
        "\n"
        "def test_plants_an_entry(monkeypatch):\n"
        "    monkeypatch.setitem(conftest.TABLE, \"test_planted.py\", \"the whole file reads HEAD\")\n"
    )

    assert guard.offences(tmp_path) == []


def test_a_planted_test_file_naming_a_test_file_as_a_table_key_is_exempt_only_when_setitem_or_delitem_is_called_on_monkeypatch(tmp_path):
    guard = importlib.import_module("veri.fast_tier_guard")
    for name, call in (
        ("set", "monkeypatch.setitem(TABLE, \"test_planted.py\", 1)"),
        ("del", "monkeypatch.delitem(TABLE, \"test_planted.py\")"),
        ("other", "runner.setitem(TABLE, \"test_planted.py\", 1)"),
    ):
        (tmp_path / f"test_{name}.py").write_text(
            "from shared import TABLE, runner\n"
            "\n"
            "def test_plants_an_entry(monkeypatch):\n"
            f"    {call}\n"
        )

    found = guard.offences(tmp_path)

    assert found == [f"{tmp_path / 'test_other.py'}:4: runs a nested suite"]


def test_2168_the_readers_audit_suites_and_their_index_guard_live_under_tests_py_unit_and_not_beside_it():
    tier = SCRIPTS / "tests" / "py"
    names = (
        "test_readers_tree_index.py",
        "test_skill_cost_check_readers.py",
        "test_skill_diff_checked_readers.py",
        "test_skill_draft_pr_readers.py",
        "test_skill_green_readers.py",
        "test_skill_plan_readers.py",
        "test_skill_red_readers.py",
        "test_tree_index_guard.py",
    )
    assert [(name, (tier / name).is_file(), (tier / "unit" / name).is_file()) for name in names] == [
        (name, False, True) for name in names
    ]
    for name in ("test_skill_refactor_readers.py", "test_skill_phased_readers.py"):
        assert (name, (tier / name).is_file(), (tier / "unit" / name).is_file()) == (name, True, False)

def test_the_ledger_path_single_source_suite_lives_under_tests_py_unit_and_not_beside_it():
    tier = SCRIPTS / "tests" / "py"
    name = "test_ledger_path_single_source.py"
    assert (name, (tier / name).is_file(), (tier / "unit" / name).is_file()) == (name, False, True)


def test_the_fence_rule_home_suite_lives_under_tests_py_unit_and_not_beside_it():
    tier = SCRIPTS / "tests" / "py"
    name = "test_fence_rule_home.py"
    assert ((tier / name).is_file(), (tier / "unit" / name).is_file()) == (False, True)


def test_2226_the_suite_red_resume_cases_in_the_fast_tier_are_not_reported_as_running_a_nested_suite():
    guard = importlib.import_module("veri.fast_tier_guard")
    path = SCRIPTS / "tests" / "py" / "unit" / "test_suite_red_resume.py"

    assert guard._file_offences(path) == []


def test_1842_the_retired_filers_gone_suite_lives_under_tests_py_unit_and_not_beside_it():
    tier = SCRIPTS / "tests" / "py"
    name = "test_retired_filers_gone.py"
    assert ((tier / name).is_file(), (tier / "unit" / name).is_file()) == (False, True)


def test_2623_the_venv_refusal_suite_that_starts_make_for_real_is_named_by_the_guard_and_so_belongs_outside_the_tier(tmp_path):
    guard = importlib.import_module("veri.fast_tier_guard")
    suite = SCRIPTS / "tests" / "py" / "test_recipe_venv_refusal_process.py"
    (tmp_path / suite.name).write_text(suite.read_text())

    assert [line.split(":")[0] for line in guard.offences(tmp_path, {})] == [str(tmp_path / suite.name)]
