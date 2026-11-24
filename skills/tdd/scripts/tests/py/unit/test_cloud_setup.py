"""In-process cases for veri/cloud_setup.py, the module cloud-setup.sh is a shim over."""
import importlib

import pytest


@pytest.fixture
def cloud_setup():
    return importlib.import_module("veri.cloud_setup")


def test_outside_a_cloud_session_it_exits_0_doing_nothing(tmp_path, run_cli, cloud_setup):
    env_file = tmp_path / "claude-env"
    venv = tmp_path / "venv"

    code, out, err = run_cli(cloud_setup, [], env={"CLAUDE_CODE_REMOTE": "false", "CLAUDE_ENV_FILE": str(env_file),
                                                   "VERI_VENV": str(venv)})

    assert (code, out, err) == (0, "", "")
    assert not env_file.exists() and not venv.exists()


def test_in_a_cloud_session_it_installs_with_the_first_interpreter_at_or_above_the_floor_and_writes_the_path_line(
        tmp_path, run_cli, cloud_setup, monkeypatch):
    env_file = tmp_path / "claude-env"
    env_file.write_text("export FOO=1\n")
    venv = tmp_path / "venv"
    versions = {"python3": "3.11.9", "python3.13": "3.13.1", "python3.12": "3.12.7"}
    installs = []
    monkeypatch.setattr(cloud_setup, "_version", versions.get)
    monkeypatch.setattr(cloud_setup, "_install", lambda python, where: installs.append((python, where)))

    code, out, err = run_cli(cloud_setup, [], env={"CLAUDE_CODE_REMOTE": "true", "CLAUDE_ENV_FILE": str(env_file),
                                                   "VERI_VENV": str(venv)})

    assert (code, err) == (0, "")
    assert installs == [("python3.13", str(venv))]
    assert env_file.read_text() == 'export FOO=1\nexport PATH="' + str(venv) + '/bin:$PATH"\n'


def test_called_again_with_the_same_venv_lock_it_runs_no_install_and_leaves_one_path_line(
        tmp_path, run_cli, cloud_setup, monkeypatch):
    env_file = tmp_path / "claude-env"
    venv = tmp_path / "venv"
    installs = []
    monkeypatch.setattr(cloud_setup, "_version", {"python3": "3.12.7"}.get)
    monkeypatch.setattr(cloud_setup, "_install", lambda python, where: installs.append((python, where)))
    env = {"CLAUDE_CODE_REMOTE": "true", "CLAUDE_ENV_FILE": str(env_file), "VERI_VENV": str(venv)}
    run_cli(cloud_setup, [], env=env)

    code, out, err = run_cli(cloud_setup, [], env=env)

    assert (code, err) == (0, "")
    assert installs == [("python3", str(venv))]
    assert env_file.read_text() == 'export PATH="' + str(venv) + '/bin:$PATH"\n'
