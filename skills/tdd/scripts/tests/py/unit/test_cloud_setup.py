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
