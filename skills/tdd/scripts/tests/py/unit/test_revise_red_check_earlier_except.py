"""A revise-red prompt's check-earlier command carries one --except per case the step's reroutes named."""
import importlib
import json


def _check_earlier_line(prompt):
    return [line.strip() for line in prompt.splitlines() if "tests-frozen.sh check-earlier" in line]


def test_3434_revise_red_prompt_excepts_each_case_a_reroute_named(tmp_path, capsysbinary, monkeypatch):
    monkeypatch.setenv("VERI_ISSUE", "3434")
    monkeypatch.chdir(tmp_path)
    build_develop_prompt = importlib.import_module("veri.build_develop_prompt")
    spec = tmp_path / "spec.md"
    spec.write_bytes(b"# spec\n")
    reason = tmp_path / "reason.md"
    reason.write_bytes(b"rejected\n")
    step = "pin the thing"
    argv = ["revise", "red", str(spec), step, "make test", str(reason)]

    def build():
        code = build_develop_prompt.main(argv)
        out, _ = capsysbinary.readouterr()
        assert code == 0
        return _check_earlier_line(out.decode())

    plain = build()
    (tmp_path / ".tdd").mkdir()
    events = [{"event": "reroute", "step": step, "kind": kind, "case": case}
              for kind, case in (("red", "a/test_x.py::test_one"), ("repair", "b/test_y.py::test_two"))]
    events.append({"event": "reroute", "step": "another step", "kind": "red", "case": "c/test_z.py::test_other"})
    (tmp_path / ".tdd" / "events.jsonl").write_text("".join(json.dumps(e) + "\n" for e in events))
    rerouted = build()

    assert (any("--except" in line for line in plain),
            [line.count("--except a/test_x.py::test_one --except b/test_y.py::test_two") for line in rerouted],
            any("test_z" in line for line in rerouted)) == (False, [1], False)


def test_3434_revise_red_prompt_excepts_a_supersede_case_once_and_skips_caseless_reroutes(
        tmp_path, capsysbinary, monkeypatch):
    monkeypatch.setenv("VERI_ISSUE", "3434")
    monkeypatch.chdir(tmp_path)
    build_develop_prompt = importlib.import_module("veri.build_develop_prompt")
    (tmp_path / "spec.md").write_bytes(b"# spec\n")
    (tmp_path / "reason.md").write_bytes(b"rejected\n")
    step = "pin the thing"
    (tmp_path / ".tdd").mkdir()
    events = [{"event": "reroute", "step": step, "kind": "supersede", "case": "a/test_x.py::test_one"},
              {"event": "reroute", "step": step, "kind": "supersede", "case": "a/test_x.py::test_one"},
              {"event": "reroute", "step": step, "kind": "supersede"}]
    (tmp_path / ".tdd" / "events.jsonl").write_text("".join(json.dumps(e) + "\n" for e in events))

    code = build_develop_prompt.main(["revise", "red", "spec.md", step, "make test", "reason.md"])
    out, _ = capsysbinary.readouterr()
    lines = _check_earlier_line(out.decode())

    assert (code, [line.count("--except") for line in lines],
            [line.count("--except a/test_x.py::test_one") for line in lines]) == (0, [1], [1])
