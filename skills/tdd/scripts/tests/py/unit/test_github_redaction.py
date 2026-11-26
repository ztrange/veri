"""In-process cases for github.redact, the one function every body veri hands gh passes through (#3960, #3968).

Every token here is built from a documented shape with an obviously fake body; none is read from the environment."""
import ast
import base64
import importlib
import json
import pathlib
import re

import pytest

FAKE = "FAKEfake0123"  # 12 letters and digits, mixed case: three make a 36-character classic body


@pytest.fixture
def github():
    return importlib.import_module("veri.github")


@pytest.mark.parametrize("prefix", ["ghp_", "gho_", "ghu_", "ghs_", "ghr_"])
def test_redact_replaces_a_token_of_each_github_prefix_with_redacted_issue_3960(github, prefix):
    token = prefix + FAKE * 3

    assert github.redact("before %s after" % token) == "before [redacted] after"


def test_redact_replaces_a_fine_grained_github_pat_token_with_redacted_issue_3960(github):
    token = "github_pat_" + FAKE * 2 + "_" + FAKE * 5

    assert github.redact("pat=%s;" % token) == "pat=[redacted];"


def test_redact_replaces_an_sk_ant_key_with_redacted_issue_3960(github):
    key = "sk-ant-api03-" + FAKE + "_" + FAKE

    assert github.redact("key %s\n" % key) == "key [redacted]\n"


def test_redact_replaces_an_akia_access_key_id_with_redacted_issue_3960(github):
    assert github.redact("id=AKIAFAKE0123FAKE0123 ok") == "id=[redacted] ok"


def test_redact_replaces_every_occurrence_of_a_listed_variables_value_issue_3960(github, monkeypatch):
    monkeypatch.setenv("VERI_REDACT_VARS", "FAKE_SECRET")
    monkeypatch.setenv("FAKE_SECRET", "not-a-real-secret")

    assert github.redact("a not-a-real-secret b not-a-real-secret") == "a [redacted] b [redacted]"


def test_redact_leaves_alone_a_listed_variables_value_shorter_than_8_characters_issue_3960(github, monkeypatch):
    monkeypatch.setenv("VERI_REDACT_VARS", "FAKE_SHORT")
    monkeypatch.setenv("FAKE_SHORT", "a1b2c3d")

    assert github.redact("a1b2c3d stays") == "a1b2c3d stays"


def test_veri_redact_vars_defaults_to_gh_token_and_names_another_variable_when_set_issue_3960(github, monkeypatch):
    monkeypatch.delenv("VERI_REDACT_VARS", raising=False)
    monkeypatch.setenv("GH_TOKEN", "fake-gh-token-value")
    monkeypatch.setenv("FAKE_DEPLOY_KEY", "fake-deploy-key-value")
    unset = github.redact("fake-gh-token-value fake-deploy-key-value")
    monkeypatch.setenv("VERI_REDACT_VARS", "FAKE_DEPLOY_KEY")

    assert (unset, github.redact("fake-gh-token-value fake-deploy-key-value")) == (
        "[redacted] fake-deploy-key-value", "fake-gh-token-value [redacted]")


@pytest.mark.parametrize("empty", ["", "  "])
def test_a_set_but_empty_veri_redact_vars_reads_as_the_default_list_issue_3960(github, monkeypatch, empty):
    monkeypatch.setenv("VERI_REDACT_VARS", empty)
    monkeypatch.setenv("GH_TOKEN", "fake-gh-token-value")

    assert github.redact("t=fake-gh-token-value") == "t=[redacted]"


def posted(fake_processes, answer=(0, "https://github.com/o/r/issues/7#issuecomment-1\n", "")):
    """fake_processes answering every gh call with <answer>; the returned fake's argvs are what gh was handed."""
    return fake_processes.answers({"gh": answer})


def test_gh_issue_comment_hands_gh_the_body_redacted_issue_3960(github, fake_processes):
    token = "ghp_" + FAKE * 3
    fake = posted(fake_processes)

    github.gh_issue_comment("7", "leaf said %s\n" % token)

    assert "body=leaf said [redacted]\n" in fake.argvs[-1] and token not in " ".join(fake.argvs[-1])


def test_a_comment_body_with_nothing_to_redact_reaches_gh_byte_identical_issue_3960(github, fake_processes, monkeypatch):
    monkeypatch.setenv("GH_TOKEN", "fake-gh-token-value")
    body = "  ghp_short AKIA123 sk-ant-x github_pat_y fake-gh-token\r\n\\n é ✓ `gh[pousr]_` \t\n\n"
    fake = posted(fake_processes)

    github.gh_issue_comment("7", body)

    assert fake.argvs[-1][4] == "body=" + body


def test_gh_comment_post_and_gh_comment_edit_hand_gh_the_body_redacted_issue_3960(github, fake_processes):
    token = "gho_" + FAKE * 3
    fake = posted(fake_processes, (0, "{}", ""))

    github.gh_comment_post("7", "posted %s" % token)
    github.gh_comment_edit("99", "edited %s" % token)

    assert [argv[-1] for argv in fake.argvs] == ["body=posted [redacted]", "body=edited [redacted]"]


def test_gh_issue_create_hands_gh_the_title_and_the_body_redacted_issue_3968(github, fake_processes):
    token = "ghp_" + FAKE * 3
    fake = posted(fake_processes, (0, "https://github.com/o/r/issues/8\n", ""))

    github.gh_issue_create("Refactor candidates: %s" % token, "found %s in output" % token, "refactor")

    assert (fake.argvs[-1][4], fake.argvs[-1][6]) == ("title=Refactor candidates: [redacted]",
                                                      "body=found [redacted] in output")


def test_gh_issue_edit_hands_gh_a_body_file_whose_contents_are_redacted_the_callers_file_unchanged_issue_3968(
        github, fake_processes, tmp_path):
    token = "ghs_" + FAKE * 3
    body_file = tmp_path / "body.md"
    body_file.write_text("## Problem\nleaked %s\n" % token)
    read = []

    def gh(line, **kwargs):
        read.append(open(fake.argvs[-1][-1].split("=@", 1)[1]).read())
        return 0, "{}", ""
    fake = fake_processes.answers({"gh": gh})

    github.gh_issue_edit("60", str(body_file))

    assert (read, body_file.read_text()) == (["## Problem\nleaked [redacted]\n"], "## Problem\nleaked %s\n" % token)


@pytest.mark.parametrize("kind", [str, bytes])
def test_bounded_hands_gh_its_stdin_input_redacted_issue_3960(github, fake_processes, kind):
    token = "ghs_" + FAKE * 3
    fake = posted(fake_processes, (0, "{}", ""))
    body = '{"body": "leaked %s"}' % token

    github.bounded(["gh", "api", "x", "--input", "-"], input=body if kind is str else body.encode(),
                   capture_output=True, text=kind is str)

    assert fake.seen[-1][1]["input"] == (lambda t: t if kind is str else t.encode())('{"body": "leaked [redacted]"}')


FILE_FORMS = {"--input": lambda p: ["api", "x", "--input", p], "--body-file": lambda p: ["issue", "create", "--body-file", p],
              "-Fbody=@": lambda p: ["api", "x", "-Fbody=@" + p], "--field=body=@": lambda p: ["api", "x", "--field=body=@" + p],
              "--input=": lambda p: ["api", "x", "--input=" + p], "--body-file=": lambda p: ["pr", "edit", "--body-file=" + p]}


@pytest.mark.parametrize("form", sorted(FILE_FORMS))
def test_a_body_file_handed_gh_in_any_form_reaches_it_as_a_redacted_copy_in_a_private_directory_issue_3960(
        github, fake_processes, tmp_path, form):
    token = "ghu_" + FAKE * 3
    body_file = tmp_path / "body.md"
    body_file.write_text("out %s\n" % token)
    seen = []

    def gh(line, **kwargs):
        copy = handed(fake.argvs[-1][-1])
        seen.append((copy.read_text(), oct(copy.parent.stat().st_mode & 0o777), copy.parent != tmp_path))
        return 0, "{}", ""
    fake = fake_processes.answers({"gh": gh})

    github.run_gh(*FILE_FORMS[form](str(body_file)))

    assert (seen, body_file.read_text(), handed(fake.argvs[-1][-1]).exists()) == (
        [("out [redacted]\n", "0o700", True)], "out %s\n" % token, False)


def handed(arg):
    """The file a gh argument names: after `=@`, after a long option's `=`, or the argument itself."""
    if "=@" in arg:
        return pathlib.Path(arg.split("=@", 1)[1])
    return pathlib.Path(arg.split("=", 1)[1] if arg.startswith("--") else arg)


def test_redact_replaces_a_token_wrapped_across_a_line_break_or_a_json_newline_escape_issue_3960(github, monkeypatch):
    monkeypatch.setenv("GH_TOKEN", "fake-gh-token-value")
    token = "ghp_" + FAKE * 3
    wrapped = "x %s\n%s rest\nNext line\n" % (token[:20], token[20:])
    crlf = "%s\r\n%s\r\n" % (token[:10], token[10:])
    # Joined across split points, a token stops at its documented length: the next line's first word stays ("ok").
    escaped = '{"out": "%s\\n%s\\nok"}' % (token[:30], token[30:])
    value = "v fake-gh-\ntoken-value w"

    assert [github.redact(text) for text in (wrapped, crlf, escaped, value)] == [
        "x [redacted] rest\nNext line\n", "[redacted]\r\n", '{"out": "[redacted]\\nok"}', "v [redacted] w"]


def test_redact_replaces_a_token_inside_a_url_a_query_string_or_glued_to_text_issue_3960(github):
    app, user = "ghs_" + FAKE * 3, "ghu_" + "fakeFAKE9876" * 3
    texts = ("https://x-access-token:%s@github.com/o/r.git" % app, "https://h/x?token=%s&page=2" % user,
             "abc%sdef!" % app, "AKIAFAKE0123FAKE0123XY", "keysk-ant-" + FAKE * 2)

    assert [github.redact(text) for text in texts] == [
        "https://x-access-token:[redacted]@github.com/o/r.git", "https://h/x?token=[redacted]&page=2",
        "abc[redacted]!", "[redacted]XY", "key[redacted]"]


def test_redact_replaces_the_base64_of_a_token_or_of_a_listed_value_issue_3960(github, monkeypatch):
    monkeypatch.setenv("GH_TOKEN", "fake-gh-token-value")
    token = "ghr_" + FAKE * 3

    def b64(text, urlsafe=False):
        return (base64.urlsafe_b64encode if urlsafe else base64.b64encode)(text.encode()).decode()
    texts = ("Authorization: Basic %s\n" % b64("x-access-token:" + token), "x=%s;" % b64(token),
             "glued%s" % b64("prefix " + token), b64("::" + token, urlsafe=True), "v %s" % b64("fake-gh-token-value"))

    assert [github.redact(text) for text in texts] == [
        "Authorization: Basic [redacted]\n", "x=[redacted];", "[redacted]", "[redacted]", "v [redacted]"]


SHAPES = ["ghp_" + FAKE * 3, "github_pat_" + (FAKE * 2)[:22] + "_" + (FAKE * 5)[:59], "sk-ant-api03-" + FAKE * 2,
          "AKIAFAKE0123FAKE0123", "fake-gh-token-value"]


@pytest.mark.parametrize("wrap", ["\n    ", "\n\t", "  \n", " \t\n", "\\n  ", "\r\n  "])
@pytest.mark.parametrize("secret", SHAPES)
def test_redact_replaces_a_secret_split_by_a_wrap_with_indentation_or_trailing_blanks_issue_3960(
        github, monkeypatch, secret, wrap):
    monkeypatch.setenv("GH_TOKEN", "fake-gh-token-value")

    assert github.redact("a %s%s%s b" % (secret[:12], wrap, secret[12:])) == "a [redacted] b"


@pytest.mark.parametrize("mark", ["​", "‌", "‍", "﻿", "­"])
@pytest.mark.parametrize("secret", SHAPES)
def test_redact_replaces_a_secret_holding_a_zero_width_character_issue_3960(github, monkeypatch, secret, mark):
    monkeypatch.setenv("GH_TOKEN", "fake-gh-token-value")

    assert github.redact("a %s%s%s b" % (secret[:9], mark, secret[9:])) == "a [redacted] b"


def test_redact_replaces_a_listed_value_in_its_json_escaped_form_issue_3960(github, monkeypatch):
    value = 'fake\\secret"value'
    monkeypatch.setenv("VERI_REDACT_VARS", "FAKE_SECRET")
    monkeypatch.setenv("FAKE_SECRET", value)

    assert github.redact(json.dumps({"out": value})) == '{"out": "[redacted]"}'


@pytest.mark.timeout(10)
@pytest.mark.parametrize("body", [" " * 1048576, "\t \n" * 349525, "\\n " * 349525, "​" * 1048576])
def test_redact_answers_1_mb_of_blanks_and_breaks_within_the_case_timeout_issue_3960(github, body):
    assert github.redact(body) == body


@pytest.mark.timeout(10)
@pytest.mark.parametrize("shape", ["github_pat_" + "a" * 22, "sk-ant-" + "a" * 20, "ghp_" + "a" * 36, "AKIA" + "A" * 16])
def test_redact_answers_1_mb_of_one_repeated_token_shape_within_the_case_timeout_issue_3960(github, shape):
    body = shape * (1048576 // len(shape)) + " tail"

    assert github.redact(body) == "[redacted] tail"


@pytest.mark.timeout(10)
def test_redact_answers_a_1_mb_body_holding_tokens_within_the_case_timeout_issue_3960(github):
    token = "ghp_" + FAKE * 3
    prose = "step 4 FAIL_OUTPUT: assert 1 == 2 in test_split.py, line 17\n" * 400
    body = (prose + "leaked %s here\n" % token + "QUFB" * 500 + "\n") * 40

    redacted = github.redact(body)

    assert (len(body) > 1000000, redacted.count("leaked [redacted] here\n"), "ghp_" in redacted) == (True, 40, False)


# Where a veri module may name the gh command: github.bounded, which redacts every argument it hands gh, and the
# functions that call it; and three command lines that carry no text veri wrote, so nothing to redact.
GH_SITES = {
    ("redaction.py", "<module>"): "the shape prefix gh of the token patterns",
    ("github.py", "bounded"): "the redaction itself",
    ("github.py", "run_gh"): "through bounded",
    ("github.py", "gh_probe"): "through bounded",
    ("github.py", "rate_limit_reset"): "through bounded",
    ("plan_publish.py", "gh_call"): "through bounded (fused.run_script's run hook)",
    ("preflight.py", "issue_body"): "a read of the issue body",
    ("preflight.py", "check_environment"): "gh api user, a read",
    ("preflight.py", "finish"): "a read of the default branch",
    ("preflight.py", "ci_green"): "gh run list, a read of CI runs on the baselined commit",
    ("merge_common.py", "merge"): "the merge call, which names a pull request and a sha only",
    ("skill_edit_half.py", "run"): "a read of the issue body, through bounded",
}


def gh_sites(modules):
    """(file, enclosing function, line) of every string constant "gh" in the veri modules <modules> indexes."""
    sites = []
    for stem in modules.names:
        tree = modules.tree(stem)
        for function in [tree] + [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]:
            inner = {id(c) for n in ast.walk(function) if n is not function and isinstance(n, ast.FunctionDef)
                     for c in ast.walk(n)}
            name = getattr(function, "name", "<module>")
            sites += [(stem + ".py", name, n.lineno) for n in ast.walk(function)
                      if isinstance(n, ast.Constant) and n.value == "gh" and id(n) not in inner]
    return sites


# A string that runs gh as a shell command: gh as a word of it.
GH_WORD = re.compile(r"(^|[\s;&|(`$])gh(\s|$)")
SHELLS = {"sh", "bash", "zsh", "dash"}


def _dotted(node):
    """`os.system` for the callee os.system, `run` for a bare run, "" for anything else."""
    if isinstance(node, ast.Attribute):
        return (_dotted(node.value) + "." + node.attr).lstrip(".")
    return node.id if isinstance(node, ast.Name) else ""


def _starts_a_process(call):
    name = _dotted(call.func)
    return (name in ("os.system", "os.popen", "system", "popen", "asyncio.create_subprocess_shell", "pty.spawn")
            or name.startswith(("os.exec", "os.spawn", "os.posix_spawn", "subprocess.")))


def _strings(node):
    return [n.value for n in ast.walk(node) if isinstance(n, ast.Constant) and isinstance(n.value, str)]


def shell_gh_sites(modules):
    """(file, line) of every string naming gh as a command that a module runs through a shell or a process call:
    an argument of os.system, os.popen, os.exec*, subprocess.* and the like, or a `sh -c` command line."""
    sites = []
    for stem in modules.names:
        for node in ast.walk(modules.tree(stem)):
            if isinstance(node, ast.Call) and _starts_a_process(node):
                named = [text for arg in node.args + [k.value for k in node.keywords] for text in _strings(arg)]
            elif isinstance(node, (ast.List, ast.Tuple)) and node.elts and isinstance(node.elts[0], ast.Constant) \
                    and str(node.elts[0].value).rsplit("/", 1)[-1] in SHELLS and "-c" in _strings(node):
                named = _strings(node)
            else:
                continue
            if any(GH_WORD.search(text) for text in named):
                sites.append("%s.py:%d (runs gh through a shell or a process call)" % (stem, node.lineno))
    return sites


@pytest.mark.tree_audit("the modules under veri/, for every place that names the gh command")
def test_every_gh_command_line_a_veri_module_names_goes_through_github_bounded_or_carries_no_body_issue_3960(
        veri_modules_index):
    stray = ["%s:%d (%s)" % (file, line, name) for file, name, line in gh_sites(veri_modules_index)
             if (file, name) not in GH_SITES] + shell_gh_sites(veri_modules_index)

    assert stray == [], "a gh call outside github.bounded would post unredacted: " + ", ".join(stray)


def test_published_redacts_a_local_path_only_at_a_path_boundary_and_keeps_its_trailing_punctuation_4270(
        github, monkeypatch, tmp_path):
    # Another account's home, and this run's temp directory pinned under tmp_path: only the pattern is under test.
    monkeypatch.setenv("HOME", "/Users/someone-else")
    monkeypatch.setenv("TMPDIR", str(tmp_path))
    monkeypatch.setattr("tempfile.tempdir", str(tmp_path))
    monkeypatch.chdir(tmp_path)
    kept = ("/tmpfile /homepage https://example.com/home/tmp/x skills/tdd/scripts/veri/github.py "
            ".tdd/wt/7/.tdd/issue-7.md 1/2")
    text = kept + " path=/tmp/x, /Users/someone/x.py, /home/someone/y.py; /Users/someone/z.md: /home/someone/w.py."

    assert github.published(text) == kept + " path=<tmp>/x, <path>, <path>; <path>: <path>."


def test_published_redacts_a_system_volumes_data_path_like_its_users_path_4270(github, monkeypatch, tmp_path):
    monkeypatch.setenv("HOME", "/Users/someone-else")
    monkeypatch.setenv("TMPDIR", str(tmp_path))
    monkeypatch.setattr("tempfile.tempdir", str(tmp_path))
    monkeypatch.chdir(tmp_path)

    assert github.published("/System/Volumes/Data/Users/bob/q") == github.published("/Users/bob/q") == "<path>"
