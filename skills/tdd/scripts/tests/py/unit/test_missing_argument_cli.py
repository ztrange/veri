import importlib
import pathlib
import re

import pytest

SCRIPTS = pathlib.Path(__file__).resolve().parents[3]
SHIM_MODULE = re.compile(r'^exec python3 .*/veri/(\w+)\.py"', re.MULTILINE)
FLOOR_KNOBS = {"VERI_BASH_MAJOR": "5", "VERI_PYTHON_VERSION": "3.12.0"}


def requires_argument(script):
    usage = re.search(r"usage: .*", script.read_text())
    return usage is not None and re.search(r"<.*?>", re.sub(r"\[[^\]]*\]", "", usage.group(0))) is not None


def subjects():
    return sorted(script.name for script in SCRIPTS.glob("*.sh") if requires_argument(script))


@pytest.mark.tree_audit("every skills/tdd/scripts/*.sh, read for its usage line and its shim")
@pytest.mark.parametrize("name", subjects())
def test_a_script_requiring_a_positional_argument_exits_2_with_a_usage_line_when_called_with_none(name, run_cli):
    module = importlib.import_module(SHIM_MODULE.search((SCRIPTS / name).read_text()).group(1))
    code, out, err = run_cli(module, [], env=FLOOR_KNOBS)
    assert code == 2, "%s: want exit 2, got %s: %s" % (name, code, err)
    assert "usage" in err, "%s: no usage line on stderr: %r" % (name, err)
    assert name in err, "%s: usage line does not name it: %r" % (name, err)
