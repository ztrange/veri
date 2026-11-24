"""In-process cases for veri/cloud_install.py, the module cloud-install.sh is a shim over."""
import importlib
import json

import pytest


@pytest.fixture
def cloud_install():
    return importlib.import_module("veri.cloud_install")


@pytest.fixture
def own_repo(tmp_path, cloud_install, monkeypatch):
    """A repository holding veri's own scripts, as cloud-install.sh sees it."""
    repo = tmp_path / "repo"
    scripts = repo / "skills" / "tdd" / "scripts"
    scripts.mkdir(parents=True)
    monkeypatch.setattr(cloud_install, "SCRIPTS", str(scripts))
    return repo


SETUP = '"$CLAUDE_PROJECT_DIR"/skills/tdd/scripts/cloud-setup.sh'


def cloud_hook(setup):
    return {"hooks": [{"type": "command", "command": '[ "$CLAUDE_CODE_REMOTE" != true ] || ' + setup}]}


def test_on_a_repository_with_no_settings_it_creates_them_holding_one_cloud_session_start_hook(own_repo, run_cli, cloud_install):
    code, out, err = run_cli(cloud_install, [str(own_repo)])

    settings = own_repo / ".claude" / "settings.json"
    assert (code, err) == (0, "")
    assert json.loads(settings.read_text()) == {"hooks": {"SessionStart": [cloud_hook(SETUP)]}}


def test_on_existing_settings_it_adds_the_hook_and_keeps_every_existing_key_and_hook(own_repo, run_cli, cloud_install):
    settings = own_repo / ".claude" / "settings.json"
    settings.parent.mkdir()
    theirs = {"hooks": [{"type": "command", "command": "echo hello"}]}
    stop = {"hooks": [{"type": "command", "command": "echo bye"}]}
    settings.write_text(json.dumps({"model": "opus", "permissions": {"allow": ["Bash(ls)"]},
                                    "hooks": {"SessionStart": [theirs], "Stop": [stop]}}))

    code, out, err = run_cli(cloud_install, [str(own_repo)])

    assert (code, err) == (0, "")
    assert json.loads(settings.read_text()) == {"model": "opus", "permissions": {"allow": ["Bash(ls)"]},
                                                "hooks": {"SessionStart": [theirs, cloud_hook(SETUP)], "Stop": [stop]}}


def test_run_a_second_time_it_changes_nothing_and_leaves_one_hook(own_repo, run_cli, cloud_install):
    settings = own_repo / ".claude" / "settings.json"
    run_cli(cloud_install, [str(own_repo)])
    first = settings.read_bytes()

    code, out, err = run_cli(cloud_install, [str(own_repo)])

    assert (code, out, err) == (0, "already present in " + str(settings) + "\n", "")
    assert settings.read_bytes() == first
    assert len(json.loads(first)["hooks"]["SessionStart"]) == 1


def test_on_settings_that_are_not_valid_json_it_exits_2_naming_the_file_and_leaves_it_unchanged(own_repo, run_cli, cloud_install):
    settings = own_repo / ".claude" / "settings.json"
    settings.parent.mkdir()
    settings.write_bytes(b'{"model": "opus",\n')

    code, out, err = run_cli(cloud_install, [str(own_repo)])

    assert (code, out) == (2, "")
    assert err.count("\n") == 1 and str(settings) in err
    assert settings.read_bytes() == b'{"model": "opus",\n'


def test_on_the_repository_holding_its_own_scripts_it_names_cloud_setup_through_claude_project_dir(tmp_path, own_repo, run_cli, cloud_install):
    (tmp_path / "link").symlink_to(own_repo)

    code, out, err = run_cli(cloud_install, [str(tmp_path / "link")])

    settings = own_repo / ".claude" / "settings.json"
    assert (code, err) == (0, "")
    assert json.loads(settings.read_text()) == {"hooks": {"SessionStart": [cloud_hook(SETUP)]}}


def test_on_a_repository_other_than_veris_own_it_exits_2_with_one_stderr_line_and_writes_nothing(tmp_path, run_cli, cloud_install):
    code, out, err = run_cli(cloud_install, [str(tmp_path)])

    assert (code, out) == (2, "")
    assert err == "cloud-install: cloud setup supports only veri's own repository for now; " + str(tmp_path) + " is not it\n"
    assert list(tmp_path.iterdir()) == []
