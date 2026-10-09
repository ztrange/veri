"""The Claude Code session variables a `claude` started by veri must not inherit, and their strip."""

SESSION_VARS = (
    "CLAUDECODE",
    "CLAUDE_CODE_SESSION_ID",
    "CLAUDE_CODE_HOST_SESSION_ID",
    "CLAUDE_CODE_REMOTE_SESSION_ID",
    "CLAUDE_CODE_MESSAGING_SOCKET",
    "CLAUDE_CODE_MESSAGING_TOKEN",
    "CLAUDE_PID",
    "CLAUDE_CODE_CHILD_SESSION",
    "CLAUDE_CODE_ENTRYPOINT",
    "CLAUDE_AUTO_BACKGROUND_TASKS",
)


def strip_session_env(env):
    """Remove from `env` every SESSION_VARS name and, given a session id, every value carrying it but CLAUDE_BIN's and a VERI_* variable's, and every PATH entry carrying it."""
    session_id = env.get("CLAUDE_CODE_SESSION_ID", "")
    for name in SESSION_VARS:
        env.pop(name, None)
    if session_id:
        for name in [n for n, v in env.items() if session_id in v and not _override(n) and n != "PATH"]:
            del env[name]
        if "PATH" in env:
            env["PATH"] = ":".join(e for e in env["PATH"].split(":") if session_id not in e)


def _override(name):
    return name == "CLAUDE_BIN" or name.startswith("VERI_")
