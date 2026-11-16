"""Medium case for the Makefile's install-dev target: make started for real over a planted tree whose lock names one
local wheel, pip offline (no index, the wheel's directory as its only source), so no case touches the network (#3967)."""
import base64
import hashlib
import os
import shutil
import subprocess
import zipfile

import pytest

from conftest import ROOT, SCRIPTS


def fake_wheel(directory):
    """A minimal wheel of `veri-fake-pkg` 1.0 in <directory>; its sha256."""
    files = {"veri_fake_pkg/__init__.py": "",
             "veri_fake_pkg-1.0.dist-info/METADATA": "Metadata-Version: 2.1\nName: veri-fake-pkg\nVersion: 1.0\n",
             "veri_fake_pkg-1.0.dist-info/WHEEL": "Wheel-Version: 1.0\nGenerator: hand\nRoot-Is-Purelib: true\nTag: py3-none-any\n"}
    record = "".join("%s,sha256=%s,%d\n" % (name, base64.urlsafe_b64encode(hashlib.sha256(text.encode()).digest())
                                             .rstrip(b"=").decode(), len(text)) for name, text in files.items())
    files["veri_fake_pkg-1.0.dist-info/RECORD"] = record + "veri_fake_pkg-1.0.dist-info/RECORD,,\n"
    wheel = directory / "veri_fake_pkg-1.0-py3-none-any.whl"
    with zipfile.ZipFile(wheel, "w") as archive:
        for name, text in files.items():
            archive.writestr(name, text)
    return hashlib.sha256(wheel.read_bytes()).hexdigest()


def install_dev(tree, venv, wheels):
    """(exit code, output) of `make install-dev` in <tree>, the venv at <venv>, pip offline over <wheels>."""
    env = {k: v for k, v in os.environ.items() if not k.startswith(("VERI_", "PIP_"))}
    env.update(VERI_VENV=str(venv), PIP_NO_INDEX="1", PIP_FIND_LINKS=str(wheels), PIP_CONFIG_FILE=os.devnull,
               PIP_DISABLE_PIP_VERSION_CHECK="1", PIP_NO_CACHE_DIR="1")
    ran = subprocess.run(["make", "-C", str(tree), "install-dev"], env=env, stdin=subprocess.DEVNULL,
                         capture_output=True, text=True, timeout=80)
    return ran.returncode, ran.stdout + ran.stderr


@pytest.mark.process("make install-dev started for real over a planted tree; it builds a venv and runs pip offline")
def test_make_install_dev_exits_non_zero_on_a_lock_line_missing_its_hash_and_installs_it_with_one_issue_3967(tmp_path):
    tree, wheels, venv = tmp_path / "tree", tmp_path / "wheels", tmp_path / "venv"
    (tree / "skills" / "tdd" / "scripts").mkdir(parents=True)
    wheels.mkdir()
    shutil.copy(ROOT / "Makefile", tree / "Makefile")
    (tree / "skills" / "tdd" / "scripts" / "lib").symlink_to(SCRIPTS / "lib")
    digest = fake_wheel(wheels)
    (tree / "requirements-dev.txt").write_text("veri-fake-pkg==1.0\n")

    code, output = install_dev(tree, venv, wheels)
    (tree / "requirements-dev.txt").write_text("veri-fake-pkg==1.0 \\\n    --hash=sha256:%s\n" % digest)
    hashed = install_dev(tree, venv, wheels)

    assert (code != 0, "--require-hashes" in output, hashed[0]) == (True, True, 0), (output, hashed)
