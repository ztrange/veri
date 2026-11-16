"""The claude options that limit what a veri session loads, shared by leaf and conductor."""
import json
import os


def context_limits(excludes=(), settings=None):
    """`excludes`: further `claudeMdExcludes` paths, after the global `CLAUDE.md`; `settings`: further keys of the one
    `--settings` object, after these."""
    return ["--disable-slash-commands", "--strict-mcp-config",
            "--mcp-config", json.dumps({"mcpServers": {}}),
            "--settings", json.dumps({
                "autoMemoryEnabled": False,
                "claudeMdExcludes": [os.path.join(os.path.expanduser("~"), ".claude", "CLAUDE.md"), *excludes],
                **(settings or {})})]
