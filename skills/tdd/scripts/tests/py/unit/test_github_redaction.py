"""In-process cases for github.redact, the one function every body veri hands gh passes through (#3960, #3968).

Every token here is built from a documented shape with an obviously fake body; none is read from the environment."""
import ast
import base64
import importlib

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


def test_redact_replaces_a_token_wrapped_across_a_line_break_or_a_json_newline_escape_issue_3960(github, monkeypatch):
    monkeypatch.setenv("GH_TOKEN", "fake-gh-token-value")
    token = "ghp_" + FAKE * 3 + "Zz"
    wrapped = "x %s\n%s rest\nNext line\n" % (token[:20], token[20:])
    crlf = "%s\r\n%s\r\n" % (token[:10], token[10:])
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
    ("github.py", "<module>"): "the shape prefix gh of the token patterns",
    ("github.py", "bounded"): "the redaction itself",
    ("github.py", "run_gh"): "through bounded",
    ("github.py", "gh_probe"): "through bounded",
    ("github.py", "rate_limit_reset"): "through bounded",
    ("network_guard.py", "<module>"): "the names it refuses, starting nothing",
    ("preflight.py", "issue_body"): "a read of the issue body",
    ("preflight.py", "check_environment"): "gh api user, a read",
    ("preflight.py", "finish"): "a read of the default branch",
    ("queued_merge.py", "_locked"): "the merge call, which names a pull request and a sha only",
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


@pytest.mark.tree_audit("the modules under veri/, for every place that names the gh command")
def test_every_gh_command_line_a_veri_module_names_goes_through_github_bounded_or_carries_no_body_issue_3960(
        veri_modules_index):
    stray = ["%s:%d (%s)" % (file, line, name) for file, name, line in gh_sites(veri_modules_index)
             if (file, name) not in GH_SITES]

    assert stray == [], "a gh call outside github.bounded would post unredacted: " + ", ".join(stray)
