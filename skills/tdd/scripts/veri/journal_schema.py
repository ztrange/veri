"""What skills/tdd/JOURNAL.md documents for each event kind, and what writers pass (#audit of journal fields).

Interface, documented side (pure: each takes JOURNAL.md's text, the caller reads the file):
  kinds(text)             the event kinds that have a table row
  fields(text, kind)      the row's key names in table order, () for a "—" row, None for an undocumented kind
  optional(text, kind)    the subset of those keys the row's meaning calls optional or absent

Interface, writer side (pure: takes a module's source text):
  writer_calls(source)    one (line, kind, fields) per call that appends an event, found with `ast`

`kind` is a string literal or a module-level string constant assigned once, else None; `fields` holds only the names written
as a literal `"name=…"` (a constant, an f-string or `%`/`+` expression starting with one). Blind
spots: a computed kind, `**fields`, a field list built in a variable, and events that prose writes
through `event.sh`.
"""
import ast
import re

ROW = re.compile(r"^\|\s*`([a-z][a-z0-9-]*)`\s*\|([^|]*)\|(.*)\|\s*$", re.M)
NAME = re.compile(r"`([A-Za-z_][A-Za-z0-9_]*)`")
OPTIONAL_WORDS = re.compile(r"optional|absent|only", re.I)
FIELD_LITERAL = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)=")

# call shape -> (index of the kind among the positional arguments, index where the fields start)
CALLS = {
    ("event", "mark"): (2, 3), ("event", "append"): (2, 3),
    ("verify", "mark"): (1, 2), ("supervise", "mark"): (2, 3), ("push_branch", "record"): (0, 1),
}
LOCAL_CALLS = {"verify": {"mark": (1, 2)}, "supervise": {"mark": (2, 3)}, "push_branch": {"record": (0, 1)}}


def _row(text, kind):
    return next((m for m in ROW.finditer(text) if m.group(1) == kind), None)


def kinds(text):
    return {m.group(1) for m in ROW.finditer(text)}


def fields(text, kind):
    row = _row(text, kind)
    return None if row is None else tuple(NAME.findall(row.group(2)))


def optional(text, kind):
    row = _row(text, kind)
    if row is None:
        return set()
    names = set()
    for clause in re.split(r"(?<=[.;])\s+", row.group(3)):
        if OPTIONAL_WORDS.search(clause):
            names |= set(NAME.findall(clause))
    return names & set(NAME.findall(row.group(2)))


def _literal(node):
    """The string a node starts with, when it is a literal, f-string, `+` or `%` expression."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.JoinedStr) and node.values:
        return _literal(node.values[0])
    if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Mod)):
        return _literal(node.left)
    return None


def _field_names(node):
    if isinstance(node, (ast.List, ast.Tuple)):
        return [name for element in node.elts for name in _field_names(element)]
    if isinstance(node, ast.Starred):
        return _field_names(node.value)
    if isinstance(node, ast.IfExp):
        return _field_names(node.body) + _field_names(node.orelse)
    text = _literal(node)
    found = FIELD_LITERAL.match(text) if text else None
    return [found.group(1)] if found else []


def _shape(call, module):
    func = call.func
    if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name):
        return CALLS.get((func.value.id, func.attr))
    if isinstance(func, ast.Name):
        return LOCAL_CALLS.get(module, {}).get(func.id)
    return None


def writer_calls(source, module=""):
    """(line, kind or None, literal field names) for every event-writing call in `source`; `module` is the
    source's own module name, so that `mark(role, "kind", …)` inside verify.py is read as verify.mark."""
    found = []
    tree = ast.parse(source)
    assigned = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            assigned.setdefault(node.targets[0].id, []).append(node.value)
    constants = {name: values[0].value for name, values in assigned.items() if len(values) == 1
                 and isinstance(values[0], ast.Constant) and isinstance(values[0].value, str)}
    for call in ast.walk(tree):
        shape = isinstance(call, ast.Call) and _shape(call, module)
        if not shape or len(call.args) <= shape[0]:
            continue
        kind_arg = call.args[shape[0]]
        if isinstance(kind_arg, ast.Constant) and isinstance(kind_arg.value, str):
            kind = kind_arg.value
        else:
            kind = constants.get(kind_arg.id) if isinstance(kind_arg, ast.Name) else None
        names = []
        for argument in call.args[shape[1]:]:
            names += _field_names(argument)
        found.append((call.lineno, kind, names))
    return found
