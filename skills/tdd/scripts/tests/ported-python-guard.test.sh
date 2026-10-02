#!/usr/bin/env bash
# Unit tests for the guard suite that keeps a ported script's Bash free of Python source —
# skills/tdd/scripts/tests/no-python-in-ported-scripts.test.sh.
#
# Contract under test:
#   Over a tree holding a script whose module exists under veri/ and that feeds python3 a
#   heredoc and a -c string, the guard fails and names each as `<script>:<line>`; it says
#   nothing about a python3 -c inside a comment, nor about a script with no module under
#   veri/; and once the offender is removed from
#   the same tree it passes.
#
# Run: skills/tdd/scripts/tests/ported-python-guard.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"

GUARD='skills/tdd/scripts/tests/no-python-in-ported-scripts.test.sh'
GUARD_PATH="$ROOT/$GUARD"
GUARD_NAME="$(basename "$GUARD")"

SCRIPTS_DIR='skills/tdd/scripts'
TESTS_DIR='skills/tdd/scripts/tests'

OFFENDER_REL="$SCRIPTS_DIR/probe-port.sh"
MODULE_REL="$SCRIPTS_DIR/veri/probe_port.py"
UNPORTED_REL="$SCRIPTS_DIR/probe-unported.sh"
OFFENDER_NAME="$(basename "$OFFENDER_REL")"
UNPORTED_NAME="$(basename "$UNPORTED_REL")"

HEREDOC_MARK='heredoc-probe'
DASH_C_MARK='dash-c-probe'
COMMENT_MARK='comment-probe'

source "$HERE/lib/harness.sh"

flat() { local s="$1"; printf '%s' "${s//$'\n'/\/}"; }

write_script() {
  local path="$1"
  {
    echo '#!/usr/bin/env bash'
    echo 'set -uo pipefail'
    echo "# python3 -c 'print(1)'  # $COMMENT_MARK"
    echo "python3 - \"\$1\" <<'PY'  # $HEREDOC_MARK"
    echo 'import sys'
    echo 'print(sys.argv[1])'
    echo 'PY'
    echo "python3 -c 'import sys; print(sys.argv[1])' \"\$1\"  # $DASH_C_MARK"
  } > "$path"
  chmod 755 "$path"
}

line_of() { grep -n "$1" "$offender_path" | cut -d: -f1; }

plant() {
  tree="$(scratch_dir)" || {
    problems+=("could not make a scratch tree to plant this case's files in, so the criterion went unasked")
    return 1
  }
  mkdir -p "$tree/$TESTS_DIR/lib" "$tree/$SCRIPTS_DIR/veri"

  offender_path="$tree/$OFFENDER_REL"
  unported_path="$tree/$UNPORTED_REL"
  guard_copy="$tree/$TESTS_DIR/$GUARD_NAME"

  write_script "$offender_path"
  write_script "$unported_path"
  printf 'def main(argv):\n    return 0\n' > "$tree/$MODULE_REL"
  : > "$tree/$SCRIPTS_DIR/veri/__init__.py"

  cp "$GUARD_PATH" "$guard_copy" && chmod 755 "$guard_copy"
  cp "$HERE/lib/harness.sh" "$tree/$TESTS_DIR/lib/"
  new_repo "$tree" >/dev/null 2>&1
  git -C "$tree" add -A >/dev/null 2>&1

  heredoc_line="$(line_of "$HEREDOC_MARK")"
  dash_c_line="$(line_of "$DASH_C_MARK")"
  comment_line="$(line_of "$COMMENT_MARK")"
  return 0
}

drop_tree() {
  [[ -z "${tree:-}" ]] || rm -rf "$tree"
}

probe_guard_is_there() {
  [[ -f "$GUARD_PATH" ]] || {
    problems+=("there is no guard suite at $GUARD, so nothing stops a script whose module exists under veri/ from holding Python source again")
    return 1
  }
  [[ -x "$GUARD_PATH" ]] || {
    problems+=("$GUARD is not executable, so \`make test\`'s runner cannot run it")
    return 1
  }
}

probe_plant_is_what_it_claims() {
  [[ "$heredoc_line" =~ ^[0-9]+$ && "$dash_c_line" =~ ^[0-9]+$ && "$comment_line" =~ ^[0-9]+$ ]] || {
    problems+=("the planted offender has no single marked line per form to name (heredoc '$heredoc_line', -c '$dash_c_line', comment '$comment_line'), so the criterion cannot be asked")
    return 1
  }
}

run_guard() {
  guard_out="$("$guard_copy" 2>&1)" && guard_code=0 || guard_code=$?
}

naming() { grep -F "$1" <<< "$guard_out"; }

names_none() {
  local named
  named="$(naming "$1")"
  [[ -z "$named" ]] || problems+=("$2: $(flat "$named")")
}

probe_guard_names_each_form() {
  local form line
  [[ "$guard_code" != 0 ]] ||
    problems+=("want the guard to fail over $OFFENDER_REL, whose module $MODULE_REL exists and which feeds python3 Python source; it exited 0 and said: $(flat "$guard_out")")
  for form in "heredoc:$heredoc_line" "-c string:$dash_c_line"; do
    line="${form##*:}"
    [[ -n "$(naming "$OFFENDER_REL:$line")" ]] ||
      problems+=("no line of the guard's output names $OFFENDER_REL:$line, where python3 is fed a ${form%:*}; it said: $(flat "$guard_out")")
  done
}

probe_guard_leaves_the_comment_alone() {
  names_none "$OFFENDER_REL:$comment_line " "the guard named $OFFENDER_REL:$comment_line, where python3 -c appears only inside a comment"
}

probe_guard_leaves_the_unported_alone() {
  names_none "$UNPORTED_NAME" "the guard named $UNPORTED_REL, which has no module under veri/ and so is not ported yet"
}

remove_plant() {
  rm -f "$offender_path"
  git -C "$tree" add -A >/dev/null 2>&1
}

probe_guard_is_green_once_the_plant_is_removed() {
  [[ "$guard_code" == 0 ]] ||
    problems+=("want the guard to pass over the same tree once $OFFENDER_REL is removed; it exited $guard_code and said: $(flat "$guard_out")")
  names_none "$OFFENDER_NAME" "the guard still named $OFFENDER_NAME, whose file is no longer in the tree"
}

name="no-python-in-ported-scripts.test.sh names a script whose module exists under veri/ as <script>:<line> at its python3 heredoc and its python3 -c string, leaves a commented python3 -c and a script with no module alone, and goes green once the planted offender is removed"
problems=()

if probe_guard_is_there && plant; then
  if probe_plant_is_what_it_claims; then
    run_guard
    probe_guard_names_each_form
    probe_guard_leaves_the_comment_alone
    probe_guard_leaves_the_unported_alone
    remove_plant
    run_guard
    probe_guard_is_green_once_the_plant_is_removed
  fi
fi
drop_tree

report "$name"

finish
