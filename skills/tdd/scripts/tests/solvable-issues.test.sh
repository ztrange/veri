#!/usr/bin/env bash
# Unit tests for scripts/solvable-issues.sh — the selection layer. Given a repo's issues
# and open PRs, print the numbers of the issues veri may take right now, one per line, and
# exit 0; print nothing and exit 3 when there are none.
#
# Contract under test:
#   solvable-issues.sh [--repo owner/name]
#   VERI_GH_JSON=<dir>   read <dir>/issues.json and <dir>/prs.json instead of shelling out
#                        to gh, in the shape of
#                          gh issue list --json number,title,labels,body,state
#                          gh pr list    --json body,state
#   VERI_LABEL=<name>    the opt-in label to select on, default `ready-for-agent`. Set but
#                        empty is exit 2.
#
# Run: scripts/tests/solvable-issues.test.sh
set -uo pipefail
unset VERI_GH_DRIVER

HERE="$(cd "$(dirname "$0")" && pwd)"
SOLVABLE="$HERE/../solvable-issues.sh"
REPO_ROOT="$(cd "$HERE/../../../.." && pwd)"
source "$HERE/lib/harness.sh"
work="$(scratch_dir)"

no_claims="$work/no-claims"
new_repo -b main "$no_claims" >/dev/null 2>&1
cd "$no_claims" || exit 2

fixture() {  # fixture <name> -> path
  local dir="$work/$1"
  mkdir -p "$dir"
  printf '[]\n' > "$dir/prs.json"
  echo "$dir"
}

run() {  # run <fixture-dir> [script args…]; sets $out and $code
  local fixture="$1"; shift
  out="$(VERI_GH_JSON="$fixture" "$SOLVABLE" "$@" 2>/dev/null)" && code=0 || code=$?
}

label_run() {  # label_run <fixture-dir> <env setting…>; sets $out and $code
  local fixture="$1"; shift
  out="$(env "$@" VERI_GH_JSON="$fixture" "$SOLVABLE" 2>/dev/null)" && code=0 || code=$?
}

refused_run() {  # refused_run <fixture-dir> <env setting…>; sets $refused_out/$refused_err/$refused_code
  local fixture="$1"; shift
  refused_out="$fixture/refused.out" refused_err="$fixture/refused.err"
  env "$@" VERI_GH_JSON="$fixture" "$SOLVABLE" >"$refused_out" 2>"$refused_err" \
    && refused_code=0 || refused_code=$?
}

fx="$(fixture unblocked)"
cat > "$fx/issues.json" <<'JSON'
[
  {
    "number": 41,
    "title": "solvable-issues.sh: list the issues veri may take, in order",
    "labels": [{"name": "ready-for-agent"}],
    "state": "OPEN",
    "body": "## What to build\n\nA script that prints the numbers veri may take.\n\n## Blocked by\n\nNone.\n"
  }
]
JSON

run "$fx"

{ [[ "$code" == 0 ]] && [[ "$out" == "41" ]]; } \
  && ok || no "open ready-for-agent issue with no blockers is listed (exit=$code want 0, stdout='$out' want '41')"

fx="$(fixture blocked)"
issues() {  # issues <state-of-49>
  cat <<JSON
[
  {
    "number": 50,
    "title": "the /tdd loop skill",
    "labels": [{"name": "ready-for-agent"}],
    "state": "OPEN",
    "body": "## What to build\n\nA loop over solvable-issues.sh.\n\n## Blocked by\n\n#49\n"
  },
  {
    "number": 49,
    "title": "solvable-issues.sh: list the issues veri may take",
    "labels": [{"name": "ready-for-agent"}],
    "state": "$1",
    "body": "## Blocked by\n\nNone.\n"
  }
]
JSON
}

issues OPEN > "$fx/issues.json"
run "$fx"; while_open="$out" open_code="$code"

issues CLOSED > "$fx/issues.json"
run "$fx"; once_closed="$out" closed_code="$code"

{ [[ "$open_code" == 0 && "$while_open" == "49" ]] \
  && [[ "$closed_code" == 0 && "$once_closed" == "50" ]]; } \
  && ok || no "issue blocked by an open issue is withheld until that issue closes (blocker open: exit=$open_code want 0, stdout='$while_open' want '49'; blocker closed: exit=$closed_code want 0, stdout='$once_closed' want '50')"

fx="$(fixture unlabelled)"
cat > "$fx/issues.json" <<'JSON'
[
  {
    "number": 51,
    "title": "an idea nobody has vetted for veri yet",
    "labels": [],
    "state": "OPEN",
    "body": "## What to build\n\nSomething, eventually.\n\n## Blocked by\n\nNone.\n"
  },
  {
    "number": 52,
    "title": "the /tdd loop skill",
    "labels": [{"name": "ready-for-agent"}],
    "state": "OPEN",
    "body": "## Blocked by\n\nNone.\n"
  }
]
JSON

run "$fx"

{ [[ "$code" == 0 ]] && [[ "$out" == "52" ]]; } \
  && ok || no "issue without the ready-for-agent label is never listed (exit=$code want 0, stdout='$out' want '52')"

fx="$(fixture claimed)"
cat > "$fx/issues.json" <<'JSON'
[
  {
    "number": 53,
    "title": "solvable-issues.sh: list the issues veri may take",
    "labels": [{"name": "ready-for-agent"}],
    "state": "OPEN",
    "body": "## What to build\n\nA script that prints the numbers veri may take.\n\n## Blocked by\n\nNone.\n"
  },
  {
    "number": 54,
    "title": "the /tdd loop skill",
    "labels": [{"name": "ready-for-agent"}],
    "state": "OPEN",
    "body": "## Blocked by\n\nNone.\n"
  }
]
JSON
cat > "$fx/prs.json" <<'JSON'
[
  {
    "state": "OPEN",
    "body": "Draft PR opened by a /tdd run.\n\nCloses #53\n"
  }
]
JSON

run "$fx"

{ [[ "$code" == 0 ]] && [[ "$out" == "54" ]]; } \
  && ok || no "issue an open PR already Closes is not listed (exit=$code want 0, stdout='$out' want '54')"

fx="$(fixture ordering)"
cat > "$fx/issues.json" <<'JSON'
[
  {
    "number": 57,
    "title": "the /tdd loop skill",
    "labels": [{"name": "ready-for-agent"}],
    "state": "OPEN",
    "body": "## Blocked by\n\nNone.\n"
  },
  {
    "number": 55,
    "title": "solvable-issues.sh: list the issues veri may take",
    "labels": [{"name": "ready-for-agent"}],
    "state": "OPEN",
    "body": "## Blocked by\n\nNone.\n"
  },
  {
    "number": 56,
    "title": "classify-bail.sh: label the bail a human reads",
    "labels": [{"name": "ready-for-agent"}],
    "state": "OPEN",
    "body": "## Blocked by\n\nNone.\n"
  }
]
JSON

run "$fx"; many="$out" many_code="$code"

fx="$(fixture none)"
cat > "$fx/issues.json" <<'JSON'
[
  {
    "number": 58,
    "title": "the /tdd loop skill",
    "labels": [{"name": "ready-for-agent"}],
    "state": "OPEN",
    "body": "## Blocked by\n\n#59\n"
  },
  {
    "number": 59,
    "title": "an idea nobody has vetted for veri yet",
    "labels": [],
    "state": "OPEN",
    "body": "## Blocked by\n\nNone.\n"
  }
]
JSON

run "$fx"; empty="$out" empty_code="$code"

{ [[ "$many_code" == 0 && "$many" == $'55\n56\n57' ]] \
  && [[ "$empty_code" == 3 && -z "$empty" ]]; } \
  && ok || no "output is one number per line ascending, and no solvable issue means exit 3 and empty stdout (three takeable: exit=$many_code want 0, stdout='$many' want '55\\n56\\n57'; none takeable: exit=$empty_code want 3, stdout='$empty' want empty)"

fx="$(fixture gh)"
cat > "$fx/issues.json" <<'JSON'
[
  {
    "number": 60,
    "title": "solvable-issues.sh: list the issues veri may take",
    "labels": [{"name": "ready-for-agent"}],
    "state": "OPEN",
    "body": "## Blocked by\n\nNone.\n"
  },
  {
    "number": 61,
    "title": "the /tdd loop skill",
    "labels": [{"name": "ready-for-agent"}],
    "state": "OPEN",
    "body": "## Blocked by\n\nNone.\n"
  }
]
JSON
cat > "$fx/prs.json" <<'JSON'
[
  {
    "state": "OPEN",
    "body": "Draft PR opened by a /tdd run.\n\nCloses #60\n"
  }
]
JSON

stubdir="$work/bin"
mkdir -p "$stubdir"
cat > "$stubdir/gh" <<'STUB'
#!/bin/sh
printf '%s\n' "$*" >> "$ARGV_OUT"
case "$1 $2" in
  "issue list") cat "$GH_ISSUES" ;;
  "pr list")    cat "$GH_PRS" ;;
esac
STUB
chmod +x "$stubdir/gh"

gh_run() {  # gh_run <argv-log> [script args...]; sets $out and $code
  local log="$1"; shift
  : > "$log"
  out="$(env -u VERI_GH_JSON VERI_GH_DRIVER=auto PATH="$stubdir:$PATH" ARGV_OUT="$log" \
         GH_ISSUES="$fx/issues.json" GH_PRS="$fx/prs.json" \
         "$SOLVABLE" "$@" 2>/dev/null)" && code=0 || code=$?
}

gh_run "$work/argv-bare"; bare="$out" bare_code="$code"
bare_argv="$(cat "$work/argv-bare")"

gh_run "$work/argv-repo" --repo owner/name; scoped="$out" scoped_code="$code"
repo_argv="$(cat "$work/argv-repo")"

{ [[ "$bare_code" == 0 && "$bare" == "61" ]] \
  && grep -q '^issue list' <<<"$bare_argv" && grep -q '^pr list' <<<"$bare_argv" \
  && ! grep -q -- '--repo' <<<"$bare_argv" \
  && [[ "$scoped_code" == 0 && "$scoped" == "61" ]] \
  && [[ "$(grep -c -- '--repo owner/name' <<<"$repo_argv")" == 2 ]]; } \
  && ok || no "without VERI_GH_JSON the script reads gh issue list and gh pr list itself, forwarding --repo when given (no flag: exit=$bare_code want 0, stdout='$bare' want '61', gh calls=$(tr '\n' '|' <<<"$bare_argv") want an 'issue list' and a 'pr list', neither with --repo; --repo owner/name: exit=$scoped_code want 0, stdout='$scoped' want '61', gh calls=$(tr '\n' '|' <<<"$repo_argv") want --repo owner/name on both)"

fx="$(fixture default-label)"
cat > "$fx/issues.json" <<'JSON'
[
  {
    "number": 62,
    "title": "solvable-issues.sh: take the opt-in label from VERI_LABEL",
    "labels": [{"name": "ready-for-agent"}],
    "state": "OPEN",
    "body": "## What to build\n\nA label parameter with ready-for-agent as the default.\n\n## Blocked by\n\nNone.\n"
  },
  {
    "number": 63,
    "title": "walkthrough: draw rung 2",
    "labels": [{"name": "ready-for-agent:docs"}],
    "state": "OPEN",
    "body": "## Blocked by\n\nNone.\n"
  }
]
JSON

label_run "$fx" -u VERI_LABEL

{ [[ "$code" == 0 ]] && [[ "$out" == "62" ]]; } \
  && ok || no "with VERI_LABEL unset the opt-in label is exactly ready-for-agent (exit=$code want 0, stdout='$out' want '62')"

fx="$(fixture other-label)"
cat > "$fx/issues.json" <<'JSON'
[
  {
    "number": 64,
    "title": "solvable-issues.sh: take the opt-in label from VERI_LABEL",
    "labels": [{"name": "ready-for-agent"}],
    "state": "OPEN",
    "body": "## What to build\n\nA label parameter with ready-for-agent as the default.\n\n## Blocked by\n\nNone.\n"
  },
  {
    "number": 65,
    "title": "walkthrough: draw rung 2",
    "labels": [{"name": "ready-for-agent:docs"}],
    "state": "OPEN",
    "body": "## Blocked by\n\nNone.\n"
  }
]
JSON

label_run "$fx" VERI_LABEL=ready-for-agent:docs

{ [[ "$code" == 0 ]] && [[ "$out" == "65" ]]; } \
  && ok || no "with VERI_LABEL set to another label only issues carrying that label are listed (exit=$code want 0, stdout='$out' want '65')"

fx="$(fixture both-labels)"
cat > "$fx/issues.json" <<'JSON'
[
  {
    "number": 66,
    "title": "walkthrough: draw rung 2's selection layer",
    "labels": [{"name": "ready-for-agent"}, {"name": "ready-for-agent:docs"}],
    "state": "OPEN",
    "body": "## What to build\n\nA panel for solvable-issues.sh.\n\n## Blocked by\n\nNone.\n"
  }
]
JSON

label_run "$fx" -u VERI_LABEL; under_default="$out" default_code="$code"

label_run "$fx" VERI_LABEL=ready-for-agent:docs; under_docs="$out" docs_code="$code"

{ [[ "$default_code" == 0 && "$under_default" == "66" ]] \
  && [[ "$docs_code" == 0 && "$under_docs" == "66" ]]; } \
  && ok || no "an issue carrying both labels is listed under either VERI_LABEL value (VERI_LABEL unset: exit=$default_code want 0, stdout='$under_default' want '66'; VERI_LABEL=ready-for-agent:docs: exit=$docs_code want 0, stdout='$under_docs' want '66')"

fx="$(fixture empty-label)"
cat > "$fx/issues.json" <<'JSON'
[
  {
    "number": 67,
    "title": "solvable-issues.sh: take the opt-in label from VERI_LABEL",
    "labels": [{"name": "ready-for-agent"}],
    "state": "OPEN",
    "body": "## What to build\n\nA label parameter with ready-for-agent as the default.\n\n## Blocked by\n\nNone.\n"
  },
  {
    "number": 68,
    "title": "walkthrough: draw rung 2",
    "labels": [{"name": "ready-for-agent:docs"}],
    "state": "OPEN",
    "body": "## Blocked by\n\nNone.\n"
  }
]
JSON

refused_run "$fx" VERI_LABEL=

{ [[ "$refused_code" == 2 ]] \
  && [[ ! -s "$refused_out" ]] \
  && [[ -s "$refused_err" ]]; } \
  && ok || no "VERI_LABEL set to the empty string is refused with exit 2 and a diagnostic on stderr, never treated as any label (exit=$refused_code want 2, stdout='$(tr '\n' '|' < "$refused_out")' want empty, stderr='$(tr '\n' ' ' < "$refused_err")' want a diagnostic)"

skill_doc="skills/tdd/SCOPE-LOOP.md"
procedure_doc="skills/tdd/SKILL.md"

loop_bullet() {  # loop_bullet <opening-line regex> <line that ends it>
  awk -v opens="$1" -v ends="$2" '
    $0 ~ opens { keep = 1 }
    $0 ~ ends  { keep = 0 }
    keep
  ' "$REPO_ROOT/$skill_doc"
}

doc_claims() {  # doc_claims <doc> <tag> <grep argument…>
  local doc="$1" tag="$2"; shift 2
  grep -q "$@" "$REPO_ROOT/$doc" || docs_missing="$docs_missing $doc:$tag"
}

docs_missing=""
for doc in "$skill_doc" README.md CONTEXT.md; do
  doc_claims "$doc" VERI_LABEL -e 'VERI_LABEL'
  doc_claims "$doc" one-label-per-loop -iE -e 'one[ -]label[ -]per[ -]loop'
done

[[ -z "$docs_missing" ]] \
  && ok || no "the three documents name VERI_LABEL and the one-label-per-loop partitioning use (missing:$docs_missing)"

exit3="$(loop_bullet '^- [*][*]Exit 3:' '^- [*][*]Exit 0:')"

{ [[ -n "$exit3" ]] && grep -q 'VERI_LABEL' <<<"$exit3"; } \
  && ok || no "the exit-3 instruction in $skill_doc names the label it drained (bullet='$(tr '\n' ' ' <<<"$exit3")' want a non-empty slice naming VERI_LABEL)"

fx="$(fixture url-blocked)"
url_issues() {  # url_issues <state-of-120>
  cat <<JSON
[
  {
    "number": 125,
    "title": "walkthrough: a line no commentary chunk claims is owed, not fatal",
    "labels": [{"name": "ready-for-agent"}],
    "state": "OPEN",
    "body": "## What to build\n\nLet the build print what it owes.\n\n## Blocked by\n\n- https://github.com/ztrange/veri/issues/120\n"
  },
  {
    "number": 120,
    "title": "docs-owed.sh: file the commentary debt",
    "labels": [{"name": "ready-for-agent"}],
    "state": "$1",
    "body": "## Blocked by\n\nNone.\n"
  }
]
JSON
}

url_issues OPEN > "$fx/issues.json"
run "$fx"; url_while_open="$out" url_open_code="$code"

url_issues CLOSED > "$fx/issues.json"
run "$fx"; url_once_closed="$out" url_closed_code="$code"

{ [[ "$url_open_code" == 0 && "$url_while_open" == "120" ]] \
  && [[ "$url_closed_code" == 0 && "$url_once_closed" == "125" ]]; } \
  && ok || no "a blocker written as a github.com issue URL blocks exactly as #<n> does (blocker open: exit=$url_open_code want 0, stdout='$url_while_open' want '120'; blocker closed: exit=$url_closed_code want 0, stdout='$url_once_closed' want '125')"

fx="$(fixture foreign-url)"
cat > "$fx/issues.json" <<'JSON'
[
  {
    "number": 131,
    "title": "solve-issue: narrate each phase to the issue thread",
    "labels": [{"name": "ready-for-agent"}],
    "state": "OPEN",
    "body": "## What to build\n\nA comment per phase.\n\n## Blocked by\n\n- https://github.com/ztrange/veri-demo-node/issues/120\n"
  },
  {
    "number": 120,
    "title": "docs-owed.sh: file the commentary debt",
    "labels": [{"name": "ready-for-agent"}],
    "state": "OPEN",
    "body": "## Blocked by\n\nNone.\n"
  }
]
JSON

run "$fx" --repo ztrange/veri

{ [[ "$code" == 0 ]] && [[ "$out" == $'120\n131' ]]; } \
  && ok || no "a URL naming another repository's issue is not read as a blocker in this one (exit=$code want 0, stdout='$out' want '120\\n131')"

header="$(awk '/^set -euo pipefail$/ {exit} {print}' "$SOLVABLE")"

header_names() {  # header_names <tag> <grep argument…>
  local tag="$1"; shift
  grep -q "$@" <<<"$header" || header_missing="$header_missing $tag"
}

header_missing=""
header_names hash-form -e '#<n>'
header_names url-form -E -e 'https://github\.com/[^ ]*/issues/'

{ [[ -n "$header" ]] && [[ -z "$header_missing" ]]; } \
  && ok || no "the header comment of solvable-issues.sh names both blocker spellings (missing:$header_missing; header slice above 'set -euo pipefail' is $(grep -c '' <<<"$header") lines, want a non-empty slice naming '#<n>' and a github.com issues URL)"

fx="$(fixture in-flight)"
cat > "$fx/issues.json" <<'JSON'
[
  {
    "number": 170,
    "title": "solvable-issues.sh lists an issue whose conductor is running",
    "labels": [{"name": "ready-for-agent"}],
    "state": "OPEN",
    "body": "## What to build\n\nA run in flight claims its issue from its first step.\n\n## Blocked by\n\nNone.\n"
  },
  {
    "number": 171,
    "title": "a run that bailed and left its worktree behind",
    "labels": [{"name": "ready-for-agent"}],
    "state": "OPEN",
    "body": "## Blocked by\n\nNone.\n"
  },
  {
    "number": 172,
    "title": "an issue nobody has started",
    "labels": [{"name": "ready-for-agent"}],
    "state": "OPEN",
    "body": "## Blocked by\n\nNone.\n"
  }
]
JSON

flight_repo="$work/in-flight"
mkdir -p "$flight_repo"
new_repo -b main "$flight_repo" >/dev/null 2>&1
git -C "$flight_repo" -c user.name=veri -c user.email=veri@example.test \
  commit -q --allow-empty -m initial >/dev/null 2>&1

claim() {  # claim <n> <pid>
  local wt="$flight_repo/.tdd/wt/$1"
  git -C "$flight_repo" worktree add -q -b "tdd/$1-slug" "$wt" main >/dev/null 2>&1
  mkdir -p "$wt/.tdd"
  printf '%s\n' "$2" > "$wt/.tdd/conductor.pid"
}

sh -c 'exit 0' & dead_pid=$!
wait "$dead_pid" 2>/dev/null || true

claim 170 "$$"
claim 171 "$dead_pid"

out="$(cd "$flight_repo" && VERI_GH_JSON="$fx" "$SOLVABLE" 2>/dev/null)" && code=0 || code=$?

{ [[ "$code" == 0 ]] && [[ "$out" == $'171\n172' ]]; } \
  && ok || no "an issue whose worktree holds a live conductor PID is withheld, one with a dead PID or no worktree is listed (exit=$code want 0, stdout='$(tr '\n' '|' <<<"$out")' want '171|172|'; live pid=$$, dead pid=$dead_pid)"

fx="$(fixture bailed)"
cat > "$fx/issues.json" <<'JSON'
[
  {
    "number": 173,
    "title": "a run that bailed before opening its draft PR",
    "labels": [{"name": "ready-for-agent"}],
    "state": "OPEN",
    "body": "## Blocked by\n\nNone.\n"
  }
]
JSON

claim 173 "$dead_pid"

out="$(cd "$flight_repo" && VERI_GH_JSON="$fx" "$SOLVABLE" 2>/dev/null)" && code=0 || code=$?

{ [[ "$code" == 0 ]] && [[ "$out" == 173 ]]; } \
  && ok || no "a bailed or killed run's issue — a dead conductor PID in its worktree's lock, no open PR — is listed again so a resume is still possible (exit=$code want 0, stdout='$(tr '\n' '|' <<<"$out")' want '173|'; dead pid=$dead_pid)"

context_md="CONTEXT.md"

solvable_entry_slice() {
  awk '/^\*\*Solvable\*\*:/ { keep = 1; next } keep && /^\*\*/ { exit } keep' \
    "$REPO_ROOT/$context_md"
}

solvable_entry="$(solvable_entry_slice)"

entry_claims() {  # entry_claims <tag> <grep argument…>
  local tag="$1"; shift
  grep -q "$@" <<<"$solvable_entry" || entry_missing="$entry_missing $tag"
}

entry_missing=""
if [[ -z "${solvable_entry// /}" ]]; then
  entry_missing="$entry_missing the-Solvable-entry-itself"
else
  entry_claims the-lock-by-name -F -e 'conductor.pid'
  entry_claims that-only-a-live-process-claims -iE \
    -e 'kill -0|alive|still running|live (conductor|process|run)'
fi

[[ -z "$entry_missing" ]] \
  && ok || no "$context_md's Solvable entry names the conductor PID lock, and a live holder, as what marks a run in flight (missing:$entry_missing)"

step1="$(awk '/^### 1\./ { keep = 1; next } keep && /^### / { exit } keep' "$REPO_ROOT/$procedure_doc")"

step1_missing=""
if [[ -z "${step1// /}" ]]; then
  step1_missing="$step1_missing step-1-itself"
else
  grep -qE '> *"?\.tdd/conductor\.pid' <<<"$step1" \
    || step1_missing="$step1_missing the-write-into-the-lock"
  grep -qE '\$PPID[^>]*> *"?\.tdd/conductor\.pid' <<<"$step1" \
    || step1_missing="$step1_missing the-pid-that-outlives-one-command"
fi

[[ -z "$step1_missing" ]] \
  && ok || no "$procedure_doc step 1 tells the conductor to write its own long-lived pid (\$PPID, not \$\$) into .tdd/conductor.pid, so the lock cases 17 and 18 read is one a real run leaves (missing:$step1_missing)"

fx="$(fixture pushed-branch)"
cat > "$fx/issues.json" <<'JSON'
[
  {
    "number": 191,
    "title": "a run's commits live on one disk until the draft PR",
    "labels": [{"name": "ready-for-agent"}],
    "state": "OPEN",
    "body": "## What to build\n\nThe conductor pushes the branch after each step's green commit.\n\n## Blocked by\n\nNone.\n"
  }
]
JSON

pushed_repo="$work/pushed"
pushed_remote="$work/pushed-remote.git"
mkdir -p "$pushed_repo"
new_repo -b main "$pushed_repo" >/dev/null 2>&1
git -C "$pushed_repo" -c user.name=veri -c user.email=veri@example.test \
  commit -q --allow-empty -m initial >/dev/null 2>&1
new_repo --bare "$pushed_remote" >/dev/null 2>&1
git -C "$pushed_repo" remote add origin "$pushed_remote"

pushed_wt="$pushed_repo/.tdd/wt/191"
git -C "$pushed_repo" worktree add -q -b tdd/191-slug "$pushed_wt" main >/dev/null 2>&1
git -C "$pushed_wt" push -q --set-upstream origin HEAD >/dev/null 2>&1

on_remote="$(git -C "$pushed_repo" ls-remote --heads origin tdd/191-slug 2>/dev/null)"

out="$(cd "$pushed_repo" && VERI_GH_JSON="$fx" "$SOLVABLE" 2>/dev/null)" && code=0 || code=$?

{ [[ -n "$on_remote" ]] && [[ "$code" == 0 ]] && [[ "$out" == 191 ]]; } \
  && ok || no "a branch on the remote, with no open PR and no live conductor pid, leaves its issue takeable (exit=$code want 0, stdout='$(tr '\n' '|' <<<"$out")' want '191|'; ls-remote tdd/191-slug='$on_remote', want non-empty)"


fx="$(fixture bug-band)"
cat > "$fx/issues.json" <<'JSON'
[
  {
    "number": 117,
    "title": "a capability somebody wants",
    "labels": [{"name": "ready-for-agent"}],
    "state": "OPEN",
    "body": "## Blocked by\n\nNone.\n"
  },
  {
    "number": 120,
    "title": "a thing that is broken",
    "labels": [{"name": "ready-for-agent"}, {"name": "bug"}],
    "state": "OPEN",
    "body": "## Blocked by\n\nNone.\n"
  },
  {
    "number": 108,
    "title": "an older capability somebody wants",
    "labels": [{"name": "ready-for-agent"}],
    "state": "OPEN",
    "body": "## Blocked by\n\nNone.\n"
  },
  {
    "number": 124,
    "title": "a second thing that is broken",
    "labels": [{"name": "bug"}, {"name": "ready-for-agent"}],
    "state": "OPEN",
    "body": "## Blocked by\n\nNone.\n"
  }
]
JSON

label_run "$fx" -u VERI_PRIORITY_LABEL

{ [[ "$code" == 0 ]] && [[ "$out" == $'120\n124\n108\n117' ]]; } \
  && ok || no "a bug-labelled issue is printed ahead of a lower-numbered plain one, each band ascending by number (exit=$code want 0, stdout='$(tr '\n' '|' <<<"$out")' want '120|124|108|117|')"

fx="$(fixture priority-band)"
cat > "$fx/issues.json" <<'JSON'
[
  {
    "number": 120,
    "title": "a thing that is broken",
    "labels": [{"name": "ready-for-agent"}, {"name": "bug"}],
    "state": "OPEN",
    "body": "## Blocked by\n\nNone.\n"
  },
  {
    "number": 160,
    "title": "a thing that is broken and wanted today",
    "labels": [{"name": "bug"}, {"name": "ready-for-agent"}, {"name": "priority"}],
    "state": "OPEN",
    "body": "## Blocked by\n\nNone.\n"
  },
  {
    "number": 150,
    "title": "a capability wanted today",
    "labels": [{"name": "priority"}, {"name": "ready-for-agent"}],
    "state": "OPEN",
    "body": "## Blocked by\n\nNone.\n"
  }
]
JSON

label_run "$fx" -u VERI_PRIORITY_LABEL

{ [[ "$code" == 0 ]] && [[ "$out" == $'150\n160\n120' ]]; } \
  && ok || no "a priority-labelled issue is printed ahead of a lower-numbered bug, and one carrying both labels sorts in the priority band (exit=$code want 0, stdout='$(tr '\n' '|' <<<"$out")' want '150|160|120|')"

fx="$(fixture priority-without-opt-in)"
cat > "$fx/issues.json" <<'JSON'
[
  {
    "number": 170,
    "title": "an unvetted idea somebody flagged as urgent",
    "labels": [{"name": "priority"}],
    "state": "OPEN",
    "body": "## What to build\n\nSomething, urgently.\n\n## Blocked by\n\nNone.\n"
  },
  {
    "number": 180,
    "title": "a capability veri may take",
    "labels": [{"name": "ready-for-agent"}],
    "state": "OPEN",
    "body": "## Blocked by\n\nNone.\n"
  }
]
JSON

label_run "$fx" -u VERI_PRIORITY_LABEL

{ [[ "$code" == 0 ]] && [[ "$out" == "180" ]]; } \
  && ok || no "the priority label alone never opts an issue in (exit=$code want 0, stdout='$(tr '\n' '|' <<<"$out")' want '180|')"


fx="$(fixture band-never-enlarges)"
cat > "$fx/issues.json" <<'JSON'
[
  {
    "number": 189,
    "title": "the open blocker",
    "labels": [],
    "state": "OPEN",
    "body": "## Blocked by\n\nNone.\n"
  },
  {
    "number": 190,
    "title": "a capability wanted today, waiting on another",
    "labels": [{"name": "ready-for-agent"}, {"name": "priority"}],
    "state": "OPEN",
    "body": "## Blocked by\n\n#189\n"
  },
  {
    "number": 191,
    "title": "a thing that is broken, already in flight",
    "labels": [{"name": "ready-for-agent"}, {"name": "bug"}],
    "state": "OPEN",
    "body": "## Blocked by\n\nNone.\n"
  },
  {
    "number": 192,
    "title": "a capability wanted today, already done",
    "labels": [{"name": "ready-for-agent"}, {"name": "priority"}],
    "state": "CLOSED",
    "body": "## Blocked by\n\nNone.\n"
  },
  {
    "number": 195,
    "title": "a capability veri may take",
    "labels": [{"name": "ready-for-agent"}],
    "state": "OPEN",
    "body": "## Blocked by\n\nNone.\n"
  }
]
JSON
cat > "$fx/prs.json" <<'JSON'
[
  {
    "state": "OPEN",
    "body": "Closes #191\n"
  }
]
JSON

label_run "$fx" -u VERI_PRIORITY_LABEL

{ [[ "$code" == 0 ]] && [[ "$out" == "195" ]]; } \
  && ok || no "a priority or bug issue that is blocked, claimed or closed is still not printed (exit=$code want 0, stdout='$(tr '\n' '|' <<<"$out")' want '195|')"


fx="$(fixture priority-label-tunable)"
cat > "$fx/issues.json" <<'JSON'
[
  {
    "number": 100,
    "title": "a capability veri may take",
    "labels": [{"name": "ready-for-agent"}],
    "state": "OPEN",
    "body": "## Blocked by\n\nNone.\n"
  },
  {
    "number": 200,
    "title": "a capability wanted today",
    "labels": [{"name": "ready-for-agent"}, {"name": "priority"}],
    "state": "OPEN",
    "body": "## Blocked by\n\nNone.\n"
  }
]
JSON

refused_run "$fx" VERI_PRIORITY_LABEL=

label_run "$fx" -u VERI_PRIORITY_LABEL

{ [[ "$refused_code" == 2 ]] \
  && [[ ! -s "$refused_out" ]] \
  && [[ -s "$refused_err" ]] \
  && [[ "$code" == 0 ]] && [[ "$out" == $'200\n100' ]]; } \
  && ok || no "VERI_PRIORITY_LABEL set to the empty string is refused with exit 2 and a diagnostic, while unset defaults to the priority label (set-but-empty: exit=$refused_code want 2, stdout='$(tr '\n' '|' < "$refused_out")' want empty, stderr='$(tr '\n' ' ' < "$refused_err")' want a diagnostic; unset: exit=$code want 0, stdout='$(tr '\n' '|' <<<"$out")' want '200|100|')"



fx="$(fixture no-band-labels)"
cat > "$fx/issues.json" <<'JSON'
[
  {
    "number": 210,
    "title": "a capability veri may take",
    "labels": [{"name": "ready-for-agent"}],
    "state": "OPEN",
    "body": "## Blocked by\n\nNone.\n"
  },
  {
    "number": 208,
    "title": "another capability veri may take",
    "labels": [{"name": "ready-for-agent"}],
    "state": "OPEN",
    "body": "## Blocked by\n\nNone.\n"
  },
  {
    "number": 207,
    "title": "a capability already in flight",
    "labels": [{"name": "ready-for-agent"}],
    "state": "OPEN",
    "body": "## Blocked by\n\nNone.\n"
  },
  {
    "number": 209,
    "title": "a capability waiting on another",
    "labels": [{"name": "ready-for-agent"}],
    "state": "OPEN",
    "body": "## Blocked by\n\n#212\n"
  },
  {
    "number": 211,
    "title": "an idea nobody has vetted for veri yet",
    "labels": [],
    "state": "OPEN",
    "body": "## Blocked by\n\nNone.\n"
  },
  {
    "number": 212,
    "title": "the open blocker",
    "labels": [],
    "state": "OPEN",
    "body": "## Blocked by\n\nNone.\n"
  },
  {
    "number": 213,
    "title": "a capability already done",
    "labels": [{"name": "ready-for-agent"}],
    "state": "CLOSED",
    "body": "## Blocked by\n\nNone.\n"
  }
]
JSON
cat > "$fx/prs.json" <<'JSON'
[
  {
    "state": "OPEN",
    "body": "Closes #207\n"
  }
]
JSON

printf '208\n210\n' > "$work/no-band-labels.expected"

refused_run "$fx" -u VERI_PRIORITY_LABEL

{ [[ "$refused_code" == 0 ]] \
  && cmp -s "$refused_out" "$work/no-band-labels.expected"; } \
  && ok || no "with no issue carrying either band label the output is byte-identical to today's (exit=$refused_code want 0, stdout='$(tr '\n' '|' < "$refused_out")' want '208|210|')"


narration="$(loop_bullet '^- [*][*]Exit 0:' '^### ')"

{ [[ -n "$narration" ]] \
  && grep -qiE 'lower[ -]numbered' <<<"$narration" \
  && grep -qE 'priority' <<<"$narration" \
  && grep -qE 'bug' <<<"$narration"; } \
  && ok || no "the exit-0 instruction in $skill_doc says when it took an issue ahead of a lower-numbered one and which band did it (bullet='$(tr '\n' ' ' <<<"$narration")' want a non-empty slice naming a lower-numbered issue and both bands, priority and bug)"



paging_gh() {  # paging_gh <dir> < <case body>
  mkdir -p "$1"
  { cat <<'STUB'
#!/bin/sh
limit=30
prev=""
for arg in "$@"; do
  case "$prev" in --limit|-L) limit="$arg" ;; esac
  case "$arg" in --limit=*) limit="${arg#--limit=}" ;; esac
  prev="$arg"
done
STUB
    cat; } > "$1/gh"
  chmod +x "$1/gh"
}

paged_run() {  # paged_run <dir of a paging_gh stub>; the real gh path, sets $out and $code
  out="$(env -u VERI_GH_JSON -u VERI_LABEL -u VERI_PRIORITY_LABEL VERI_GH_DRIVER=auto PATH="$1:$PATH" \
         "$SOLVABLE" 2>/dev/null)" && code=0 || code=$?
}

pagedir="$work/paging-bin"
paging_gh "$pagedir" <<'STUB'
case "$1 $2" in
  "issue list")
    python3 -c '
import json, sys
limit = int(sys.argv[1])
issues = [
    {"number": n, "title": "issue %d" % n, "state": "OPEN",
     "labels": [{"name": "ready-for-agent"}] if n == 101 else [],
     "body": "## Blocked by\n\nNone.\n"}
    for n in range(140, 100, -1)
]
print(json.dumps(issues[:limit]))
' "$limit" ;;
  "pr list") echo '[]' ;;
esac
STUB

paged_run "$pagedir"

{ [[ "$code" == 0 && "$out" == "101" ]]; } \
  && ok || no "an opted-in, unblocked issue older than gh's default page of 30 is printed (40 open issues, only the oldest #101 opted in: exit=$code want 0, stdout='$out' want '101')"


blockdir="$work/paging-blocker-bin"
paging_gh "$blockdir" <<'STUB'
case "$1 $2" in
  "issue list")
    python3 -c '
import json, sys
limit = int(sys.argv[1])
issues = [
    {"number": n, "title": "issue %d" % n, "state": "OPEN",
     "labels": [{"name": "ready-for-agent"}] if n == 140 else [],
     "body": "## Blocked by\n\n- #101\n" if n == 140 else "## Blocked by\n\nNone.\n"}
    for n in range(140, 100, -1)
]
print(json.dumps(issues[:limit]))
' "$limit" ;;
  "pr list") echo '[]' ;;
esac
STUB

paged_run "$blockdir"

{ [[ "$code" == 3 && -z "$out" ]]; } \
  && ok || no "an issue blocked by an open issue older than gh's default page of 30 is not printed (40 open issues, #140 opted in and blocked by the oldest #101: exit=$code want 3, stdout='$out' want '')"


prpagedir="$work/paging-prs-bin"
paging_gh "$prpagedir" <<'STUB'
case "$1 $2" in
  "issue list")
    printf '%s\n' '[{"number": 7, "title": "issue 7", "state": "OPEN", "labels": [{"name": "ready-for-agent"}], "body": "## Blocked by\n\nNone.\n"}]' ;;
  "pr list")
    python3 -c '
import json, sys
limit = int(sys.argv[1])
prs = [
    {"state": "OPEN", "body": "Closes #7" if i == 39 else "Closes #%d" % (1000 + i)}
    for i in range(40)
]
print(json.dumps(prs[:limit]))
' "$limit" ;;
esac
STUB

paged_run "$prpagedir"

{ [[ "$code" == 3 && -z "$out" ]]; } \
  && ok || no "an open PR older than gh's default page of 30 saying Closes #<n> still claims its issue (40 open PRs, only the oldest says Closes #7: exit=$code want 3, stdout='$out' want '')"


fx="$(fixture claimed-by-pr-dead-pid)"
cat > "$fx/issues.json" <<'JSON'
[
  {
    "number": 175,
    "title": "a run that bailed after opening its draft PR",
    "labels": [{"name": "ready-for-agent"}],
    "state": "OPEN",
    "body": "## Blocked by\n\nNone.\n"
  }
]
JSON
cat > "$fx/prs.json" <<'JSON'
[
  {
    "state": "OPEN",
    "body": "Draft PR opened by a /tdd run that bailed.\n\nCloses #175\n"
  }
]
JSON

claim 175 "$dead_pid"

out="$(cd "$flight_repo" && VERI_GH_JSON="$fx" "$SOLVABLE" 2>/dev/null)" && code=0 || code=$?

{ [[ "$code" == 3 ]] && [[ -z "$out" ]]; } \
  && ok || no "an issue an open PR Closes stays out of the pool though its conductor pid is dead (exit=$code want 3, stdout='$(tr '\n' '|' <<<"$out")' want ''; dead pid=$dead_pid)"


CLAIM_PR='closes #|pull request|open pr|draft pr'
CLAIM_ANY_MACHINE='every machine|any machine|other machine|another machine|all machines|across machines|cross-machine|machine-independent'
CLAIM_WORD='claim'
CLAIM_LOCK='conductor\.pid|pid lock|the lock|the pid'
CLAIM_WORKTREE='worktree'
CLAIM_GUARD='guard'
CLAIM_LOCAL='same[- ]machine|one machine|machine-local|local'
CLAIM_ADR='adr[ -]?[0-9]{4}'

says_all() {
  local text="$1"; shift
  local line re
  while IFS= read -r line; do
    for re in "$@"; do
      [[ "$line" =~ $re ]] || continue 2
    done
    return 0
  done <<<"$text"
  return 1
}

claim_says() {
  local passage="$1" tag="$2" text="$3"; shift 3
  says_all "$text" "$@" || claim_missing="$claim_missing $passage:$tag"
}

claim_entry="$(solvable_entry_slice | tr '\n' ' ' | tr '[:upper:]' '[:lower:]')"
claim_header="$(awk 'NR == 1 { next }
                     !/^#/ { exit }
                     /^#[[:space:]]*$/ { if (rec != "") print rec; rec = ""; next }
                     { line = $0; sub(/^#[[:space:]]?/, "", line)
                       rec = (rec == "" ? line : rec " " line) }
                     END { if (rec != "") print rec }' "$SOLVABLE" | tr '[:upper:]' '[:lower:]')"

claim_passage() {
  local passage="$1" empty_tag="$2" text="$3"
  if [[ -z "${text// /}" ]]; then
    claim_missing="$claim_missing $passage:$empty_tag"
    return
  fi
  claim_says "$passage" the-open-PR-as-the-claim-every-machine-sees \
    "$text" "$CLAIM_PR" "$CLAIM_ANY_MACHINE" "$CLAIM_WORD"
  claim_says "$passage" the-lock-as-one-machines-worktree-guard \
    "$text" "$CLAIM_LOCK" "$CLAIM_WORKTREE" "$CLAIM_GUARD" "$CLAIM_LOCAL"
  claim_says "$passage" the-ADR-recording-the-decision "$text" "$CLAIM_ADR"
}

claim_missing=""
claim_passage "$context_md" the-Solvable-entry-itself "$claim_entry"
claim_passage solvable-issues.sh the-header-comment-itself "$claim_header"

[[ -z "$claim_missing" ]] \
  && ok || no "$context_md's Solvable entry and solvable-issues.sh's header say an open PR is the claim every machine sees and the conductor.pid lock is only that machine's worktree guard, each citing the ADR that records it (missing:$claim_missing)"


bad_arg="$(fixture bad-argument)"
VERI_GH_JSON="$bad_arg" "$SOLVABLE" --repo >"$bad_arg/out" 2>"$bad_arg/err" && code=0 || code=$?
{ [[ "$code" == 2 ]] && [[ ! -s "$bad_arg/out" ]] \
  && [[ "$(cat "$bad_arg/err")" == "usage: solvable-issues.sh [--repo owner/name]" ]] \
  && [[ "$(wc -l < "$bad_arg/err" | tr -d ' ')" == 1 ]]; } \
  && ok || no "--repo with no value exits 2 with nothing on stdout and stderr exactly the usage line (exit=$code want 2, stdout='$(cat "$bad_arg/out")' want '', stderr='$(cat "$bad_arg/err")' want 'usage: solvable-issues.sh [--repo owner/name]')"

sym_fx="$(fixture symlinked-skill)"
cat > "$sym_fx/issues.json" <<'JSON'
[
  {"number": 5, "title": "in flight", "labels": [{"name": "ready-for-agent"}], "state": "OPEN", "body": "## Blocked by\n\nNone.\n"},
  {"number": 6, "title": "takeable", "labels": [{"name": "ready-for-agent"}], "state": "OPEN", "body": "## Blocked by\n\nNone.\n"}
]
JSON
sym_repo="$work/symlinked-skill/repo"
new_repo -b main "$sym_repo" >/dev/null 2>&1
git -C "$sym_repo" -c user.name=veri -c user.email=veri@example.test \
  commit -q --allow-empty -m initial >/dev/null 2>&1
git -C "$sym_repo" worktree add -q -b linked "$work/symlinked-skill/linked" main >/dev/null 2>&1
mkdir -p "$sym_repo/.tdd/wt/5/.tdd"
printf '%s\n' "$$" > "$sym_repo/.tdd/wt/5/.tdd/conductor.pid"
ln -s "$(cd "$HERE/../.." && pwd)" "$work/symlinked-skill/skill-link"
in_place_out="$(cd "$work/symlinked-skill/linked" && VERI_GH_JSON="$sym_fx" "$SOLVABLE" 2>/dev/null)" \
  && in_place_code=0 || in_place_code=$?
linked_out="$(cd "$work/symlinked-skill/linked" \
  && VERI_GH_JSON="$sym_fx" "$work/symlinked-skill/skill-link/scripts/solvable-issues.sh" 2>/dev/null)" \
  && linked_code=0 || linked_code=$?
{ [[ "$in_place_code" == 0 && "$in_place_out" == 6 ]] \
  && [[ "$linked_code" == "$in_place_code" && "$linked_out" == "$in_place_out" ]]; } \
  && ok || no "run through a symlink to the skill directory from a linked worktree, solvable-issues.sh prints the same numbers and exit code as in place, the issue locked under the main working tree withheld either way (in place: exit=$in_place_code stdout='$(tr '\n' '|' <<<"$in_place_out")' want 0 and '6'; through the symlink: exit=$linked_code stdout='$(tr '\n' '|' <<<"$linked_out")' want the same)"

mkdir -p "$work/refused-driver/bin"
printf '#!/bin/sh\necho "gh $*" >> "$GH_CALLS"\necho "[]"\n' > "$work/refused-driver/bin/gh"
chmod +x "$work/refused-driver/bin/gh"
driver_problems=""
for driver in '' REST gql; do
  : > "$work/refused-driver/calls"
  out="$(env -u VERI_GH_JSON -u VERI_LABEL -u VERI_PRIORITY_LABEL VERI_GH_DRIVER="$driver" \
         PATH="$work/refused-driver/bin:$PATH" GH_CALLS="$work/refused-driver/calls" \
         "$SOLVABLE" 2>"$work/refused-driver/err")" && code=0 || code=$?
  err="$(cat "$work/refused-driver/err")"
  { [[ "$code" == 2 && -z "$out" && ! -s "$work/refused-driver/calls" ]] \
    && [[ "$(wc -l < "$work/refused-driver/err" | tr -d ' ')" == 1 && "$err" == *VERI_GH_DRIVER* && "$err" == *"'$driver'"* ]]; } \
    || driver_problems+="VERI_GH_DRIVER='$driver': exit=$code stdout='$out' stderr='$(tr '\n' '|' <<<"$err")' gh calls='$(tr '\n' '|' < "$work/refused-driver/calls")'; "
done

[[ -z "$driver_problems" ]] \
  && ok || no "with VERI_GH_DRIVER empty, REST or gql, solvable-issues.sh starts no gh process, prints nothing on stdout, exits 2 and prints one stderr line naming VERI_GH_DRIVER and the value ($driver_problems want exit 2, empty stdout, no gh call and one stderr line naming VERI_GH_DRIVER and the value)"
fx="$(fixture graphql-refused)"
cat > "$fx/issues.json" <<'JSON'
[
  {"number": 70, "title": "unblocked", "labels": [{"name": "ready-for-agent"}], "state": "OPEN",
   "body": "## Blocked by\n\nNone.\n"},
  {"number": 71, "title": "blocked by an open one", "labels": [{"name": "ready-for-agent"}], "state": "OPEN",
   "body": "## Blocked by\n\n#72\n"},
  {"number": 72, "title": "not opted in", "labels": [], "state": "OPEN", "body": ""},
  {"number": 73, "title": "claimed by an open PR", "labels": [{"name": "ready-for-agent"}], "state": "OPEN",
   "body": "## Blocked by\n\nNone.\n"},
  {"number": 74, "title": "priority", "labels": [{"name": "ready-for-agent"}, {"name": "priority"}], "state": "OPEN",
   "body": "## Blocked by\n\nNone.\n"}
]
JSON
cat > "$fx/prs.json" <<'JSON'
[{"state": "OPEN", "body": "Draft PR opened by a /tdd run.\n\nCloses #73\n"}]
JSON
python3 -c '
import json, sys
fx = sys.argv[1]
filler = [{"number": 100 + k, "title": "filler", "labels": [], "state": "OPEN", "body": ""} for k in range(110)]
json.dump(filler + json.load(open(fx + "/issues.json")), open(fx + "/issues.json", "w"))
json.dump([{"state": "OPEN", "body": ""}] * 105 + json.load(open(fx + "/prs.json")), open(fx + "/prs.json", "w"))
issues = json.load(open(fx + "/issues.json"))
for i in issues:
    i["state"] = i["state"].lower()
    i["body"] = i["body"] or None
    i["labels"] = [dict(l, id=100 + k, color="ededed") for k, l in enumerate(i["labels"])]
json.dump(issues, open(fx + "/rest-issues.json", "w"))
prs = json.load(open(fx + "/prs.json"))
pulls = [dict(p, number=900 + k, state=p["state"].lower(), draft=True) for k, p in enumerate(prs)]
json.dump(pulls, open(fx + "/rest-pulls.json", "w"))
' "$fx"

refusedir="$work/graphql-refusing-bin"
mkdir -p "$refusedir"
cat > "$refusedir/gh" <<'STUB'
#!/bin/sh
refusal='GitHub GraphQL is not available from Claude Code sessions; use the REST API (gh api repos/{owner}/{repo}/...)'
case "$1" in
  issue|pr|repo) echo "HTTP 403: $refusal" >&2; exit 1 ;;
esac
case "$*" in
  "api graphql"*) echo "HTTP 403: $refusal" >&2; exit 1 ;;
  *-q*|*--jq*|*--template*) echo "gh stub: unexpected call: gh $*" >&2; exit 1 ;;
  "api "*"repos/{owner}/{repo}/issues"*) file="$GH_REST_ISSUES" ;;
  "api "*"repos/{owner}/{repo}/pulls"*) file="$GH_REST_PULLS" ;;
  *) echo "gh stub: unexpected call: gh $*" >&2; exit 1 ;;
esac
case " $* " in *" --paginate "*) paginate=1 ;; *) paginate=0 ;; esac
per_page="$(printf '%s\n' "$*" | sed -n 's/.*[?&]per_page=\([0-9]*\).*/\1/p')"
page="$(printf '%s\n' "$*" | sed -n 's/.*[?&]page=\([0-9]*\).*/\1/p')"
exec python3 -c '
import json, sys
items = json.load(open(sys.argv[1]))
size = min(int(sys.argv[3] or 30), 100)
pages = [items[k:k + size] for k in range(0, len(items), size)] or [[]]
n = int(sys.argv[4] or 1)
sys.stdout.write("".join(json.dumps(p) for p in (pages if sys.argv[2] == "1" else pages[n - 1:n] or [[]])))
' "$file" "$paginate" "$per_page" "$page"
STUB
chmod +x "$refusedir/gh"

refused_run() {  # refused_run <gh-dir> [script args...]; sets $out, $err and $code
  local dir="$1"; shift
  out="$(env -u VERI_GH_JSON -u VERI_LABEL -u VERI_PRIORITY_LABEL PATH="$dir:$PATH" \
         GH_REST_ISSUES="$fx/rest-issues.json" GH_REST_PULLS="$fx/rest-pulls.json" \
         "$SOLVABLE" "$@" 2>"$work/refused-stderr")" && code=0 || code=$?
  err="$(cat "$work/refused-stderr")"
}

gh_run "$work/argv-graphql-working"; working="$out" working_code="$code"

refused_run "$refusedir"

{ [[ "$working_code" == 0 && "$working" == $'74\n70' ]] \
  && [[ "$code" == "$working_code" && "$out" == "$working" ]]; } \
  && ok || no "against a gh that refuses GraphQL with the 403 and answers REST under repos/{owner}/{repo}/ a page at a time, no arguments prints the same issue numbers and exit code as a working gh, across more than one 100-item page (#568) (working gh: exit=$working_code stdout='$(tr '\n' '|' <<<"$working")' want 0 and '74|70'; GraphQL refused: exit=$code stdout='$(tr '\n' '|' <<<"$out")' want the same)"

nameddir="$work/graphql-refusing-named-bin"
mkdir -p "$nameddir"
sed 's#"repos/{owner}/{repo}/#"repos/owner/name/#' "$refusedir/gh" > "$nameddir/gh"
chmod +x "$nameddir/gh"

gh_run "$work/argv-graphql-working-named" --repo owner/name; working="$out" working_code="$code"

refused_run "$nameddir" --repo owner/name

{ [[ "$working_code" == 0 && "$working" == $'74\n70' ]] \
  && [[ "$code" == "$working_code" && "$out" == "$working" ]]; } \
  && ok || no "--repo owner/name, against a gh that refuses GraphQL and answers REST only under repos/owner/name/, prints the same issue numbers and exit code as a working gh (#568) (working gh: exit=$working_code stdout='$(tr '\n' '|' <<<"$working")' want 0 and '74|70'; GraphQL refused: exit=$code stdout='$(tr '\n' '|' <<<"$out")' want the same)"


env -u VERI_GH_JSON -u VERI_LABEL -u VERI_PRIORITY_LABEL VERI_GH_DRIVER=auto PATH="$stubdir:$PATH" ARGV_OUT="$work/argv-stderr-working" \
  GH_ISSUES="$fx/issues.json" GH_PRS="$fx/prs.json" \
  "$SOLVABLE" >/dev/null 2>"$work/stderr-working" || true
refused_run "$refusedir"; refused_err="$err"
working_err="$(cat "$work/stderr-working")"

{ [[ -z "$working_err" && -z "$refused_err" ]]; } \
  && ok || no "against a gh that refuses GraphQL with the 403, solvable-issues.sh writes nothing to stderr, the same as against a working gh: the refusal is not passed through to the caller (#568) (working gh stderr='$(tr '\n' '|' <<<"$working_err")' want ''; GraphQL refused stderr='$(tr '\n' '|' <<<"$refused_err")' want '')"

python3 -c '
import json, sys
fx = sys.argv[1]
issues = [
    {"number": 70, "title": "unblocked", "labels": [{"name": "ready-for-agent"}], "state": "open", "body": "## Blocked by\n\nNone.\n"},
    {"number": 75, "title": "a pull request", "labels": [{"name": "ready-for-agent"}], "state": "open", "body": "",
     "pull_request": {"url": "https://api.github.com/repos/owner/name/pulls/75"}},
]
json.dump(issues, open(fx + "/rest-issues-with-pr.json", "w"))
' "$fx"
GH_ISSUES_WITH_PR="$fx/rest-issues-with-pr.json"
out="$(env -u VERI_GH_JSON -u VERI_LABEL -u VERI_PRIORITY_LABEL PATH="$refusedir:$PATH" \
       GH_REST_ISSUES="$GH_ISSUES_WITH_PR" GH_REST_PULLS="$fx/rest-pulls.json" \
       "$SOLVABLE" 2>/dev/null)" && code=0 || code=$?

{ [[ "$code" == 0 && "$out" == "70" ]]; } \
  && ok || no "against a gh that refuses GraphQL, a /issues REST item carrying pull_request is not counted as a solvable issue even with the opt-in label (#568) (exit=$code want 0, stdout='$(tr '\n' '|' <<<"$out")' want '70')"


argcapdir="$work/argcap-bin"
argcap_python3_stub "$argcapdir"

short_fx="$(fixture large-doc-short)" long_fx="$(fixture large-doc-long)"
python3 -c '
import json, sys
def issues(pad):
    return [{"number": n, "title": "issue %d" % n,
             "labels": [{"name": "ready-for-agent"}] if n % 2 == 0 else [],
             "state": "OPEN",
             "body": "## What to build\n\n" + pad + "\n\n## Blocked by\n\nNone.\n"}
            for n in range(1, 41)]
json.dump(issues("short"), open(sys.argv[1] + "/issues.json", "w"))
json.dump(issues("x" * 8192), open(sys.argv[2] + "/issues.json", "w"))
' "$short_fx" "$long_fx"
long_size="$(wc -c < "$long_fx/issues.json" | tr -d ' ')"

out="$(PATH="$argcapdir:$PATH" VERI_GH_JSON="$short_fx" "$SOLVABLE" 2>/dev/null)" && code=0 || code=$?
short_out="$out" short_code="$code"
out="$(PATH="$argcapdir:$PATH" VERI_GH_JSON="$long_fx" "$SOLVABLE" 2>/dev/null)" && code=0 || code=$?

{ [[ "$long_size" -gt 262144 ]] \
  && [[ "$short_code" == 0 && "$short_out" == "$(seq 2 2 40)" ]] \
  && [[ "$code" == 0 && "$out" == "$short_out" ]]; } \
  && ok || no "a VERI_GH_JSON issues.json larger than 256 KiB prints the same numbers and exits 0 as the same issues with short bodies, under a python3 that refuses any argument over 128 KiB the way Linux does (#591) (long issues.json=$long_size bytes want >262144; short: exit=$short_code stdout='$(tr '\n' '|' <<<"$short_out")' want 0 and '2|4|…|40'; long: exit=$code stdout='$(tr '\n' '|' <<<"$out")' want the same)"


issue_pages=(
  '{"number": 70, "title": "a", "labels": [{"name": "ready-for-agent"}], "body": "## Blocked by\n\n- #74\n", "state": "open"}, {"number": 71, "title": "b", "labels": [{"name": "ready-for-agent"}], "body": "", "state": "closed"}'
  '{"number": 72, "title": "c", "labels": [{"name": "ready-for-agent"}], "body": "", "state": "open"}, {"number": 73, "title": "d", "labels": [{"name": "ready-for-agent"}, {"name": "bug"}], "body": "", "state": "open"}'
  '{"number": 74, "title": "e", "labels": [], "body": "", "state": "open"}, {"number": 75, "title": "f", "labels": [{"name": "ready-for-agent"}, {"name": "priority"}], "body": "", "state": "open"}'
)
pull_pages=(
  '{"number": 1, "state": "closed", "body": "Closes #73"}, {"number": 2, "state": "open", "body": ""}'
  '{"number": 3, "state": "open", "body": ""}, {"number": 4, "state": "closed", "body": ""}'
  '{"number": 5, "state": "open", "body": "Closes #72"}, {"number": 6, "state": "closed", "body": ""}'
)
mkdir -p "$work/three-pages/one" "$work/three-pages/three" "$work/three-pages/bin"
for i in 0 1 2; do
  printf '[%s]\n' "${issue_pages[i]}" > "$work/three-pages/three/issues-$((i + 1)).json"
  printf '[%s]\n' "${pull_pages[i]}" > "$work/three-pages/three/pulls-$((i + 1)).json"
done
(IFS=,; printf '[%s]\n' "${issue_pages[*]}" > "$work/three-pages/one/issues-1.json"
 printf '[%s]\n' "${pull_pages[*]}" > "$work/three-pages/one/pulls-1.json")
cat > "$work/three-pages/bin/gh" <<'STUB'
#!/bin/sh
proxy='gh: Numeric-ID repository paths (repositories/{id}/...) are not supported through this proxy. Use repos/{owner}/{repo}/... endpoints instead. (HTTP 403)'
case "$1" in
  issue|pr|repo) echo "HTTP 403: GitHub GraphQL is not available from Claude Code sessions" >&2; exit 1 ;;
  api) shift ;;
  *) echo "gh stub: unexpected call: gh $*" >&2; exit 1 ;;
esac
paginate="" path=""
for arg in "$@"; do
  case "$arg" in
    --paginate) paginate=1 ;;
    -*) echo "gh stub: unsupported flag $arg" >&2; exit 1 ;;
    *) path="$arg" ;;
  esac
done
case "$path" in
  *repositories/*) echo "$proxy" >&2; exit 1 ;;
  "repos/{owner}/{repo}/issues"*) list=issues ;;
  "repos/{owner}/{repo}/pulls"*) list=pulls ;;
  *) echo "gh stub: unexpected path $path" >&2; exit 1 ;;
esac
page="$(printf '%s\n' "$path" | sed -n 's/.*[?&]page=\([0-9][0-9]*\).*/\1/p')"
[ -n "$page" ] || page=1
if [ -f "$GH_FX/$list-$page.json" ]; then cat "$GH_FX/$list-$page.json"; else echo '[]'; fi
if [ -n "$paginate" ] && [ -f "$GH_FX/$list-$((page + 1)).json" ]; then echo "$proxy" >&2; exit 1; fi
exit 0
STUB
chmod +x "$work/three-pages/bin/gh"
three_page_run() {  # three_page_run <one|three>; sets $out and $code
  out="$(env -u VERI_GH_JSON -u VERI_LABEL -u VERI_PRIORITY_LABEL PATH="$work/three-pages/bin:$PATH" \
         GH_FX="$work/three-pages/$1" "$SOLVABLE" 2>"$work/three-pages/$1.err")" && code=0 || code=$?
}
three_page_run one; one_out="$out" one_code="$code"
three_page_run three

{ [[ "$one_code" == 0 && "$one_out" == $'75\n73' ]] \
  && [[ "$code" == "$one_code" && "$out" == "$one_out" ]]; } \
  && ok || no "against a gh that serves issues and PRs over three pages on repos/{owner}/{repo} and refuses repositories/{id} with the proxy's 403, prints the same issue numbers and exit code as against a single-page fixture holding the same issues and PRs (#592) (single page: exit=$one_code stdout='$(tr '\n' '|' <<<"$one_out")' want 0 and '75|73'; three pages: exit=$code stdout='$(tr '\n' '|' <<<"$out")' want the same; three pages stderr='$(tr '\n' '|' < "$work/three-pages/three.err")')"

finish
