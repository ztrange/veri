"""When a case in the current tree is "the same case" as one a frozen record names, and the digest of the helpers it calls.

"The same case" is decided by the record's body digest, never by position: a case is the one recorded when
its body (or one of its `parents[N]` root-lookup variants, for a file that moved to another depth) hashes to
a recorded digest. A case missing under its recorded name is the same case when it was only renamed (its
text unchanged but for the name, read off the file's history), and a file missing under its recorded name is
the same file when a visible copy elsewhere in the tree holds the case. The assertions a case leans on in
the helpers it calls are part of its identity: `helper_digest` is the digest of those assertion lines.

Interface (a function says what it touches: text only, the tree's files, or case_history):
  squeezed(text)                          `text` with every run of whitespace dropped. Text only.
  assertion_lines(body)                   the squeezed lines of `body` that start (after indentation) with
                                          assert, expect(, t.Fatal, t.Error, t.Fail or require. Text only.
  checked_lines(body)                     assertion_lines(body), but a t.Fatal or t.Error line whose previous non-blank
                                          line is an `if <cond> {` guard is that guard, squeezed, then the call's name
                                          (its text before the first `(`), message dropped: a changed condition changes
                                          the line, a reworded message does not. An unguarded line stays whole. Text only.
  bodies_of(text, case)                   every body of the cases named `case` in test source `text`, in file
                                          order; [] when none. Text only; UnclosedCase from case_reader.cut_cases
                                          when a JS call never closes.
  helpers_in(text, body, legacy=False, transitive=True)
                                          the definitions in `text` (python def, Go func, JS function or arrow
                                          const) that `body` calls by name, each from its head to the next
                                          column-0 definition keyword; a python `test*` def and a Go `Test*` func
                                          are never helpers. `transitive` also follows the calls the helpers
                                          make, each helper once by name, so a recursive helper or a pair calling
                                          each other ends the walk (#4642); `transitive=False` is the formula
                                          records before it were written with. `legacy` ends a definition only at
                                          `func` and is never transitive, the formula older records were written
                                          with. "" when none. Text only.
  helper_digest(text, body, legacy=False, transitive=True)
                                          the body digest of the sorted assertion lines of helpers_in. Text only.
  root_variants(body)                     `body`, then `body` with each `parents[N]` rewritten to depth 0..9. Text only.
  as_recorded(body, digests)              the first of root_variants(body) whose digest is in `digests`, else
                                          `body`. Text only.

  path_holding(case, digests, only=None) the first file under the current directory (hidden directories skipped; only the
                                          basename `only` when given) one of whose `case` bodies, or a root variant of
                                          one, hashes into `digests`, as os.walk spells it ("./tests/x.py"); None when
                                          none does. Reads the tree's files; OSError when one cannot be opened.
  moved_path(name, case, digests)         `name` while that file holds a body of `case`, whatever its digest (a case
                                          changed in place is judged there, never at a copy elsewhere); else the
                                          path_holding of a file of the same basename, else of any file, else `name`.
                                          Reads the tree's files; UnclosedCase from case_reader when `name` cannot be cut.

  renamed_to(name, case, digest, text, consumed)
                                          the case of `text` that is the recorded `case` of file `name` but for its
                                          name: the case_history revision (newest first) that held `case` at `digest`
                                          is compared with `text` by renamed_case, skipping names that revision held
                                          and names in `consumed`; the answer is added to `consumed`. None when no
                                          revision held that body or no case of `text` fits. Asks case_history.
  changed_by_refactor(name, case)         True when the newest commit that changed `case` in `name` has a subject
                                          starting "refactor:". False when `case` is not at HEAD, was never changed,
                                          or the history cannot be read (OSError). Asks case_history.
  called_helpers(rev, name, body, transitive=True)
                                          helpers_in of the file `name` at `rev` (read quietly), then, for a Go
                                          `_test.go` file only, of every other `_test.go` file in its directory at
                                          `rev` (one package, one namespace), each name taken once, the case's own file
                                          first. A Python or JS case never reads a sibling test file: its helper may be
                                          imported from anywhere, and a sibling's same-named one is not it. "" when git
                                          can show none of them. Asks case_history.
  helper_digest_beside(name, text, body, transitive=True)
                                          helper_digest over `text` (the file `name`) plus, for a Go `_test.go` file,
                                          the tree's other `_test.go` files in its directory, each name taken once,
                                          `text` first: the digest called_helpers' definitions give. Reads the tree's
                                          files; a sibling that cannot be read adds nothing.

Error modes: only changed_by_refactor catches anything (OSError from case_history, answered False). The rest let
case_reader's UnclosedCase, a file's OSError and case_history's OSError through to the caller, who decides.
"""
import os
import re

import case_history
import renamed_case
from case_reader import cut_cases
from frozen_record import body_digest


def squeezed(text):
    return re.sub(r"\s+", "", text)


_ASSERTION_STARTS = ("assert", "expect(", "t.Fatal", "t.Error", "t.Fail", "require.")


def assertion_lines(body):
    return [squeezed(line) for line in body.splitlines() if line.lstrip().startswith(_ASSERTION_STARTS)]


def checked_lines(body):
    lines, guard = [], ""
    for line in body.splitlines():
        text = line.strip()
        if not text:
            continue
        if text.startswith(_ASSERTION_STARTS):
            guarded = guard and text.startswith(("t.Fatal", "t.Error"))
            lines.append(guard + squeezed(text).split("(")[0] if guarded else squeezed(text))
        guard = squeezed(text) if re.match(r"if\s.*\{$", text) else ""
    return lines


def bodies_of(text, case):
    return [b for c, b in cut_cases(text) if c == case]


_HELPER_NAME = r"^(?:(?:function|func|def)\s+(?:\([^)]*\)\s*)?(\w+)|const\s+(\w+)\s*=\s*(?:async\s*)?(?:\([^)]*\)|\w+)\s*=>)"


def _named_helpers(text, body, legacy=False):
    """(name, definition) of each helper in `text` that `body` calls, in file order."""
    helpers = []
    stop = r"func" if legacy else r"(?:function|func|def|const)"
    rest = re.compile(r"(?:(?!%s\b).*\n?)*" % stop)
    for head in re.finditer(_HELPER_NAME + r"[^\n]*\n", text, re.M):
        definition = head.group() + rest.match(text, head.end()).group()
        name = head.group(1) or head.group(2)
        keyword = definition.split(None, 1)[0]
        collected = (keyword == "def" and name.startswith("test")) or (keyword == "func" and name.startswith("Test"))
        if not collected and re.search(r"\b%s\(" % name, body):
            helpers.append((name, definition))
    return helpers


def _own_lines(definition):
    """`definition` cut at its first column-0 line that is neither blank nor a closing bracket: a Python def ends at
    its dedent, though _named_helpers' definition runs on to the next column-0 def, past any class between."""
    lines = definition.split("\n")
    for k, line in enumerate(lines[1:], 1):
        if line and not line[0].isspace() and line[0] not in "})]":
            return "\n".join(lines[:k])
    return definition


def _walk(texts, body):
    """The definitions of every helper `body` calls in `texts`, directly or through another helper it calls: each
    helper once, by name (a visited set, so a helper that calls itself or a pair calling each other ends the walk)."""
    seen, found, pending = set(), [], [body]
    while pending:
        calling = pending.pop()
        for text in texts:
            for name, definition in _named_helpers(text, calling):
                if name not in seen:
                    seen.add(name)
                    found.append(definition)
                    pending.append(_own_lines(definition))
    return found


def helpers_in(text, body, legacy=False, transitive=True):
    if transitive and not legacy:
        return "\n".join(_walk([text], body))
    return "\n".join(definition for _, definition in _named_helpers(text, body, legacy))


def helper_digest(text, body, legacy=False, transitive=True):
    return body_digest("\n".join(sorted(assertion_lines(helpers_in(text, body, legacy, transitive)))))


def root_variants(body):
    yield body
    for k in range(10):
        yield re.sub(r"parents\[\d+\]", "parents[%d]" % k, body)


def as_recorded(body, digests):
    return next((v for v in root_variants(body) if body_digest(v) in digests), body)


def _text_holds(text, case, digests):
    return any(body_digest(v) in digests for body in bodies_of(text, case) for v in root_variants(body))


def path_holding(case, digests, only=None):
    for top, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for file in files:
            if only is not None and file != only:
                continue
            path = os.path.join(top, file)
            with open(path, encoding="utf-8", errors="replace") as handle:
                if _text_holds(handle.read(), case, digests):
                    return path
    return None


def _has_case(path, case):
    try:
        with open(path, encoding="utf-8", errors="replace") as handle:
            text = handle.read()
    except OSError:
        return False
    return bool(bodies_of(text, case))


def moved_path(name, case, digests):
    if _has_case(name, case):
        return name
    return (
        path_holding(case, digests, only=os.path.basename(name))
        or path_holding(case, digests)
        or name
    )


def renamed_to(name, case, digest, text, consumed):
    for rev in case_history.revisions(name):
        held = case_history.cases_at(rev, name)
        if case in held and body_digest(held[case]) == digest:
            other = renamed_case.renamed_to(case, case_history.text_at(rev, name), text, set(held) | consumed)
            if other:
                consumed.add(other)
            return other
    return None


def changed_by_refactor(name, case):
    try:
        if case not in case_history.cases_at("HEAD", name):
            return False
        revs = case_history.revisions(name)
        history = [case_history.cases_at(rev, name).get(case) for rev in revs]
    except OSError:
        return False
    for rev, now, before in zip(revs, history, history[1:]):
        if now != before:
            return case_history.subject(rev).startswith("refactor:")
    return False


def _go_siblings(name, paths):
    if not name.endswith("_test.go"):
        return []
    return [path for path in paths if path != os.path.normpath(name) and path.endswith("_test.go")]


def _first_named(texts, body, transitive=True):
    if transitive:
        return "\n".join(_walk(texts, body))
    seen, helpers = set(), []
    for text in texts:
        for helper, definition in _named_helpers(text, body):
            if helper not in seen:
                seen.add(helper)
                helpers.append(definition)
    return "\n".join(helpers)


def called_helpers(rev, name, body, transitive=True):
    siblings = _go_siblings(name, case_history.paths_at(rev, os.path.dirname(name)))
    return _first_named([case_history.text_at(rev, path, quiet=True) for path in [name] + siblings], body, transitive)


def _tree_text(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as handle:
            return handle.read()
    except OSError:
        return ""


def helper_digest_beside(name, text, body, transitive=True):
    directory = os.path.dirname(name)
    listed = sorted(os.path.normpath(os.path.join(directory, f)) for f in os.listdir(directory or "."))
    siblings = _go_siblings(os.path.normpath(name), listed)
    helpers = _first_named([text] + [_tree_text(path) for path in siblings], body, transitive)
    return body_digest("\n".join(sorted(assertion_lines(helpers))))
