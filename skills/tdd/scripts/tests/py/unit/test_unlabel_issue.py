"""In-process case for veri/unlabel_issue.py, the module unlabel-issue.sh is a shim over."""
import importlib
import subprocess


def _claim_call(args):
    """The taken:<lane> label's create and add calls, answered 0 and left unasserted; None for any other call."""
    joined = " ".join(args)
    if args[:3] == ["gh", "label", "create"] or "--add-label" in args:
        return subprocess.CompletedProcess(args, 0, "", "")
    if args[:3] == ["gh", "api", "-X"] and args[3] == "POST" or args[:2] == ["gh", "api"] and "/labels" in joined and "DELETE" not in args and "-X" not in args:
        return subprocess.CompletedProcess(args, 0, "{}", "")
    return None


def test_main_1656_removes_the_opt_in_label_so_the_issue_is_unlisted_and_a_label_already_absent_exits_0(monkeypatch, capsys):
    unlabel_issue = importlib.import_module("veri.unlabel_issue")
    monkeypatch.setenv("VERI_GH_DRIVER", "auto")
    labels = {"7": {"ready-for-agent", "bug"}, "8": {"bug"}}

    def fake_run(args, **kwargs):
        args = [str(arg) for arg in args]
        joined = " ".join(args)
        claim = _claim_call(args)
        if claim:
            return claim
        if args[:3] == ["gh", "api", "-X"] and args[3] == "DELETE":
            number, _, name = args[4].partition("/issues/")[2].partition("/labels/")
            if name not in labels[number]:
                return subprocess.CompletedProcess(args, 1, "", "gh: Label does not exist (HTTP 404)\n")
            labels[number].discard(name)
            return subprocess.CompletedProcess(args, 0, "[]", "")
        if args[:3] == ["gh", "issue", "edit"] and "--remove-label" in args:
            labels[args[3]].discard(args[args.index("--remove-label") + 1])
            return subprocess.CompletedProcess(args, 0, "", "")
        raise AssertionError("unexpected call: %s" % joined)

    monkeypatch.setattr(subprocess, "run", fake_run)

    carrying = unlabel_issue.main(["7"])
    carrying_left = set(labels["7"])
    bare = unlabel_issue.main(["8"])

    assert (carrying, carrying_left, bare, labels["8"], capsys.readouterr().err) == (0, {"bug"}, 0, {"bug"}, "")


def _deleting(monkeypatch, answer):
    """Fake gh: records each DELETE's path and answers it with `answer` (returncode, stderr)."""
    deleted = []

    def fake_run(args, **kwargs):
        args = [str(arg) for arg in args]
        claim = _claim_call(args)
        if claim:
            return claim
        if args[:4] != ["gh", "api", "-X", "DELETE"]:
            raise AssertionError("unexpected call: %s" % " ".join(args))
        deleted.append(args[4])
        return subprocess.CompletedProcess(args, answer[0], "", answer[1])

    monkeypatch.setattr(subprocess, "run", fake_run)
    return deleted


def test_main_1656_removes_the_label_veri_label_names_not_the_default_one(monkeypatch, capsys):
    unlabel_issue = importlib.import_module("veri.unlabel_issue")
    monkeypatch.setenv("VERI_LABEL", "veri ok")
    deleted = _deleting(monkeypatch, (0, ""))

    code = unlabel_issue.main(["7"])

    assert (code, deleted, capsys.readouterr().err) == (0, ["repos/{owner}/{repo}/issues/7/labels/veri%20ok"], "")


def test_main_1656_exits_2_and_echoes_gh_when_the_removal_fails_with_anything_but_a_404(monkeypatch, capsys):
    unlabel_issue = importlib.import_module("veri.unlabel_issue")
    _deleting(monkeypatch, (1, "gh: Server Error (HTTP 502)\n"))

    code = unlabel_issue.main(["7"])

    assert (code, capsys.readouterr().err) == (2, "gh: Server Error (HTTP 502)\n")


def test_main_1672_exits_2_naming_a_non_numeric_issue_argument_and_asks_gh_nothing(monkeypatch, capsys):
    unlabel_issue = importlib.import_module("veri.unlabel_issue")
    deleted = _deleting(monkeypatch, (1, "gh: Not Found (HTTP 404)\n"))

    code = unlabel_issue.main(["abc"])

    err = capsys.readouterr().err
    assert (code, deleted, "abc" in err) == (2, [], True)


def test_main_1672_exits_2_naming_a_nonexistent_issue_while_an_existing_issue_without_the_label_exits_0(monkeypatch, capsys):
    unlabel_issue = importlib.import_module("veri.unlabel_issue")
    labels = {"8": {"bug"}}

    def fake_run(args, **kwargs):
        args = [str(arg) for arg in args]
        claim = _claim_call(args)
        if claim and args[-1].partition("/issues/")[2].partition("/")[0] in labels or args[:3] == ["gh", "label", "create"]:
            return claim
        if args[:2] != ["gh", "api"]:
            raise AssertionError("unexpected call: %s" % " ".join(args))
        path = args[-1].partition("/issues/")[2]
        number = path.partition("/")[0]
        if number not in labels:
            return subprocess.CompletedProcess(args, 1, "", "gh: Not Found (HTTP 404)\n")
        if "DELETE" in args:
            return subprocess.CompletedProcess(args, 1, "", "gh: Label does not exist (HTTP 404)\n")
        return subprocess.CompletedProcess(args, 0, "{}", "")

    monkeypatch.setattr(subprocess, "run", fake_run)

    existing = unlabel_issue.main(["8"])
    existing_err = capsys.readouterr().err
    missing = unlabel_issue.main(["999"])
    missing_err = capsys.readouterr().err

    assert (existing, existing_err, missing, "999" in missing_err) == (0, "", 2, True)


def test_main_1672_exits_2_naming_the_unanswered_removal_request_when_gh_gets_no_answer(monkeypatch, capsys):
    unlabel_issue = importlib.import_module("veri.unlabel_issue")
    _deleting(monkeypatch, (1, "error connecting to api.github.com\n"))

    code = unlabel_issue.main(["7"])

    err = capsys.readouterr().err
    assert (code, "unlabel-issue.sh" in err, "#7" in err) == (2, True, True)


def test_main_1974_removes_the_label_through_the_port_and_starts_no_gh_process_itself(monkeypatch, capsys):
    unlabel_issue = importlib.import_module("veri.unlabel_issue")
    github = importlib.import_module("veri.github")
    monkeypatch.setenv("VERI_GH_DRIVER", "rest")
    monkeypatch.delenv("VERI_GH_JSON", raising=False)
    ported = []

    def port_launch(*args, **kwargs):
        ported.append(list(args))
        return subprocess.CompletedProcess(args, 0, "", "")

    def own_launch(args, **kwargs):
        raise AssertionError("unlabel_issue started a process itself: %s" % " ".join(map(str, args)))

    monkeypatch.setattr(github, "_gh", port_launch)
    monkeypatch.setattr(subprocess, "run", own_launch)

    code = unlabel_issue.main(["7"])

    deletions = [call for call in ported if "DELETE" in call]
    assert (code, deletions, capsys.readouterr().err) == (
        0, [["api", "-X", "DELETE", "repos/{owner}/{repo}/issues/7/labels/ready-for-agent"]], "")


def test_main_2030_adds_the_taken_lane_label_named_after_the_text_after_the_last_colon_of_veri_label_or_main(monkeypatch):
    unlabel_issue = importlib.import_module("veri.unlabel_issue")
    monkeypatch.setenv("VERI_GH_DRIVER", "auto")
    calls = []

    def fake_run(args, **kwargs):
        args = [str(arg) for arg in args]
        calls.append(args)
        return subprocess.CompletedProcess(args, 0, "{}", "")

    monkeypatch.setattr(subprocess, "run", fake_run)

    def taken_after(label):
        calls.clear()
        if label is None:
            monkeypatch.delenv("VERI_LABEL", raising=False)
        else:
            monkeypatch.setenv("VERI_LABEL", label)
        code = unlabel_issue.main(["7"])
        added = sorted({word[len("labels[]="):] for call in calls if call[:4] == ["gh", "api", "-X", "POST"]
                        for word in call if word.startswith("labels[]=taken:")})
        label_writes = [call for call in calls if call[:3] in (["gh", "label", "create"], ["gh", "label", "edit"])]
        return code, added, label_writes

    assert [taken_after(None), taken_after("ready-for-agent"), taken_after("ready-for-agent:mu")] == [
        (0, ["taken:main"], []), (0, ["taken:main"], []), (0, ["taken:mu"], [])]


def test_main_2030_creates_the_taken_lane_label_in_the_repository_when_absent_so_the_add_succeeds_and_the_issue_carries_it(monkeypatch, capsys):
    unlabel_issue = importlib.import_module("veri.unlabel_issue")
    monkeypatch.setenv("VERI_GH_DRIVER", "auto")
    monkeypatch.setenv("VERI_LABEL", "ready-for-agent:mu")
    repository_labels = {"bug"}
    issue_labels = {"7": {"ready-for-agent:mu"}}

    def fake_run(args, **kwargs):
        args = [str(arg) for arg in args]
        if args[:2] == ["gh", "api"] and "/labels/" in args[-1] and "-X" not in args:
            if args[-1].rpartition("/labels/")[2].replace("%3A", ":") in repository_labels:
                return subprocess.CompletedProcess(args, 0, "{}", "")
            return subprocess.CompletedProcess(args, 1, "", "gh: Not Found (HTTP 404)\n")
        if args[:3] == ["gh", "label", "create"]:
            repository_labels.add(args[3])
            return subprocess.CompletedProcess(args, 0, "", "")
        if args[:4] == ["gh", "api", "-X", "DELETE"]:
            issue_labels["7"].discard(args[4].rpartition("/labels/")[2].replace("%3A", ":"))
            return subprocess.CompletedProcess(args, 0, "[]", "")
        if args[:4] == ["gh", "api", "-X", "POST"]:
            added = [word[len("labels[]="):] for word in args if word.startswith("labels[]=")]
            if not set(added) <= repository_labels:
                return subprocess.CompletedProcess(args, 1, "", "gh: Validation Failed (HTTP 422)\n")
            issue_labels["7"].update(added)
            return subprocess.CompletedProcess(args, 0, "[]", "")
        raise AssertionError("unexpected call: %s" % " ".join(args))

    monkeypatch.setattr(subprocess, "run", fake_run)

    code = unlabel_issue.main(["7"])

    assert (code, issue_labels["7"], "taken:mu" in repository_labels, capsys.readouterr().err) == (
        0, {"taken:mu"}, True, "")


def test_main_2030_exits_0_when_the_issue_already_carries_the_taken_lane_label_and_leaves_it_on_the_issue(monkeypatch, capsys):
    unlabel_issue = importlib.import_module("veri.unlabel_issue")
    monkeypatch.setenv("VERI_GH_DRIVER", "auto")
    monkeypatch.setenv("VERI_LABEL", "ready-for-agent:mu")
    issue_labels = {"7": {"taken:mu", "bug"}}

    def fake_run(args, **kwargs):
        args = [str(arg) for arg in args]
        if args[:2] == ["gh", "api"] and "/labels/" in args[-1] and "-X" not in args:
            return subprocess.CompletedProcess(args, 0, "{}", "")
        if args[:3] == ["gh", "label", "create"]:
            return subprocess.CompletedProcess(args, 0, "", "")
        if args[:4] == ["gh", "api", "-X", "DELETE"]:
            name = args[4].rpartition("/labels/")[2].replace("%3A", ":")
            if name not in issue_labels["7"]:
                return subprocess.CompletedProcess(args, 1, "", "gh: Label does not exist (HTTP 404)\n")
            issue_labels["7"].discard(name)
            return subprocess.CompletedProcess(args, 0, "[]", "")
        if args[:4] == ["gh", "api", "-X", "POST"]:
            issue_labels["7"].update(word[len("labels[]="):] for word in args if word.startswith("labels[]="))
            return subprocess.CompletedProcess(args, 0, "[]", "")
        raise AssertionError("unexpected call: %s" % " ".join(args))

    monkeypatch.setattr(subprocess, "run", fake_run)

    code = unlabel_issue.main(["7"])

    assert (code, issue_labels["7"], capsys.readouterr().err) == (0, {"taken:mu", "bug"}, "")


def test_main_2030_exits_2_naming_the_taken_label_when_gh_gets_no_answer_to_creating_it_or_to_adding_it(monkeypatch, capsys):
    unlabel_issue = importlib.import_module("veri.unlabel_issue")
    monkeypatch.setenv("VERI_GH_DRIVER", "auto")

    def silent_on(step):
        def fake_run(args, **kwargs):
            args = [str(arg) for arg in args]
            if args[:2] == ["gh", "api"] and "/labels/" in args[-1] and "-X" not in args:
                if step == "create":
                    return subprocess.CompletedProcess(args, 1, "", "gh: Not Found (HTTP 404)\n")
                return subprocess.CompletedProcess(args, 0, "{}", "")
            if args[:4] == ["gh", "api", "-X", "DELETE"]:
                return subprocess.CompletedProcess(args, 0, "[]", "")
            asked = "create" if args[:3] == ["gh", "label", "create"] else "add"
            if asked == step:
                return subprocess.CompletedProcess(args, 1, "", "error connecting to api.github.com\n")
            return subprocess.CompletedProcess(args, 0, "[]", "")

        monkeypatch.setattr(subprocess, "run", fake_run)
        code = unlabel_issue.main(["7"])
        err = capsys.readouterr().err
        return code, "unlabel-issue.sh" in err, "taken:main" in err, "#7" in err

    assert [silent_on("create"), silent_on("add")] == [(2, True, True, True)] * 2



def test_main_2301_creates_a_missing_taken_lane_label_once_with_a_fixed_colour_and_description_and_no_force_and_exits_2_when_the_lookup_gets_no_answer(monkeypatch, capsys):
    unlabel_issue = importlib.import_module("veri.unlabel_issue")
    monkeypatch.setenv("VERI_GH_DRIVER", "auto")

    def claim(lookup):
        calls = []

        def fake_run(args, **kwargs):
            args = [str(arg) for arg in args]
            calls.append(args)
            if args[:2] == ["gh", "api"] and "/labels/" in args[-1] and "-X" not in args:
                return lookup(args)
            return subprocess.CompletedProcess(args, 0, "[]", "")

        monkeypatch.setattr(subprocess, "run", fake_run)
        code = unlabel_issue.main(["7"])
        return code, calls, capsys.readouterr().err

    code, calls, _ = claim(lambda args: subprocess.CompletedProcess(args, 1, "", "gh: Not Found (HTTP 404)\n"))
    creates = [call for call in calls if call[:3] == ["gh", "label", "create"]]
    adds = [call for call in calls if "labels[]=taken:main" in call]
    create = creates[0] if creates else []
    colour = create[create.index("--color") + 1] if "--color" in create else ""
    description = create[create.index("--description") + 1] if "--description" in create else ""
    ordered = bool(creates) and bool(adds) and calls.index(creates[0]) < calls.index(adds[0])
    assert (code, len(creates), len(colour) == 6 and set(colour) <= set("0123456789abcdefABCDEF"), bool(description),
            "--force" in create, ordered) == (0, 1, True, True, False, True)

    code, calls, err = claim(lambda args: subprocess.CompletedProcess(args, 1, "", "error connecting to api.github.com\n"))
    assert (code, "taken:main" in err, "#7" in err, [call for call in calls if call[:3] == ["gh", "label", "create"]]) == (2, True, True, [])
