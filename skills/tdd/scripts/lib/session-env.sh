#!/usr/bin/env bash
# lib/session-env.sh — sourced, not run: defines SESSION_VARS, the Claude Code session
# variables a `claude` started by veri must not inherit, and strip_session_env, which
# unsets them and every variable whose value carries CLAUDE_CODE_SESSION_ID.
SESSION_VARS=(
  CLAUDECODE
  CLAUDE_CODE_SESSION_ID
  CLAUDE_CODE_HOST_SESSION_ID
  CLAUDE_CODE_REMOTE_SESSION_ID
  CLAUDE_CODE_MESSAGING_SOCKET
  CLAUDE_CODE_MESSAGING_TOKEN
  CLAUDE_PID
  CLAUDE_CODE_CHILD_SESSION
  CLAUDE_CODE_ENTRYPOINT
  CLAUDE_AUTO_BACKGROUND_TASKS
)

strip_session_env() {
  local session_id="${CLAUDE_CODE_SESSION_ID:-}" name
  unset "${SESSION_VARS[@]}"
  if [[ -n "$session_id" ]]; then
    for name in $(compgen -e); do
      if [[ "${!name}" == *"$session_id"* ]]; then unset "$name"; fi
    done
  fi
}
