"""The shared indexes the tree audits read: every test file under tests/py, every module of veri/.

Each file is read once and parsed on first use, so a sweep that reads names and segments never pays for the node walks.
conftest.py exposes them as the `tests_py_index` and `veri_modules_index` session fixtures.
"""
import ast
import dataclasses
import functools
import pathlib
import re


class _Parts:
    """What an audit may ask of one top-level node. Each field is walked on first use and kept, so an audit that
    reads only names and segments never pays for the node walks, and the names an assignment binds share one."""

    def __init__(self, node):
        self.node = node

    @functools.cached_property
    def nodes(self):
        return list(ast.walk(self.node))

    @functools.cached_property
    def literals(self):
        return tuple(p.value for p in self.nodes if isinstance(p, ast.Constant) and isinstance(p.value, str))

    @functools.cached_property
    def names(self):
        return tuple(p.id for p in self.nodes if isinstance(p, ast.Name) and isinstance(p.ctx, ast.Load))

    @functools.cached_property
    def constants(self):
        return tuple(_constants(self.node))

    @functools.cached_property
    def strings(self):
        return _strings(self.nodes, str)

    @functools.cached_property
    def byte_strings(self):
        return tuple(b.decode("utf-8", "replace") for b in _strings(self.nodes, bytes))


@dataclasses.dataclass(frozen=True)
class Definition:
    name: str
    segment: str
    _parts: _Parts = dataclasses.field(repr=False, compare=False)

    literals = property(lambda self: self._parts.literals)
    names = property(lambda self: self._parts.names)
    constants = property(lambda self: self._parts.constants)
    strings = property(lambda self: self._parts.strings)
    byte_strings = property(lambda self: self._parts.byte_strings)


@dataclasses.dataclass(frozen=True)
class WalkResult:
    definitions: tuple


def mentioned_names(segments):
    """For each definition in `segments` ({name: source}), the other definitions whose name its source mentions as a
    whole word. Every name is a Python identifier, so it is all `\\w`: `\\bname\\b` matches exactly where `name` is a whole
    `\\w+` run of the source, which is what a set of the source's runs answers, tokenised once per definition instead of
    one regex search (and compile) per definition pair."""
    return {name: (set(re.findall(r"\w+", src)) & segments.keys()) - {name} for name, src in segments.items()}


def _constants(node):
    if isinstance(node, ast.JoinedStr):
        return
    if isinstance(node, ast.Constant):
        if isinstance(node.value, str):
            yield node.value
        return
    for field, value in ast.iter_fields(node):
        if isinstance(node, ast.Assert) and field == "msg":
            continue
        for child in value if isinstance(value, list) else [value]:
            if isinstance(child, ast.AST):
                yield from _constants(child)


def _strings(parts, kind):
    """Every `kind` constant but an f-string's own literal fragments: the text a readers audit counts as read,
    assert messages and constants inside an f-string's `{...}` included, as each audit's own walk counted it before #2170."""
    fragments = {id(v) for j in parts if isinstance(j, ast.JoinedStr) for v in j.values}
    return tuple(p.value for p in parts if isinstance(p, ast.Constant) and type(p.value) is kind and id(p) not in fragments)


def _lines(text):
    """text split as ast.get_source_segment splits it, once per file instead of once per definition."""
    return re.findall(r"[^\r\n]*(?:\r\n|\n|\r)|[^\r\n]+$", text)


def _segment(lines, node):
    first, last = node.lineno - 1, node.end_lineno - 1
    if first == last:
        return lines[first].encode()[node.col_offset:node.end_col_offset].decode()
    return "".join([lines[first].encode()[node.col_offset:].decode(), *lines[first + 1:last],
                    lines[last].encode()[:node.end_col_offset].decode()])


def _definition(text, node, lines=None):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        names = [node.name]
    else:
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        names = [t.id for target in targets for t in ast.walk(target) if isinstance(t, ast.Name)]
    segment = _segment(lines if lines is not None else _lines(text), node)
    parts = _Parts(node)
    return [Definition(name=name, segment=segment, _parts=parts) for name in names]


class TestFile:
    def __init__(self, path):
        self.path = path
        self.text = path.read_text(encoding="utf-8")
        self._tree = None
        self._walk = None

    @property
    def tree(self):
        if self._tree is None:
            self._tree = ast.parse(self.text)
        return self._tree

    @property
    def walk(self):
        if self._walk is None:
            lines = _lines(self.text)
            self._walk = WalkResult(tuple(
                d for node in self.tree.body
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Assign, ast.AnnAssign))
                for d in _definition(self.text, node, lines)))
        return self._walk

    @functools.cached_property
    def nodes(self):
        """Every node of the file, class bodies and module-level statements included, walked once and kept."""
        return tuple(ast.walk(self.tree))



def tests_py_index_of(root):
    return [TestFile(path) for path in sorted(pathlib.Path(root).rglob("test_*.py"))]


class VeriModules:
    """Every `*.py` module of one directory (veri/), by stem: its path, text and parsed tree, each read on first use
    and kept."""

    def __init__(self, directory, users=None):
        self._paths = {path.stem: path for path in sorted(pathlib.Path(directory).glob("*.py"))}
        self._texts = {}
        self._trees = {}
        self._users = VeriModules(users) if users else None

    def user_trees(self):
        """{stem: tree} of the modules outside the directory that count as users of its names, never as its modules."""
        return {} if self._users is None else {name: self._users.tree(name) for name in self._users.names}

    @property
    def names(self):
        return tuple(self._paths)

    def path(self, name):
        return self._paths[name]

    def text(self, name):
        if name not in self._texts:
            self._texts[name] = self._paths[name].read_text(encoding="utf-8")
        return self._texts[name]

    def tree(self, name):
        if name not in self._trees:
            self._trees[name] = ast.parse(self.text(name))
        return self._trees[name]
