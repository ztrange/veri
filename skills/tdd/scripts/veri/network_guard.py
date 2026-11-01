"""A pytest plugin the launcher loads: no case may reach a non-loopback address or start a gh or curl it did not plant under its basetemp."""
import ipaddress
import os
import shutil
import socket
import subprocess

import pytest

from veri.popen_command import command_basename, command_words


def loopback(host):
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


def faked(command, kwargs, basetemp):
    env = kwargs.get("env") or os.environ
    found = command if os.sep in command else shutil.which(command, path=env.get("PATH"))
    return bool(found) and os.path.realpath(found).startswith(basetemp + os.sep)


@pytest.fixture(autouse=True)
def network_refusal(monkeypatch, tmp_path_factory):
    basetemp = os.path.realpath(tmp_path_factory.getbasetemp())
    real_connect = socket.socket.connect
    real_popen = subprocess.Popen.__init__
    refusals = {}
    for name in ("gh", "curl"):
        refusals[name] = tmp_path_factory.mktemp("refuse-" + name)
        (refusals[name] / name).write_text("#!/bin/sh\necho \"a case started %s; fake the call\" >&2\nexit 1\n" % name)
        (refusals[name] / name).chmod(0o755)

    def check_address(sock, address):
        if sock.family in (socket.AF_INET, socket.AF_INET6) and not loopback(address[0]):
            raise AssertionError("a case connected to %s; fake the network" % address[0])

    def connect(self, address):
        check_address(self, address)
        return real_connect(self, address)

    def popen(self, args, *rest, **kwargs):
        words = command_words(args)
        command = command_basename(words)
        if command in ("gh", "curl") and not faked(os.fsdecode(words[0]), kwargs, basetemp):
            raise AssertionError("a case started %s; fake the call" % command)
        env = kwargs.get("env")
        if env is not None:
            path = os.pathsep.join(os.get_exec_path(env))
            for name in ("gh", "curl"):
                if not faked(name, kwargs, basetemp):
                    path = str(refusals[name]) + os.pathsep + path
            kwargs["env"] = dict(env, PATH=path)
        return real_popen(self, args, *rest, **kwargs)

    monkeypatch.setattr(socket.socket, "connect", connect)
    monkeypatch.setattr(subprocess.Popen, "__init__", popen)
