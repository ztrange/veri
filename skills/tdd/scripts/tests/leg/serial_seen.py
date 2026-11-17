"""The pytest leg's probe plugin: records in a file what each collection held, for the leg to plan its serial pass from.

One record per collection, appended in a single write so xdist workers' records never interleave:
  `serial` or `none`   whether a case carried the serial mark
  `named <n>`          how many cases were collected, before any -k or -m deselected one
  `args <json>`        the targets pytest parsed, the rootdir and the ini file it settled on
  `file <path>`        one line per test file holding a serial case"""
import json
import os

import pytest


@pytest.hookimpl(tryfirst=True)
def pytest_collection_modifyitems(items):
    path = os.environ.get("PYTEST_LEG_SERIAL_SEEN")
    if not path:
        return
    serial = [item for item in items if item.get_closest_marker("serial")]
    lines = ["serial" if serial else "none", "named %d" % len(items)]
    if items:
        config = items[0].config
        lines.append("args " + json.dumps({"targets": list(config.args), "root": str(config.rootpath),
                                           "ini": str(config.inipath) if config.inipath else None}))
    lines.extend("file " + held for held in dict.fromkeys(str(item.path) for item in serial))
    try:
        descriptor = os.open(path, os.O_WRONLY | os.O_APPEND | os.O_CREAT)
    except FileNotFoundError:
        return
    try:
        os.write(descriptor, ("\n".join(lines) + "\n").encode())
    finally:
        os.close(descriptor)
