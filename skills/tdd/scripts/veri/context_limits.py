"""The claude options that limit what a veri session loads, shared by leaf and conductor."""
import json
import os


def context_limits():
    return ["--disable-slash-commands", "--strict-mcp-config",
            "--mcp-config", json.dumps({"mcpServers": {}}),
            "--settings", json.dumps({
                "autoMemoryEnabled": False,
                "claudeMdExcludes": [os.path.join(os.path.expanduser("~"), ".claude", "CLAUDE.md")]})]
