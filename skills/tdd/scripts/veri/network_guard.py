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

    def check_address(sock, address):
        if sock.family in (socket.AF_INET, socket.AF_INET6) and not loopback(address[0]):
            raise AssertionError("a case connected to %s; fake the network" % address[0])

    def connect(self, address):
        check_address(self, address)
        return real_connect(self, address)

    def popen(self, args, *rest, **kwargs):
        command = command_basename(args)
        if command in ("gh", "curl") and not faked(os.fsdecode(command_words(args)[0]), kwargs, basetemp):
            raise AssertionError("a case started %s; fake the call" % command)
        return real_popen(self, args, *rest, **kwargs)

    monkeypatch.setattr(socket.socket, "connect", connect)
    monkeypatch.setattr(subprocess.Popen, "__init__", popen)
