"""In-process cases for veri/session_env.py, the strip run-leaf.sh's module launches its leaf through."""
import importlib
import re

from conftest import SCRIPTS


def test_session_vars_equal_the_libs_list_and_the_strip_removes_them_and_only_with_an_id_every_value_carrying_it():
    session_env = importlib.import_module("veri.session_env")
    lib = (SCRIPTS / "lib" / "session-env.sh").read_text()
    declared = re.search(r"^SESSION_VARS=\(\n(.*?)^\)", lib, re.M | re.S).group(1).split()

    session_id = "a.b*c"
    with_id = {name: "x" for name in session_env.SESSION_VARS}
    with_id.update(CLAUDE_CODE_SESSION_ID=session_id, CARRIES="pre-a.b*c-post", PATTERN_ONLY="aXb_c", KEPT="v")
    session_env.strip_session_env(with_id)

    without_id = {name: "x" for name in session_env.SESSION_VARS}
    without_id.update(CLAUDE_CODE_SESSION_ID="", CARRIES="pre-a.b*c-post", KEPT="v")
    session_env.strip_session_env(without_id)

    assert (list(session_env.SESSION_VARS), with_id, without_id) == (
        declared,
        {"PATTERN_ONLY": "aXb_c", "KEPT": "v"},
        {"CARRIES": "pre-a.b*c-post", "KEPT": "v"},
    )
