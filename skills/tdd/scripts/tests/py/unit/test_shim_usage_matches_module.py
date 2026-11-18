"""A shim's `# Usage:` header and its module's `USAGE` (what `--help` and a refusal print) describe the same invocations."""
import ast
import pathlib
import re

import pytest

SHIM_EXEC = re.compile(r'^exec (?:python3|"\$py") .*/(veri/[\w-]+\.py)"', re.MULTILINE)
STOP = re.compile(r"(Exit|Exits|Env)\b|exit:", re.I)

# Pairs whose texts differ and that cannot be made to agree without editing graded prose (skills/tdd/SCRIPTS.md audits
# each shim header against its synopsis). A ratchet: the dict may shrink, never grow; an entry that now agrees fails.
EXEMPT = {
    "status.sh": "the module also takes `--report` and `--recover dev [--lane <lane>]`; SCRIPTS.md's synopsis lists"
                 " `--report` only and `--recover` in prose, so the shim header cannot add them",
    "stop-reason.sh": "the module's USAGE also describes the first output line (running | done <pr> | bailed …); adding those"
                      " words to the shim header would put verbs in it that SCRIPTS.md's synopsis does not have",
}


def _synopsis(text, name):
    """The invocation lines of a shim's `# Usage:` block, whitespace collapsed, `usage:` prefix dropped.

    Stops at the `Exit:`/`Env:` lines and at the first line that is prose rather than an invocation of `name`; an
    invocation led by an environment assignment (`VERI_X=1 name.sh`) is a variant of the one before it and is left out.
    """
    block, found = [], False
    for line in text.splitlines():
        if found and (re.fullmatch(r"#\s*", line) or not line.startswith("#")):
            break
        if not found and re.match(r"# *usage:", line, re.I):
            found = True
        if not found:
            continue
        body = re.sub(r"^usage:\s*", "", re.sub(r"^# ?", "", line).strip(), flags=re.I)
        if STOP.match(body):
            break
        if re.match(r"[A-Z_]+=", body):
            continue
        if block and not (body.startswith(name) or body.startswith("|")):
            break
        block.append(re.split(r"\s{2,}", body)[0])
    return " ".join(" ".join(block).split())


def _usage(tree):
    """The module's `USAGE` literal, whitespace collapsed, `usage:` prefix dropped; None when it is not a literal."""
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "USAGE" for t in node.targets):
            try:
                value = ast.literal_eval(node.value)
            except ValueError:
                return None
            value = value.decode() if isinstance(value, bytes) else str(value)
            return " ".join(re.sub(r"^(?:[\w.-]+: )?usage:\s*", "", value.strip(), flags=re.I).split())
    return None


def _signature(text, name):
    """The flags, placeholders and verbs of a synopsis in order: remarks in parentheses and `#` comments are not part of it."""
    text = text.replace(name, " ").split(" # ")[0]
    while re.search(r"\([^()]*\)", text):
        text = re.sub(r"\([^()]*\)", " ", text)
    return re.findall(r"--[a-z][\w-]*|<[^>]*>|(?<![\w<-])[a-z][a-z0-9-]*(?![\w>-])", text)


def _pairs(index):
    from conftest import SCRIPTS

    for shim in sorted(SCRIPTS.glob("*.sh")):
        text = shim.read_text()
        match = SHIM_EXEC.search(text)
        if not match:
            continue
        synopsis, usage = _synopsis(text, shim.name), _usage(index.tree(pathlib.PurePath(match.group(1)).stem))
        if synopsis and usage:
            yield shim.name, synopsis, usage


def _differing(index):
    return {name: (synopsis, usage) for name, synopsis, usage in _pairs(index)
            if synopsis != usage and _signature(synopsis, name) != _signature(usage, name)}


@pytest.mark.tree_audit("every shim of skills/tdd/scripts")
def test_enough_shims_are_comparable_for_the_audit_to_mean_something(veri_modules_index):
    assert len(list(_pairs(veri_modules_index))) >= 60


@pytest.mark.tree_audit("every shim of skills/tdd/scripts")
def test_a_shims_usage_header_and_its_modules_usage_name_the_same_invocations(veri_modules_index):
    differing = _differing(veri_modules_index)

    assert not set(differing) - set(EXEMPT), "\n".join(
        f"{name}:\n  shim:   {shim}\n  module: {module}" for name, (shim, module) in sorted(differing.items())
        if name not in EXEMPT)
    assert not set(EXEMPT) - set(differing), f"exemptions that now agree, remove them: {sorted(set(EXEMPT) - set(differing))}"
