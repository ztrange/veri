"""The one writer of a `#!/bin/sh` stub script a case puts in place of a real executable."""
import ast
import os

HEADER = "#!/bin/sh"


def write_stub(path, body):
    """Write `#!/bin/sh` and `body` to `path`, make it executable (0755) and return `path`."""
    with open(path, "w") as stub:
        stub.write(HEADER + "\n" + body)
    os.chmod(path, 0o755)
    return path


def holds_an_inline_stub(source):
    """True when `source` holds a string literal (an f-string's leading piece included) that starts `#!/bin/sh`."""
    return any(isinstance(node, ast.Constant) and isinstance(node.value, str) and node.value.startswith(HEADER)
               for node in ast.walk(ast.parse(source)))
