#!/usr/bin/env bash
# Unit tests for scripts/veri/json_documents.py — the one reader of JSON documents written
# back to back, as gh_rest_list prints a listing.
#
# Contract under test:
#   veri/json_documents.py  documents(<text>) → the documents in order, unflattened;
#                           items(<text>) → their elements as one list. Its importers —
#                           solvable-issues.sh, workqueue.sh, invisible-work.sh, wait-ci.sh
#                           and parallel-conductors.sh — find it under veri/, not lib/.
#
# Run: scripts/tests/json-documents.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
SCRIPTS="$(cd "$HERE/.." && pwd)"
source "$HERE/lib/harness.sh"

problems=()
[[ ! -e "$SCRIPTS/lib/json_documents.py" ]] || problems+=("scripts/lib/json_documents.py still exists")
scratch="$(scratch_dir)"
mkdir -p "$scratch/scripts" "$scratch/gh" "$scratch/gh-parallel" "$scratch/bin" "$scratch/main/.tdd" "$scratch/common/info"
cp -R "$SCRIPTS/lib" "$SCRIPTS/veri" "$scratch/scripts/"
rm -rf "$scratch/scripts/lib/json_documents.py" "$scratch/scripts/lib/__pycache__" "$scratch/scripts/veri/__pycache__"
cp "$SCRIPTS/solvable-issues.sh" "$SCRIPTS/workqueue.sh" "$SCRIPTS/invisible-work.sh" \
  "$SCRIPTS/wait-ci.sh" "$SCRIPTS/parallel-conductors.sh" "$scratch/scripts/"
cat > "$scratch/scripts/veri/json_documents.py" <<'PY'
def documents(text):
    return [{"check_runs": [{"status": "completed", "conclusion": "failure"}]}, {"statuses": []}]


def items(text):
    if "parallel" in text:
        return [{"body": "Closes #7", "isDraft": False, "url": "https://decoy.test/pull/7"}]
    return [{"number": 7, "title": "decoy", "state": "OPEN",
             "labels": [{"name": "ready-for-agent"}], "body": "", "headRefName": "decoy"}]
PY
printf '[]\n' > "$scratch/gh/prs.json"
printf '[{"marker": "parallel"}]\n' > "$scratch/gh-parallel/prs.json"
cat > "$scratch/gh/issues.json" <<'JSON'
[
  {"number": 5, "title": "closed", "state": "CLOSED", "labels": [], "body": ""},
  {"number": 7, "title": "blocked by an open issue", "state": "OPEN",
   "labels": [{"name": "ready-for-agent"}], "body": "## Blocked by\n\n- #8\n"},
  {"number": 8, "title": "the open blocker", "state": "OPEN",
   "labels": [], "body": "## Blocked by\n\nNone.\n"}
]
JSON
printf 'alpha\t7\tqueued\t\n' > "$scratch/main/.tdd/workqueue"
cat > "$scratch/bin/git" <<STUB
#!/bin/sh
case "\$1" in
  worktree) [ "\$2" = list ] && [ "\$3" = --porcelain ] && [ -z "\$4" ] && printf 'worktree %s\n' "$scratch/main" ;;
  rev-parse) echo "$scratch/common" ;;
  symbolic-ref) echo origin/main ;;
  for-each-ref) [ "\$3" = refs/remotes/origin/ ] && echo "refs/remotes/origin/tdd/5-decoy 1234567" ;;
  rev-list) echo 2 ;;
esac
exit 0
STUB
cat > "$scratch/bin/gh" <<'STUB'
#!/bin/sh
case "$2" in
  */pulls/*) echo '{"head": {"sha": "abc1234"}}' ;;
  */check-runs\?page=1) echo '{"check_runs": [{"status": "completed", "conclusion": "success"}]}' ;;
  */check-runs*) echo '{"check_runs": []}' ;;
  */status) echo '{"statuses": []}' ;;
  *) exit 1 ;;
esac
STUB
printf '#!/bin/sh\necho 7\n' > "$scratch/scripts/solvable-stub"
printf '#!/bin/sh\nexit 0\n' > "$scratch/scripts/supervise-stub"
chmod +x "$scratch/bin/git" "$scratch/bin/gh" "$scratch/scripts/solvable-stub" "$scratch/scripts/supervise-stub"
run() { (cd "$scratch/main" && env -u VERI_LABEL -u VERI_PRIORITY_LABEL -u VERI_MAX_ISSUES \
  PATH="$scratch/bin:$PATH" VERI_GH_JSON="$scratch/gh" PYTHONDONTWRITEBYTECODE=1 "$@" 2>&1); }

out="$(run "$scratch/scripts/solvable-issues.sh")" && code=0 || code=$?
[[ "$code" -eq 0 && "$out" == 7* ]] \
  || problems+=("solvable-issues.sh beside a stand-in veri/json_documents.py: exit $code, output '$out', want issue 7")
out="$(run "$scratch/scripts/workqueue.sh" next alpha)" && code=0 || code=$?
[[ "$code" -eq 0 && "$out" == 7 ]] \
  || problems+=("workqueue.sh next beside a stand-in veri/json_documents.py: exit $code, output '$out', want '7'")
out="$(run "$scratch/scripts/invisible-work.sh")" && code=0 || code=$?
[[ "$code" -eq 0 && "$out" == *"issue #5 unknown"* ]] \
  || problems+=("invisible-work.sh beside a stand-in veri/json_documents.py: exit $code, output '$out', want 'issue #5 unknown'")
out="$(run "$scratch/scripts/wait-ci.sh" https://github.com/acme/widgets/pull/1 5 5)" && code=0 || code=$?
[[ "$code" -eq 1 ]] \
  || problems+=("wait-ci.sh beside a stand-in veri/json_documents.py: exit $code, output '$out', want 1 (the stand-in's failing check)")
mv "$scratch/scripts/solvable-stub" "$scratch/scripts/solvable-issues.sh"
mv "$scratch/scripts/supervise-stub" "$scratch/scripts/supervise.sh"
out="$(run env VERI_MAX_ISSUES=1 VERI_GH_JSON="$scratch/gh-parallel" "$scratch/scripts/parallel-conductors.sh")" && code=0 || code=$?
[[ "$out" == *"#7 — done https://decoy.test/pull/7"* ]] \
  || problems+=("parallel-conductors.sh beside a stand-in veri/json_documents.py: exit $code, output '$out', want '#7 — done https://decoy.test/pull/7'")

report "json_documents is a module of scripts/veri/, not scripts/lib/: solvable-issues.sh, workqueue.sh, invisible-work.sh, wait-ci.sh and parallel-conductors.sh read JSON documents through veri/json_documents.py"

finish
