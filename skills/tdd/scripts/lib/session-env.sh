#!/usr/bin/env bash
# lib/session-env.sh — sourced, not run: defines SESSION_VARS, the Claude Code session
# variables a `claude` started by veri must not inherit.
SESSION_VARS=(
  CLAUDECODE
  CLAUDE_CODE_SESSION_ID
  CLAUDE_CODE_HOST_SESSION_ID
  CLAUDE_CODE_MESSAGING_SOCKET
  CLAUDE_CODE_MESSAGING_TOKEN
  CLAUDE_PID
  CLAUDE_CODE_CHILD_SESSION
  CLAUDE_CODE_ENTRYPOINT
)
