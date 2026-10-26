"""The green freeze slot fillers of build_develop_prompt.py are read from prompt fragments, not constants."""
import importlib.util

from conftest import SCRIPTS

FREEZE = "_develop-green-freeze-rule.md"
GUARD = "_develop-guard-subject-grant.md"
REPAIR = "_develop-repair-test-edit.md"


def scripts_tree(tmp_path):
    scripts = tmp_path / "scripts"
    (scripts / "veri").mkdir(parents=True)
    module_path = scripts / "veri" / "build_develop_prompt.py"
    module_path.write_bytes((SCRIPTS / "veri" / "build_develop_prompt.py").read_bytes())
    prompts = scripts / "prompts"
    prompts.mkdir()
    (prompts / "develop-green.md").write_bytes(b"[{{FREEZE_RULE}}]{{REPLACES_CASE}}{{SUITE_REPAIR}}\n")
    (prompts / "_develop-shared.md").write_bytes(b"shared\n")
    (prompts / "_develop-green-suite-repair.md").write_bytes(b"sr\n")
    loader = importlib.util.spec_from_file_location("fragments_build_develop_prompt", module_path)
    module = importlib.util.module_from_spec(loader)
    loader.loader.exec_module(module)
    spec = tmp_path / "spec.md"
    spec.write_bytes(b"spec\n")
    return module, scripts / "prompts", str(spec)


def render_green(module, spec, step, capsysbinary):
    code = module.main(["green", spec, step, "make test", "tp", "tid", "make unit"])
    return (code, *capsysbinary.readouterr())


def test_green_freeze_slot_fillers_are_read_from_their_prompt_fragments(tmp_path, capsysbinary):
    module, prompts, spec = scripts_tree(tmp_path)
    (prompts / FREEZE).write_bytes(b"PLANTED-FREEZE\n")
    (prompts / GUARD).write_bytes(b"PLANTED-GUARD\n")
    (prompts / REPAIR).write_bytes(b"PLANTED-REPAIR\n")

    plain = render_green(module, spec, "step", capsysbinary)
    guarded = render_green(module, spec, "step ⟦guard-subject: t.py⟧", capsysbinary)
    repair = render_green(module, spec, "step ⟦suite-repair⟧", capsysbinary)

    assert [(code, b"PLANTED-FREEZE" in out, b"PLANTED-GUARD" in out, b"PLANTED-REPAIR" in out)
            for code, out, _ in (plain, guarded, repair)] == [
        (0, True, False, False),
        (0, True, True, False),
        (0, False, False, True),
    ]


def test_an_include_the_builder_refuses_inside_a_freeze_fragment_exits_2_naming_the_refused_partial(
        tmp_path, capsysbinary):
    module, prompts, spec = scripts_tree(tmp_path)
    (prompts / FREEZE).write_bytes(b"loop {{INCLUDE:%s}}\n" % FREEZE.encode())

    assert render_green(module, spec, "step", capsysbinary) == (
        2, b"", b"partial includes itself: " + str(prompts).encode() + b"/" + FREEZE.encode() + b"\n")


def test_revise_slot_fillers_are_read_from_their_prompt_fragments(tmp_path, capsysbinary):
    module, prompts, spec = scripts_tree(tmp_path)
    (prompts / "develop-revise.md").write_bytes(b"[{{TEST_REWRITE}}][{{WRONG_TEST_REPORT}}][{{WRONG_TEST_FORMAT}}]\n")
    (prompts / "_develop-revise-freeze-production.md").write_bytes(b"fp\n")
    (prompts / "_develop-green-freeze-rule.md").write_bytes(b"fr\n")
    slots = {"test-rewrite-grant": b"PLANTED-GRANT", "test-rewrite-none": b"PLANTED-NONE",
             "test-move-contract-a": b"PLANTED-MOVE", "wrong-test-report": b"PLANTED-REPORT",
             "wrong-test-format": b"PLANTED-FORMAT"}
    for slot, text in slots.items():
        (prompts / f"_develop-{slot}.md").write_bytes(text + b"\n")
    reason = tmp_path / "reason.md"
    reason.write_bytes(b"why\n")

    def render(revised):
        code = module.main(["revise", revised, spec, "step", "make test", str(reason)])
        return (code, *capsysbinary.readouterr())

    red, green, contract_a = render("red"), render("green"), render("contract-a")

    assert [(code, [slot for slot, text in slots.items() if text in out]) for code, out, _ in (red, green, contract_a)] == [
        (0, ["test-rewrite-grant"]),
        (0, ["test-rewrite-none", "wrong-test-report", "wrong-test-format"]),
        (0, ["test-move-contract-a"]),
    ]
