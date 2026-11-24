"""In-process cases for veri/cloud_install.py, the module cloud-install.sh is a shim over."""
import importlib
import json
import os

import pytest

from conftest import SCRIPTS


@pytest.fixture
def cloud_install():
    return importlib.import_module("veri.cloud_install")


def cloud_hook(setup):
    return {"hooks": [{"type": "command", "command": '[ "$CLAUDE_CODE_REMOTE" != true ] || ' + setup}]}


def test_on_a_repository_with_no_settings_it_creates_them_holding_one_cloud_session_start_hook(tmp_path, run_cli, cloud_install):
    code, out, err = run_cli(cloud_install, [str(tmp_path)])

    settings = tmp_path / ".claude" / "settings.json"
    setup = os.path.join(os.path.realpath(SCRIPTS), "cloud-setup.sh")
    assert (code, err) == (0, "")
    assert json.loads(settings.read_text()) == {"hooks": {"SessionStart": [cloud_hook(setup)]}}
