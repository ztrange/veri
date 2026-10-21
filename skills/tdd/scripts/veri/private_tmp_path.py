"""The pytest leg's tmp_path plugin: one fresh directory under the session basetemp, made without numbering."""
import pathlib
import re
import tempfile

import pytest


def make_tmp_path(node_name, tmp_path_factory):
    name = re.sub(r"[\W]", "_", node_name)[:30]
    return pathlib.Path(tempfile.mkdtemp(prefix=name + "_", dir=tmp_path_factory.getbasetemp()))


@pytest.fixture
def tmp_path(request, tmp_path_factory):
    return make_tmp_path(request.node.name, tmp_path_factory)
