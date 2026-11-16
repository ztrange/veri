"""The claude options that limit what a veri session loads, shared by leaf and conductor."""
import json
import os


def context_limits(excludes=()):
    """`excludes`: further `claudeMdExcludes` paths, after the global `CLAUDE.md`."""
    return ["--disable-slash-commands", "--strict-mcp-config",
            "--mcp-config", json.dumps({"mcpServers": {}}),
            "--settings", json.dumps({
                "autoMemoryEnabled": False,
                "claudeMdExcludes": [os.path.join(os.path.expanduser("~"), ".claude", "CLAUDE.md"), *excludes]})]
