"""A module of veri/ calls a sibling's typed function, never the sibling's `main(argv)`: no command line to build,
no streams to swap and re-parse. The sites that remain are the ratchet below."""
import ast

import pytest

# "caller -> callee": why the site stays. Entries may be removed, never added; the audit also fails when a listed
# site no longer exists, so the entry goes with the call.
SIBLING_MAIN_CALLS = {
    "skill_edit_step -> skill_edit_guard": "its single trivial caller (_captured around skill_edit_guard.main in "
                                           "skill_edit_step.py); skill_edit_guard is edited by another round",
}


def sibling_main_sites(tree, names):
    """The callees whose `main` the module of `tree` reaches: `callee.main` through `import callee [as alias]`,
    or `from callee import main`, for every callee in `names`."""
    aliases, sites = {}, set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name in names:
                    aliases[alias.asname or alias.name] = alias.name
        elif isinstance(node, ast.ImportFrom) and node.module in names and any(a.name == "main" for a in node.names):
            sites.add(node.module)
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and node.attr == "main" and isinstance(node.value, ast.Name) \
                and node.value.id in aliases:
            sites.add(aliases[node.value.id])
    return sites


def test_the_detector_finds_a_call_an_aliased_call_a_bare_reference_and_a_from_import_of_main():
    names = {"parse_verdict", "metrics", "entry"}
    planted = {
        "import parse_verdict\nparse_verdict.main([])\n": {"parse_verdict"},
        "import metrics as m\nm.main(['7'])\n": {"metrics"},
        "import parse_verdict\nrun(parse_verdict.main, [])\n": {"parse_verdict"},
        "from metrics import main\n": {"metrics"},
        "import entry\nentry.run(main, [])\nimport pytest\npytest.main([])\n": set(),
    }

    assert {src: sibling_main_sites(ast.parse(src), names) for src in planted} == planted


@pytest.mark.tree_audit("skills/tdd/scripts/veri")
def test_no_module_reaches_a_siblings_main_beyond_the_listed_ratchet(veri_modules_index):
    names = set(veri_modules_index.names)
    found = {f"{name} -> {callee}"
             for name in veri_modules_index.names
             for callee in sibling_main_sites(veri_modules_index.tree(name), names)}

    assert sorted(found - set(SIBLING_MAIN_CALLS)) == [], "a module reaches a sibling's main; call its typed function"
    assert sorted(set(SIBLING_MAIN_CALLS) - found) == [], "SIBLING_MAIN_CALLS lists a site that no longer exists; remove it"
