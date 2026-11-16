"""The one writer of a `#!/bin/sh` stub script a case puts in place of a real executable."""
import os


def write_stub(path, body):
    """Write `#!/bin/sh` and `body` to `path`, make it executable (0755) and return `path`."""
    with open(path, "w") as stub:
        stub.write("#!/bin/sh\n" + body)
    os.chmod(path, 0o755)
    return path
