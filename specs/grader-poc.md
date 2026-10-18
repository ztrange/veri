# Grader proof of concept, 2026-10-17

The question: can an agent grade prose against a requirements list reliably enough to replace
the substring suites? Answered before PRD 011 builds anything, so the stability slice cannot
fail mid-PRD.

## Setup

- **Units** (from `origin/main` a6da749):
  - `prompts/develop-red.md` (7.3 kB)
  - `prompts/verify-refactor.md` (3.9 kB)
  - SKILL.md *Bailing* (8.6 kB)
- **Lists:** 11–13 requirements per unit, below.
- **Variants per unit:**
  - **original**, graded 3 times;
  - **violating**, graded 3 times: two requirements contradicted by a reworded passage, not a deleted one;
  - **harmless**, graded 2 times: two passages reworded with the same meaning. A substring suite would go red on these.
- **Grader:** `claude -p --model claude-sonnet-5-5 --setting-sources "" --tools ""`, with the system prompt below. No tools; the prose arrives in the prompt.

## Results

| Pass | Contract | Originals PASS | Harmless PASS | Violations REJECTed, planted IDs named | Bad outputs | Cost (24 calls) |
|---|---|---|---|---|---|---|
| 1 | one line per ID, then VERDICT | 8/9 | 6/6 | 6/6 runs, 12/12 IDs* | 1: VERDICT PASS beside a FAIL line | $0.40 |
| 2 | same, IDs verbatim, DR13 reworded | 7/9 | 6/6 | 9/9 runs, 17/18 IDs | 2: FAIL lines "corrected" mid-answer | $0.48 |
| 3 | reason first, final `BEGIN/END GRADES` block, strict parser | **9/9** | **6/6** | **9/9 runs, 18/18 IDs, no extra IDs** | **0** | $0.70 |

\* In pass 1, the two misses in the originals were DR13 (2 of 3 runs). DR13 said the report
"ends with" the keys, but a `REPORT-FORMAT` line follows them in the prose, so the grader was
right: the requirement was wrong. That is the ambiguity S2 is meant to catch, caught on the
first try.

- **Per grading (pass 3):** $0.012–0.037, 11 s on average.
- **Projection for a full regrade of veri's prose:** SKILL.md (214 kB) cut into ~30 section units is ≈ $1.
- **Whole PoC:** $1.57 over 72 calls.

## Verdict: go, with G5/G5a as amended

The judgement held from the first pass. Every instability came from the output contract
(unclear IDs, no room to reason, a self-reported verdict), and pass 3's contract removed all of
it.

## What this did not test

- **Sample size:** 3 units, one model (Sonnet 5.5).
- **Subtlety of the violations:** the planted ones were clear contradictions. Subtle drift, such
  as a weakened qualifier or a dropped exception, is untested.
- **Bias in the lists:** I wrote them while reading the prose, which biases them towards PASS.
  The violating variants check sensitivity, not completeness.
- **Ambient context:** whether user-level context reached the grader was not checked.

Slice 2 repeats S1 on its own runner, adding one subtle-drift variant per unit.

## Grader system prompt (pass 3)

```
You grade a piece of prose against a list of requirements. You judge only what the prose states or instructs, read as its reader (an AI agent following it) would read it. You do not judge whether the instructions are wise, and you do not judge behaviour.

Rules:
- `{{NAME}}` and `{{INCLUDE:...}}` are template slots filled in later. Never fail a requirement because of a slot; judge the literal text around it.
- A requirement PASSES when the prose clearly states or instructs it, in any wording. It FAILS when the prose omits it, contradicts it, or states something that would lead the reader to act against it.
- Judge each requirement independently.

First, analyse each requirement against the prose in free text — quote the prose you rely on. Change your mind here if you need to.

Then end your reply with this block and nothing after it. Inside the block, one line per requirement, in the order given, starting with the requirement's ID exactly as written in the list (e.g. `DR4`), and no corrections:
BEGIN GRADES
<ID>: PASS — <reason, at most 20 words>
<ID>: FAIL — <reason, at most 20 words, quoting the failing prose when it exists>
VERDICT: PASS or VERDICT: REJECT
END GRADES
VERDICT is PASS only if every line inside the block is PASS.
```

## Parser (pass 3)

```python
import json,sys,re
# parse.py <run.json> <req-file> -> prints "PASS|REJECT|NOVERDICT <fails>"; strict
res=json.load(open(sys.argv[1]))['result']
ids=[l.split('|')[0].strip() for l in open(sys.argv[2]) if l.strip()]
m=re.findall(r'BEGIN GRADES\n(.*?)\nEND GRADES', res, re.S)
if len(m)!=1 or not res.rstrip().endswith('END GRADES'): print('NOVERDICT block'); sys.exit(2)
lines=m[0].strip().split('\n')
grades=[re.match(r'^([A-Z]+[0-9]+): (PASS|FAIL) — ',l) for l in lines[:-1]]
if any(g is None for g in grades) or [g[1] for g in grades]!=ids: print('NOVERDICT lines'); sys.exit(2)
v=re.fullmatch(r'VERDICT: (PASS|REJECT)',lines[-1].strip())
fails=[g[1] for g in grades if g[2]=='FAIL']
derived='REJECT' if fails else 'PASS'
if not v or v[1]!=derived: print('NOVERDICT mismatch'); sys.exit(2)
print(derived,' '.join(fails)); sys.exit(0 if derived=='PASS' else 1)
```

## Requirement lists

### develop-red

| ID | Requirement |
|---|---|
| DR1 | The leaf pins only the one step it is given, as observable behaviour rather than internal structure. |
| DR2 | A valid test asserts outputs, exit codes, written files or events, or named errors — never a process count, a fork count, or a timing across a suite run. |
| DR3 | A call count may be asserted only when the criterion itself names it, and then only through an in-process spy on one function, never a PATH shim counting real processes. |
| DR4 | Costly dependencies (network, a git remote, the claude binary, a real sleep, a server) are replaced by stubs or fakes unless the behaviour under test is that dependency's real use. |
| DR5 | A test never runs another test suite, and never re-runs the suite it lives in. |
| DR6 | When the criterion can only be pinned by a test that breaks the lightweight, behaviour or self-contained rules, the leaf writes no test and reports AGAINST_UNMODIFIED: UNTESTABLE with a WHY naming the rule. |
| DR7 | A helper only the test uses is defined in the test file during Red, and a failure caused only by an undefined name in the test file does not count as a red. |
| DR8 | The leaf writes its failure prediction to .tdd/red-prediction.md before running any suite. |
| DR9 | The leaf runs the affected suites — not the full suite and not one picked by hand — against the unmodified production code. |
| DR10 | When the observed failure diverges from the prediction, the leaf revises the test and never adjusts the prediction to fit the output. |
| DR11 | When the case passes against unmodified code, the leaf shows it can fail by temporarily breaking the behaviour, compares the output to a prediction before restoring, and verifies the restore with git diff --exit-code. |
| DR12 | The leaf changes no file other than the test file. |
| DR13 | The report, at the end of the output, carries the keys TEST_PATH, TARGET_TEST, AGAINST_UNMODIFIED (FAILS, PASSES or UNTESTABLE), WHY, FAIL_OUTPUT, PREDICTED_FAILURE, PREDICTION (MATCHED or DIVERGED) and PREDICTION_NOTE. |

### verify-refactor

| ID | Requirement |
|---|---|
| VR1 | The verifier reviews the refactor through git diff from the base sha to HEAD, and does not read the range's commit messages. |
| VR2 | The verifier runs the fast command and the affected suites itself; both must be green, and a refactor that changed observable behaviour or broke a test is a REJECT. |
| VR3 | The settled code must follow the repository's conventions, name things clearly and be reasonably robust, and must not add untested generality. |
| VR4 | An unhandled edge case is reported on a FLAGS line carrying its class (overfit, uncovered-spec or beyond-spec), not as a REJECT. |
| VR5 | FLAGS lines come before the final VERDICT/REASON pair, one finding per line. |
| VR6 | A removed or weakened test assertion in the range is a REJECT that names the assertion. |
| VR7 | A purely cosmetic hunk is named in REASON but is not by itself a REJECT. |
| VR8 | An empty range is not by itself a REJECT. |
| VR9 | A shortfall against a criterion outside the step under judgement is named in REASON as out of scope and is not by itself a REJECT. |
| VR10 | A changed file outside the cycle's files (those git diff --name-only base^ base names) is a REJECT, unless its hunk removes duplication between that file and code in the list. |
| VR11 | The verifier renders one verdict: PASS when green and up to standard, otherwise REJECT naming the specific weakness. |

### bailing

| ID | Requirement |
|---|---|
| BL1 | Every bail carries a cause token, and its classification comes from classify-bail.sh, never chosen ad hoc. |
| BL2 | killed-stuck and no-verdict classify as system failures; revise-exhausted and untestable-criterion classify as process failures. |
| BL3 | A bail reached first stays a bail even when a stop is pending; only a pending `now` stop turns a leaf's exit 2 into a stop. |
| BL4 | The attempt's tree is preserved with preserve-attempt.sh before any reset, and a failed snapshot does not prevent the bail. |
| BL5 | Only the half-done step is reverted (git reset --hard HEAD); every completed step's commit and checked ledger step is kept. |
| BL6 | A bail event carrying the cause and the classification is logged before the bail comment is rendered. |
| BL7 | Metrics are rendered and committed before the branch is pushed. |
| BL8 | The branch is pushed, best-effort, so completed steps and logs are recoverable. |
| BL9 | The issue gets a "### ⛔ Bailed — <phase> (<classification> failure)" comment carrying the metrics block or its fallback line, the last reason, the skill-drift block, and a pointer to the progress log. |
| BL10 | The draft PR stays open and stays a draft, and receives the bail comment or a link to it. |
| BL11 | The report to the user names the phase, classification, reason, skill-drift block, branch and worktree path, and the worktree is left in place. |
