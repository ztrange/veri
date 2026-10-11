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
  out="$(cd "$no_claims" && VERI_GH_JSON="$fixture" "$SOLVABLE" "$@" 2>/dev/null)" && code=0 || code=$?
}

label_run() {  # label_run <fixture-dir> <env setting…>; sets $out and $code
  local fixture="$1"; shift
  out="$(cd "$no_claims" && env "$@" VERI_GH_JSON="$fixture" "$SOLVABLE" 2>/dev/null)" && code=0 || code=$?
}

refused_run() {  # refused_run <fixture-dir> <env setting…>; sets $refused_out/$refused_err/$refused_code
  local fixture="$1"; shift
  refused_out="$fixture/refused.out" refused_err="$fixture/refused.err"
  env "$@" VERI_GH_JSON="$fixture" "$SOLVABLE" >"$refused_out" 2>"$refused_err" \
    && refused_code=0 || refused_code=$?
}

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

skill_doc="skills/tdd/SCOPE-LOOP.md"
procedure_doc="skills/tdd/SKILL.md"

loop_bullet() {  # loop_bullet <opening-line regex> <line that ends it>
  awk -v opens="$1" -v ends="$2" '
    $0 ~ opens { keep = 1 }
    $0 ~ ends  { keep = 0 }
    keep
  ' "$REPO_ROOT/$skill_doc"
}


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

shiftdir="$work/shifting-pages"
mkdir -p "$shiftdir/bin"
python3 -c '
import json, sys
issues = [{"number": n, "title": "issue %d" % n, "state": "open", "body": "## Blocked by\n\nNone.\n",
           "labels": [] if n in (1, 130) else [{"name": "ready-for-agent"}]}
          for n in range(1, 131)]
json.dump(issues, open(sys.argv[1], "w"))
' "$shiftdir/issues.json"
cat > "$shiftdir/bin/gh" <<'STUB'
#!/bin/sh
[ "$1" = api ] || { echo "gh stub: unexpected call: gh $*" >&2; exit 1; }
shift
exec python3 -c '
import json, os, sys
from urllib.parse import parse_qs, urlsplit
fixture, closed_file, args = sys.argv[1], sys.argv[2], sys.argv[3:]
paginate = "--paginate" in args
paths = [a for a in args if not a.startswith("-")]
if len(paths) != 1 or len(paths) + paginate != len(args):
    sys.exit("gh stub: unsupported call: gh api %s" % " ".join(args))
url = urlsplit(paths[0])
query = {k: v[-1] for k, v in parse_qs(url.query).items()}
if url.path.endswith("/pulls"):
    sys.stdout.write("[]")
    sys.exit(0)
if not url.path.endswith("/issues"):
    sys.exit("gh stub: unexpected path %s" % paths[0])
size = min(int(query.get("per_page", 30)), 100)
page = int(query.get("page", 1))
def listing():
    closed = open(closed_file).read().split() if os.path.exists(closed_file) else []
    items = json.load(open(fixture))
    for item in items:
        if str(item["number"]) in closed:
            item["state"] = "closed"
    state = query.get("state", "open")
    items = [i for i in items if state == "all" or i["state"] == state]
    return sorted(items, key=lambda i: i["number"], reverse=query.get("direction", "desc") == "desc")
out = []
while True:
    served = listing()[(page - 1) * size:page * size]
    out.append(json.dumps(served))
    if served and not os.path.exists(closed_file):
        open(closed_file, "w").write("%d\n" % served[0]["number"])
    if not paginate or not served:
        break
    page += 1
sys.stdout.write("".join(out))
' "$GH_SHIFT_ISSUES" "$GH_SHIFT_CLOSED" "$@"
STUB
chmod +x "$shiftdir/bin/gh"

out="$(env -u VERI_GH_JSON -u VERI_LABEL -u VERI_PRIORITY_LABEL -u VERI_GH_DRIVER PATH="$shiftdir/bin:$PATH" \
       GH_SHIFT_ISSUES="$shiftdir/issues.json" GH_SHIFT_CLOSED="$shiftdir/closed" \
       "$SOLVABLE" 2>"$shiftdir/stderr")" && code=0 || code=$?
missing="$(comm -23 <(seq 2 129 | sort) <(printf '%s\n' "$out" | sort) | sort -n | tr '\n' ' ')"
extra="$(comm -13 <(seq 2 129 | sort) <(printf '%s\n' "$out" | sort) | sort -n | tr '\n' ' ')"

{ [[ "$code" == 0 && "$out" == "$(seq 2 129)" ]]; } \
  && ok || no "against a fake gh api whose open-only issue listing shifts between calls — the first issue it serves is closed once page 1 has gone out — solvable-issues.sh still prints every solvable issue the fake holds (#1051) (130 open issues, #2–#129 opted in, closed after page 1: #$(cat "$shiftdir/closed" 2>/dev/null | tr -d '\n'); exit=$code want 0; missing='$missing' want ''; unexpected='$extra' want ''; stderr='$(tr '\n' '|' < "$shiftdir/stderr")')"

wide="$work/shifting-pages-per-page"
mkdir -p "$wide/bin"
cat > "$wide/bin/gh" <<'STUB'
#!/bin/sh
printf '%s\n' "$*" >> "$GH_CALLS"
exec "$GH_SHIFT_STUB" "$@"
STUB
chmod +x "$wide/bin/gh"

out="$(env -u VERI_GH_JSON -u VERI_LABEL -u VERI_PRIORITY_LABEL -u VERI_GH_DRIVER PATH="$wide/bin:$PATH" \
       GH_CALLS="$wide/calls" GH_SHIFT_STUB="$shiftdir/bin/gh" \
       GH_SHIFT_ISSUES="$shiftdir/issues.json" GH_SHIFT_CLOSED="$wide/closed" \
       "$SOLVABLE" 2>"$wide/stderr")" && code=0 || code=$?
missing="$(comm -23 <(seq 2 129 | sort) <(printf '%s\n' "$out" | sort) | sort -n | tr '\n' ' ')"

{ [[ "$code" == 0 && "$out" == "$(seq 2 129)" ]] \
  && grep -F 'issues?state=all&sort=created&direction=asc&per_page=100' "$wide/calls" > /dev/null; } \
  && ok || no "against a fake gh api holding more than 100 open issues whose pages shift between calls, solvable-issues.sh reads the grow-only issue listing at per_page=100 and still prints every solvable issue (#1064) (130 open issues, #2–#129 opted in; exit=$code want 0; missing='$missing' want ''; gh calls='$(tr '\n' '|' < "$wide/calls" 2>/dev/null)' want one naming issues?state=all&sort=created&direction=asc&per_page=100; stderr='$(tr '\n' '|' < "$wide/stderr")')"

onepage="$work/open-issues-one-page"
mkdir -p "$onepage/bin"
python3 -c '
import json, sys
def labels(n):
    names = [] if n % 10 == 0 else ["ready-for-agent"]
    names += ["bug"] if n == 7 else ["priority"] if n == 33 else []
    return [{"name": name} for name in names]
def issue(n, labelled):
    return {"number": n, "title": "issue %d" % n, "state": "open", "body": "## Blocked by\n\nNone.\n",
            "labels": labelled}
json.dump([issue(n, labels(n)) for n in range(1, 41)], open(sys.argv[1], "w"))
json.dump([issue(n, [] if n in (1, 100) else [{"name": "ready-for-agent"}]) for n in range(1, 101)],
          open(sys.argv[2], "w"))
' "$onepage/issues.json" "$onepage/issues100.json"
cp "$wide/bin/gh" "$onepage/bin/gh"

out="$(env -u VERI_GH_JSON -u VERI_LABEL -u VERI_PRIORITY_LABEL -u VERI_GH_DRIVER PATH="$onepage/bin:$PATH" \
       GH_CALLS="$onepage/calls" GH_SHIFT_STUB="$shiftdir/bin/gh" \
       GH_SHIFT_ISSUES="$onepage/issues.json" GH_SHIFT_CLOSED="$onepage/closed" \
       "$SOLVABLE" 2>"$onepage/stderr")" && code=0 || code=$?
issue_calls="$(grep -F '/issues?' "$onepage/calls" || true)"
want="$(printf '%s\n' 33 7; seq 1 40 | grep -v -x -e 7 -e 33 -e 10 -e 20 -e 30 -e 40)"

out100="$(env -u VERI_GH_JSON -u VERI_LABEL -u VERI_PRIORITY_LABEL -u VERI_GH_DRIVER PATH="$onepage/bin:$PATH" \
          GH_CALLS="$onepage/calls100" GH_SHIFT_STUB="$shiftdir/bin/gh" \
          GH_SHIFT_ISSUES="$onepage/issues100.json" GH_SHIFT_CLOSED="$onepage/closed100" \
          "$SOLVABLE" 2>"$onepage/stderr100")" && code100=0 || code100=$?

{ [[ "$code" == 0 && "$out" == "$want" ]] \
  && [[ "$(grep -c . <<<"$issue_calls")" == 1 ]] \
  && grep -F 'issues?state=open&per_page=100' <<<"$issue_calls" > /dev/null \
  && [[ "$code100" == 0 && "$out100" == "$(seq 2 99)" ]] \
  && grep -F 'issues?state=all&sort=created&direction=asc&per_page=100' "$onepage/calls100" > /dev/null; } \
  && ok || no "against a fake gh api holding fewer than 100 open issues, solvable-issues.sh makes exactly one issue listing request, issues?state=open&per_page=100, and prints the same output as before; an open issue page of 100 items falls back to the grow-only issue listing (#1064) (40 open issues: exit=$code want 0; stdout='$(tr '\n' '|' <<<"$out")' want '$(tr '\n' '|' <<<"$want")'; issue listing calls='$(tr '\n' '|' <<<"$issue_calls")' want exactly one naming issues?state=open&per_page=100; 100 open issues: exit=$code100 want 0; stdout lines=$(grep -c . <<<"$out100") want #2–#99; gh calls='$(tr '\n' '|' < "$onepage/calls100" 2>/dev/null)' want one naming issues?state=all&sort=created&direction=asc&per_page=100; stderr='$(tr '\n' '|' < "$onepage/stderr")|$(tr '\n' '|' < "$onepage/stderr100")')"


prshift="$work/shifting-pr-pages"
mkdir -p "$prshift/bin"
python3 -c '
import json, sys
issues = [{"number": n, "title": "issue %d" % n, "state": "open", "body": "## Blocked by\n\nNone.\n",
           "labels": [{"name": "ready-for-agent"}]} for n in range(1, 11)]
prs = [{"number": n, "state": "open", "body": "Closes #5" if n == 230 else "Tidies something."}
       for n in range(201, 261)]
json.dump(issues, open(sys.argv[1], "w"))
json.dump(prs, open(sys.argv[2], "w"))
' "$prshift/issues.json" "$prshift/prs.json"
cat > "$prshift/bin/gh" <<'STUB'
#!/bin/sh
[ "$1" = api ] || { echo "gh stub: unexpected call: gh $*" >&2; exit 1; }
shift
exec python3 -c '
import json, os, sys
from urllib.parse import parse_qs, urlsplit
issues_file, prs_file, closed_file, args = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4:]
paginate = "--paginate" in args
paths = [a for a in args if not a.startswith("-")]
if len(paths) != 1 or len(paths) + paginate != len(args):
    sys.exit("gh stub: unsupported call: gh api %s" % " ".join(args))
url = urlsplit(paths[0])
query = {k: v[-1] for k, v in parse_qs(url.query).items()}
if url.path.endswith("/issues"):
    fixture, shifts = issues_file, False
elif url.path.endswith("/pulls"):
    fixture, shifts = prs_file, True
else:
    sys.exit("gh stub: unexpected path %s" % paths[0])
size = min(int(query.get("per_page", 30)), 100)
page = int(query.get("page", 1))
def listing():
    closed = open(closed_file).read().split() if shifts and os.path.exists(closed_file) else []
    items = json.load(open(fixture))
    for item in items:
        if str(item["number"]) in closed:
            item["state"] = "closed"
    state = query.get("state", "open")
    items = [i for i in items if state == "all" or i["state"] == state]
    return sorted(items, key=lambda i: i["number"], reverse=query.get("direction", "desc") == "desc")
out = []
while True:
    served = listing()[(page - 1) * size:page * size]
    out.append(json.dumps(served))
    if shifts and served and not os.path.exists(closed_file):
        open(closed_file, "w").write("%d\n" % served[0]["number"])
    if not paginate or not served:
        break
    page += 1
sys.stdout.write("".join(out))
' "$GH_SHIFT_ISSUES" "$GH_SHIFT_PRS" "$GH_SHIFT_CLOSED" "$@"
STUB
chmod +x "$prshift/bin/gh"

out="$(env -u VERI_GH_JSON -u VERI_LABEL -u VERI_PRIORITY_LABEL -u VERI_GH_DRIVER PATH="$prshift/bin:$PATH" \
       GH_SHIFT_ISSUES="$prshift/issues.json" GH_SHIFT_PRS="$prshift/prs.json" GH_SHIFT_CLOSED="$prshift/closed" \
       "$SOLVABLE" 2>"$prshift/stderr")" && code=0 || code=$?

{ [[ "$code" == 0 && "$out" == "$(printf '%s\n' 1 2 3 4 6 7 8 9 10)" ]]; } \
  && ok || no "against a fake gh api whose open-only PR listing shifts between calls — the first PR it serves is closed once page 1 has gone out — an issue claimed by an open PR on a later page is still left out of solvable-issues.sh's output (#1051) (issues #1–#10 opted in, 60 open PRs #201–#260, #230 says 'Closes #5', closed after page 1: PR #$(cat "$prshift/closed" 2>/dev/null | tr -d '\n'); exit=$code want 0; stdout='$(tr '\n' '|' <<<"$out")' want '1|2|3|4|6|7|8|9|10'; stderr='$(tr '\n' '|' < "$prshift/stderr")')"

widepr="$work/shifting-pr-pages-per-page"
mkdir -p "$widepr/bin"
python3 -c '
import json, sys
prs = [{"number": n, "state": "open", "body": "Closes #5" if n == 320 else "Tidies something."}
       for n in range(201, 331)]
json.dump(prs, open(sys.argv[1], "w"))
' "$widepr/prs.json"
cat > "$widepr/bin/gh" <<'STUB'
#!/bin/sh
printf '%s\n' "$*" >> "$GH_CALLS"
exec "$GH_SHIFT_STUB" "$@"
STUB
chmod +x "$widepr/bin/gh"

out="$(env -u VERI_GH_JSON -u VERI_LABEL -u VERI_PRIORITY_LABEL -u VERI_GH_DRIVER PATH="$widepr/bin:$PATH" \
       GH_CALLS="$widepr/calls" GH_SHIFT_STUB="$prshift/bin/gh" \
       GH_SHIFT_ISSUES="$prshift/issues.json" GH_SHIFT_PRS="$widepr/prs.json" GH_SHIFT_CLOSED="$widepr/closed" \
       "$SOLVABLE" 2>"$widepr/stderr")" && code=0 || code=$?

{ [[ "$code" == 0 && "$out" == "$(printf '%s\n' 1 2 3 4 6 7 8 9 10)" ]] \
  && grep -F 'pulls?state=all&sort=created&direction=asc&per_page=100' "$widepr/calls" > /dev/null; } \
  && ok || no "against a fake gh api holding more than 100 open PRs whose pages shift between calls, solvable-issues.sh reads the grow-only PR listing at per_page=100 and still leaves out every issue an open PR claims (#1064) (issues #1–#10 opted in, 130 open PRs #201–#330, #320 says 'Closes #5'; exit=$code want 0; stdout='$(tr '\n' '|' <<<"$out")' want '1|2|3|4|6|7|8|9|10'; gh calls='$(tr '\n' '|' < "$widepr/calls" 2>/dev/null)' want one naming pulls?state=all&sort=created&direction=asc&per_page=100; stderr='$(tr '\n' '|' < "$widepr/stderr")')"

onepr="$work/open-prs-one-page"
mkdir -p "$onepr/bin"
python3 -c '
import json, sys
def pr(n, claim):
    return {"number": n, "state": "open", "body": "Closes #5" if n == claim else "Tidies something."}
json.dump([pr(n, 230) for n in range(201, 241)], open(sys.argv[1], "w"))
json.dump([pr(n, 250) for n in range(201, 301)], open(sys.argv[2], "w"))
' "$onepr/prs.json" "$onepr/prs100.json"
cp "$widepr/bin/gh" "$onepr/bin/gh"

out="$(env -u VERI_GH_JSON -u VERI_LABEL -u VERI_PRIORITY_LABEL -u VERI_GH_DRIVER PATH="$onepr/bin:$PATH" \
       GH_CALLS="$onepr/calls" GH_SHIFT_STUB="$prshift/bin/gh" \
       GH_SHIFT_ISSUES="$prshift/issues.json" GH_SHIFT_PRS="$onepr/prs.json" GH_SHIFT_CLOSED="$onepr/closed" \
       "$SOLVABLE" 2>"$onepr/stderr")" && code=0 || code=$?
pr_calls="$(grep -F '/pulls?' "$onepr/calls" || true)"

out100="$(env -u VERI_GH_JSON -u VERI_LABEL -u VERI_PRIORITY_LABEL -u VERI_GH_DRIVER PATH="$onepr/bin:$PATH" \
          GH_CALLS="$onepr/calls100" GH_SHIFT_STUB="$prshift/bin/gh" \
          GH_SHIFT_ISSUES="$prshift/issues.json" GH_SHIFT_PRS="$onepr/prs100.json" GH_SHIFT_CLOSED="$onepr/closed100" \
          "$SOLVABLE" 2>"$onepr/stderr100")" && code100=0 || code100=$?

{ [[ "$code" == 0 && "$out" == "$(printf '%s\n' 1 2 3 4 6 7 8 9 10)" ]] \
  && [[ "$(grep -c . <<<"$pr_calls")" == 1 ]] \
  && grep -F 'pulls?state=open&per_page=100' <<<"$pr_calls" > /dev/null \
  && [[ "$code100" == 0 && "$out100" == "$(printf '%s\n' 1 2 3 4 6 7 8 9 10)" ]] \
  && grep -F 'pulls?state=all&sort=created&direction=asc&per_page=100' "$onepr/calls100" > /dev/null; } \
  && ok || no "against a fake gh api holding fewer than 100 open PRs, solvable-issues.sh makes exactly one PR listing request, pulls?state=open&per_page=100, and prints the same output as before; an open PR page of 100 items falls back to the grow-only PR listing (#1064) (issues #1–#10 opted in; 40 open PRs, #230 says 'Closes #5': exit=$code want 0; stdout='$(tr '\n' '|' <<<"$out")' want '1|2|3|4|6|7|8|9|10'; PR listing calls='$(tr '\n' '|' <<<"$pr_calls")' want exactly one naming pulls?state=open&per_page=100; 100 open PRs, #250 says 'Closes #5': exit=$code100 want 0; stdout='$(tr '\n' '|' <<<"$out100")' want '1|2|3|4|6|7|8|9|10'; gh calls='$(tr '\n' '|' < "$onepr/calls100" 2>/dev/null)' want one naming pulls?state=all&sort=created&direction=asc&per_page=100; stderr='$(tr '\n' '|' < "$onepr/stderr")|$(tr '\n' '|' < "$onepr/stderr100")')"

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
case "$path" in
  *state=open*) sed -n 's/^\[\(.*\)\]$/\1/p' "$GH_FX/$list"-*.json | paste -sd, - | sed 's/.*/[&]/'; exit 0 ;;
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

name="a live conductor lock under the surrounding repository's .tdd/wt/<n>/.tdd/conductor.pid, for unrelated numbers and for every number this suite's fixtures name, leaves run's and label_run's answer unchanged"
unrelated_numbers=(108 117 120 124)
fixture_numbers=($(sed -n 's/.*"number"[[:space:]]*:[[:space:]]*\([0-9][0-9]*\).*/\1/p' "$HERE/solvable-issues.test.sh" | sort -un))
fx="$(fixture surrounding-locks)"
{
  printf '['; sep=
  for n in $(printf '%s\n' "${unrelated_numbers[@]}" "${fixture_numbers[@]}" | sort -un); do
    printf '%s{"number": %s, "title": "t", "labels": [{"name": "ready-for-agent"}], "state": "OPEN", "body": "## Blocked by\\n\\nNone.\\n"}' "$sep" "$n"
    sep=,
  done
  printf ']\n'
} > "$fx/issues.json"

surrounding_repo() {  # surrounding_repo <dir> <n…>
  local dir="$1" n; shift
  new_repo -b main "$dir" >/dev/null 2>&1
  for n in "$@"; do
    mkdir -p "$dir/.tdd/wt/$n/.tdd"
    printf '%s\n' "$$" > "$dir/.tdd/wt/$n/.tdd/conductor.pid"
  done
}
surrounding_repo "$work/surrounding-unrelated" "${unrelated_numbers[@]}"
surrounding_repo "$work/surrounding-every" "${fixture_numbers[@]+"${fixture_numbers[@]}"}"

same_answer() {  # same_answer <what> <want-code> <want-out>; appends to $problems unless $code and $out match
  [[ "$code" == "$2" && "$out" == "$3" ]] ||
    problems+=("$1: want exit $2 and stdout '$(tr '\n' '|' <<<"$3")', got exit $code and stdout '$(tr '\n' '|' <<<"$out")'")
}

problems=()
run "$fx"; no_lock_out="$out" no_lock_code="$code"
label_run "$fx" -u VERI_PRIORITY_LABEL; no_lock_label_out="$out" no_lock_label_code="$code"
[[ "$no_lock_code" == 0 && -n "$no_lock_out" ]] ||
  problems+=("the run with no lock is not green, so there is nothing to compare against: exit $no_lock_code, stdout: $(tr '\n' '|' <<<"$no_lock_out")")
[[ "${#fixture_numbers[@]}" -gt 0 ]] ||
  problems+=("no \"number\": <n> fixture was found in solvable-issues.test.sh, so no lock was written and the arms cannot differ")
for surrounding in surrounding-unrelated surrounding-every; do
  cd "$work/$surrounding" || exit 2
  run "$fx"
  same_answer "run under $surrounding" "$no_lock_code" "$no_lock_out"
  label_run "$fx" -u VERI_PRIORITY_LABEL
  same_answer "label_run under $surrounding" "$no_lock_label_code" "$no_lock_label_out"
  cd "$no_claims" || exit 2
done
report "$name"

finish
