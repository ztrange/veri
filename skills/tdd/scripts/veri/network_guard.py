"""A pytest plugin the launcher loads: no case may reach a non-loopback address or start gh or curl."""
import ipaddress
import os
import socket
import subprocess

import pytest


def loopback(host):
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


@pytest.fixture(autouse=True)
def network_refusal(monkeypatch):
    real_connect = socket.socket.connect
    real_popen = subprocess.Popen.__init__

    def check_address(sock, address):
        if sock.family in (socket.AF_INET, socket.AF_INET6) and not loopback(address[0]):
            raise AssertionError("a case connected to %s; fake the network" % address[0])

    def connect(self, address):
        check_address(self, address)
        return real_connect(self, address)

    def popen(self, args, *rest, **kwargs):
        words = [args] if isinstance(args, (str, bytes, os.PathLike)) else list(args)
        command = os.path.basename(os.fsdecode(words[0])) if words else ""
        if command in ("gh", "curl"):
            raise AssertionError("a case started %s; fake the call" % command)
        return real_popen(self, args, *rest, **kwargs)

    monkeypatch.setattr(socket.socket, "connect", connect)
    monkeypatch.setattr(subprocess.Popen, "__init__", popen)
