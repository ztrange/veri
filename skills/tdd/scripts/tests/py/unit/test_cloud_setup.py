"""In-process cases for veri/cloud_setup.py, the module cloud-setup.sh is a shim over."""
import importlib
import os

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


def test_with_no_interpreter_at_or_above_the_floor_and_no_uv_it_exits_2_naming_each_interpreter_tried_and_its_version(
        tmp_path, run_cli, cloud_setup, monkeypatch):
    empty = tmp_path / "bin"
    empty.mkdir()
    venv = tmp_path / "venv"
    installs = []
    monkeypatch.setattr(cloud_setup, "_version", {"python3": "3.11.9"}.get)
    monkeypatch.setattr(cloud_setup, "_install", lambda python, where: installs.append((python, where)))

    code, out, err = run_cli(cloud_setup, [], env={"CLAUDE_CODE_REMOTE": "true", "PATH": str(empty),
                                                   "VERI_VENV": str(venv)})

    assert (code, out, installs) == (2, "", [])
    assert err == ("cloud-setup: veri needs Python 3.12 or newer; python3 is version 3.11.9.\n"
                   "cloud-setup: veri needs Python 3.12 or newer; no python3.13 on PATH.\n"
                   "cloud-setup: veri needs Python 3.12 or newer; no python3.12 on PATH.\n")


def test_with_no_interpreter_at_or_above_the_floor_but_uv_it_installs_one_with_uv_and_uses_it(
        tmp_path, run_cli, cloud_setup, monkeypatch):
    venv = tmp_path / "venv"
    installed = []
    installs = []

    def uv(*args):
        if args == ("python", "install", "3.12"):
            installed.append("3.12")
            return ""
        if args == ("python", "find", "3.12") and installed:
            return "/root/.local/share/uv/python/cpython-3.12.7/bin/python3.12\n"
        raise AssertionError("unexpected uv call: %r" % (args,))

    monkeypatch.setattr(cloud_setup, "_version", {"python3": "3.11.9"}.get)
    monkeypatch.setattr(cloud_setup, "_uv", uv)
    monkeypatch.setattr(cloud_setup, "_install", lambda python, where: installs.append((python, where)))

    code, out, err = run_cli(cloud_setup, [], env={"CLAUDE_CODE_REMOTE": "true", "VERI_VENV": str(venv)})

    assert (code, err) == (0, "")
    assert installs == [("/root/.local/share/uv/python/cpython-3.12.7/bin/python3.12", str(venv))]


class Boundary:
    """cloud_setup's process boundary: shutil.which finds only the names given, and fake_processes answers each
    subprocess call by its argv prefix, (returncode, stdout); calls lists each as (argv, env)."""

    def __init__(self, fake):
        self.fake = fake

    @property
    def calls(self):
        return [(list(argv), kwargs.get("env")) for argv, kwargs in self.fake.seen]


@pytest.fixture
def boundary(monkeypatch, cloud_setup, fake_processes):
    def install(on_path, answers):
        monkeypatch.setattr(cloud_setup.shutil, "which", lambda name: "/fake/" + name if name in on_path else None)
        table = {" ".join([os.path.basename(argv[0])] + argv[1:]): (code, out, "") for argv, (code, out) in answers}
        return Boundary(fake_processes.answers(table, default=(0, "", "")))
    return install


PROBE = ["/fake/python3", "-c", "import platform; print(platform.python_version())"]


def test_with_no_venv_it_creates_one_with_the_interpreter_found_and_runs_make_install_dev_into_it(
        tmp_path, run_cli, cloud_setup, monkeypatch, boundary):
    venv = tmp_path / "venv"
    processes = boundary({"python3"}, [(PROBE, (0, "3.12.7\n"))])

    code, out, err = run_cli(cloud_setup, [], env={"CLAUDE_CODE_REMOTE": "true", "VERI_VENV": str(venv)})

    assert (code, err) == (0, "")
    assert [args for args, env in processes.calls] == [
        PROBE, ["python3", "-m", "venv", str(venv)], ["make", "-C", cloud_setup.ROOT, "install-dev"]]
    assert processes.calls[-1][1]["VERI_VENV"] == str(venv)
    assert (venv / ".veri-lock-sha256").read_text() == cloud_setup._lock_sha256()


def test_with_a_venv_holding_bin_python3_but_no_stamp_it_runs_make_install_dev_without_creating_the_venv_again(
        tmp_path, run_cli, cloud_setup, monkeypatch, boundary):
    venv = tmp_path / "venv"
    (venv / "bin").mkdir(parents=True)
    (venv / "bin" / "python3").write_text("")
    processes = boundary({"python3"}, [(PROBE, (0, "3.12.7\n"))])

    code, out, err = run_cli(cloud_setup, [], env={"CLAUDE_CODE_REMOTE": "true", "VERI_VENV": str(venv)})

    assert (code, err) == (0, "")
    assert [args for args, env in processes.calls] == [PROBE, ["make", "-C", cloud_setup.ROOT, "install-dev"]]


def test_when_make_install_dev_fails_it_exits_2_writing_no_stamp_and_no_path_line(
        tmp_path, run_cli, cloud_setup, monkeypatch, boundary):
    venv = tmp_path / "venv"
    env_file = tmp_path / "claude-env"
    boundary({"python3"}, [(PROBE, (0, "3.12.7\n")), (["make"], (2, ""))])

    code, out, err = run_cli(cloud_setup, [], env={"CLAUDE_CODE_REMOTE": "true", "VERI_VENV": str(venv),
                                                   "CLAUDE_ENV_FILE": str(env_file)})

    assert code == 2
    assert not (venv / ".veri-lock-sha256").exists() and not env_file.exists()


def test_an_interpreter_whose_version_probe_fails_counts_as_none_even_when_it_printed_a_version(
        tmp_path, run_cli, cloud_setup, monkeypatch, boundary):
    venv = tmp_path / "venv"
    processes = boundary({"python3"}, [(PROBE, (1, "3.12.7\n"))])

    code, out, err = run_cli(cloud_setup, [], env={"CLAUDE_CODE_REMOTE": "true", "VERI_VENV": str(venv)})

    assert code == 2
    assert [args for args, env in processes.calls] == [PROBE]
    assert not venv.exists()


def test_given_an_argument_it_exits_2_naming_it_and_runs_nothing(tmp_path, run_cli, cloud_setup, monkeypatch, boundary):
    venv = tmp_path / "venv"
    processes = boundary({"python3"}, [(PROBE, (0, "3.12.7\n"))])

    code, out, err = run_cli(cloud_setup, ["extra"], env={"CLAUDE_CODE_REMOTE": "true", "VERI_VENV": str(venv)})

    assert (code, out) == (2, "")
    assert err == "cloud-setup.sh: unexpected argument 'extra'\nusage: cloud-setup.sh\n"
    assert processes.calls == [] and not venv.exists()


def test_with_veri_venv_unset_it_hands_make_the_default_venv_as_veri_venv(tmp_path, run_cli, cloud_setup, monkeypatch, boundary):
    monkeypatch.delenv("VERI_VENV", raising=False)
    home = tmp_path / "home"
    processes = boundary({"python3"}, [(PROBE, (0, "3.12.7\n"))])

    code, out, err = run_cli(cloud_setup, [], env={"CLAUDE_CODE_REMOTE": "true", "HOME": str(home)})

    assert (code, err) == (0, "")
    make = [env for args, env in processes.calls if args[0] == "make"]
    assert [env.get("VERI_VENV") for env in make] == [str(home / ".veri-tools" / "venv")]
