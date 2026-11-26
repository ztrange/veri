"""The step helpers the fused halves of a step share (PRD 027.4-027.6), above what `fused` holds: their inputs, the
step they take, the step's cost check and whether the run switched a phase's verifier off."""
import os
import re
import sys
from decimal import Decimal, InvalidOperation

import event
import event_log
import ledger
import run_dir
import run_pins
import run_start
from fused import Stop, call, checked, label, read_settled, script
from ledger import ledger_steps
from next_pending_refactor import refactor_pending


def inputs(name, n, *files):
    """(settled preflight values, worktree) when the preflight file and each of <files> (paths under the worktree,
    `%s` standing for the issue) exist; else None, each missing one named on stderr (FC15)."""
    try:
        settled = read_settled(run_start.preflight_file(n))
    except OSError:
        sys.stderr.write("%s: no .tdd/issue-%s-preflight: run preflight.sh first\n" % (name, n))
        return None
    wt = settled.get("worktree", "")
    missing = [f % n for f in files if not os.path.exists(os.path.join(wt, f % n))]
    for path in missing:
        sys.stderr.write("%s: no %s\n" % (name, path))
    return None if missing else (settled, wt)


def first_step(wt, n, chosen):
    """The text of the first ledger record <chosen> takes, as next-unchecked.sh and next-pending-refactor.sh print
    it, the ledger read through ledger.read_ledger as they read it (a NUL dropped, a lone carriage return kept); None
    for none."""
    return next((r.text for r in ledger_steps(ledger.read_ledger(run_dir.ledger(wt, n))) if chosen(r)), None)



def open_step(wt, n):
    """The step a run works on now, as run-step.sh takes it: the refactor-pending step, else the first unchecked one;
    None for none."""
    return first_step(wt, n, refactor_pending) or first_step(wt, n, ledger.handed_out)

def green_tick(where, wt, n, rev):
    """The newest ledger commit reachable from <rev> that changes a ledger line: the green tick of the step a refactor
    follows (#4510). None when no commit does."""
    log = checked(where, "git", "log", "--format=%x00%H", "-p", "--unified=0", rev, "--", run_dir.ledger("", n),
                  cwd=wt)
    for entry in log.split("\0")[1:]:
        sha, _, patch = entry.partition("\n")
        changed = [line for line in patch.splitlines() if line.startswith(("+", "-"))
                   and not line.startswith(("+++ ", "--- "))]
        if changed:
            return sha.strip()
    return None


def cost_check(wt, step):
    """*The step's cost check* after a leaf's wait (RH4): step-cost.sh exit 3 goes on and 2 stops; a figure over the
    first line step-budget.sh prints stops with exit 1 at `cost-check`, unless the journal already holds the step's
    step-over-budget event (the check fires once per step)."""
    code, out, _ = call(script("step-cost.sh"), step, cwd=wt)
    if code == 3:
        return
    if code != 0:
        raise Stop("cost-check", label("step-cost.sh", step) + " exit %d" % code, code)
    if any(e.get("step") == step for e in event_log.events(wt, "step-over-budget", skip_unreadable=True)):
        return
    budget = (checked("cost-check", script("step-budget.sh"), cwd=wt).splitlines() or [""])[0].strip()
    try:
        over = Decimal(out.strip()) > Decimal(budget)
    except InvalidOperation:
        raise Stop("cost-check", "spent %s budget %s unreadable" % (out.strip(), budget), 2) from None
    if over:
        raise Stop("cost-check", "spent %s over the step budget %s" % (out.strip(), budget), 1)


def verify_switched_off(wt, n, phase):
    """True when the run's pinned VERI_SKIP_VERIFY (.tdd/issue-<n>-skip-verify) names <phase> (ADR-0033)."""
    return phase in (run_pins.skip_verify(n, wt) or "").replace(",", " ").split()


def summary(step):
    """The step's ledger text without its trailing markers, read as data (the #431/#437 rule)."""
    text = ledger.body(step)
    return text[:len(text) - len(ledger.trailing_markers(text))].rstrip()


def red_test_id(test_path, target):
    """The Red case's id: <target> when it names its file (`::`), else <test_path>::<target>."""
    return target if "::" in target else test_path + "::" + target


def verdict(wt):
    """(hash, flags) of `.tdd/verify-refactor.log` as it now stands, from one read: its sha256, or `none` without one,
    which verify-refactor verdict a refactor-half record was settled after; and the `uncovered-spec` FLAGS of that
    verdict, each as refactor-half.sh writes its `uncovered_spec=` value, none without the log. Every record that names
    `verdict_log=` takes both from here, so a record never names a verdict without that verdict's flags (#4029): a
    refactor-half record (a skipped verify's leaves the flags out), seam-settle.sh's after a hand refactor, and
    step-close's rewrite of a record settled after another verdict."""
    import hashlib

    import extract_result
    from report import report_values
    try:
        with open(os.path.join(wt, ".tdd", "verify-refactor.log"), "rb") as f:
            raw = f.read()
    except FileNotFoundError:
        return "none", []
    flags = report_values(extract_result.extract(raw.decode("utf-8", errors="replace")), "FLAGS", splitlines=True,
                          strip=True)
    return (hashlib.sha256(raw).hexdigest(),
            [detail(line) for line in flags if kind(line) == "uncovered-spec"])


def kind(line):
    """A FLAGS: or CANDIDATES: value's class: its first word, before ` |` or `:`."""
    return re.split(r"\s*[|:]", line.strip(), maxsplit=1)[0].strip()


def detail(line, last=False):
    """What a flag or candidate names after its class: the text after the first `|` (the last with <last>)."""
    parts = re.split(r"\s*\|\s*", line.strip())
    return (parts[-1] if last else " | ".join(parts[1:])) if len(parts) > 1 else line.split(":", 1)[-1].strip()


def refresh(stage, wt, n, record, facts):
    """Records are caches (PRD 038.1 SC1, SC2): rewrite `.tdd/issue-<n>-<record>` so each key of <facts> holds the value
    its committed source gave, the key's first line replaced, or one added, each rewrite one `record-refreshed` event of
    <stage>; a record that already agrees is not written. A refused event stops it with exit 2."""
    path = os.path.join(wt, ".tdd", "issue-%s-%s" % (n, record))
    with open(path, encoding="utf-8", errors="surrogateescape") as f:
        lines = f.read().splitlines()
    changed = False
    for key, value in facts.items():
        at = next((i for i, line in enumerate(lines) if line.split("=", 1)[0] == key), None)
        if at is not None and lines[at] == key + "=" + value:
            continue
        old = lines[at].split("=", 1)[1] if at is not None else ""
        if at is None:
            lines.append(key + "=" + value)
        else:
            lines[at] = key + "=" + value
        changed = True
        if event.mark(wt, {"issue": n, "actor": "conductor", "step": facts.get("step", "")}, "record-refreshed",
                      ["stage=" + stage, "key=" + key, "old=" + old, "new=" + value]):
            raise Stop(stage, "record-refreshed event refused", 2)
    if changed:
        with open(path, "w", encoding="utf-8", errors="surrogateescape") as f:
            f.write("".join(line + "\n" for line in lines))


def gain(stage, wt, n, record, key, values, step):
    """Records are caches for a key a record may hold more than once (PRD 038.1 SC1, #4029): add one `<key>=<value>`
    line to `.tdd/issue-<n>-<record>` for each of <values> it lacks, each one `record-refreshed` event of <stage> with
    an empty old value; a record that already holds them all is not written. A refused event stops it with exit 2."""
    path = os.path.join(wt, ".tdd", "issue-%s-%s" % (n, record))
    with open(path, encoding="utf-8", errors="surrogateescape") as f:
        lines = f.read().splitlines()
    added = [value for value in dict.fromkeys(values) if key + "=" + value not in lines]
    for value in added:
        if event.mark(wt, {"issue": n, "actor": "conductor", "step": step}, "record-refreshed",
                      ["stage=" + stage, "key=" + key, "old=", "new=" + value]):
            raise Stop(stage, "record-refreshed event refused", 2)
    if added:
        with open(path, "w", encoding="utf-8", errors="surrogateescape") as f:
            f.write("".join(line + "\n" for line in lines + [key + "=" + value for value in added]))


def read_by(stage, wt, n, step):
    """The first stage of seam_contract.READS[<stage>] whose record names <step> by ledger.same_step, or None; a record
    that exists but cannot be read raises OSError."""
    import seam_contract
    for writer in seam_contract.READS[stage]:
        try:
            values = read_settled(os.path.join(wt, ".tdd", "issue-%s-%s" % (n, writer)))
        except FileNotFoundError:
            continue
        if ledger.same_step(values.get("step", ""), step):
            return writer
    return None


def record(stage, wt, n, step, facts=()):
    """The {key: value} of the record <stage> reads (read_by), its step and each of <facts> (key, value) refreshed from
    their committed sources; None, the seam line naming the first stage it reads printed, when no record it reads
    names <step> (PRD 038.1 SC3, SC4, SC8). A record that exists but cannot be read raises OSError."""
    import seam_contract
    writer = read_by(stage, wt, n, step)
    if writer is None:
        owed = seam_contract.READS[stage][0]
        sys.stdout.write("seam=%s code=1 reason=record next=seam-settle.sh %s %s%s\n" % (
            stage, n, owed, "".join(" %s=…" % key for key in seam_contract.CONTRACTS[owed])))
        return None
    path = os.path.join(wt, ".tdd", "issue-%s-%s" % (n, writer))
    refresh(stage, wt, n, writer, dict((("step", step),) + tuple(facts)))
    return read_settled(path)


def rejected(wt, n, stage, step):
    """(at, values) of <stage>'s rejected record (fused.wait's, PRD 038.9) when it names <step> by ledger.same_step;
    else None. Records are caches (S1): one naming another step, or none, is a REJECT a stopped revise left behind,
    and is removed."""
    import contextlib
    import json

    import fused
    path = fused.wait_record(wt, n, stage + "-rejected")
    try:
        with open(path) as f:
            theirs = json.load(f).get("step")
    except (OSError, ValueError, AttributeError):
        theirs = None
    if theirs is None or not ledger.same_step(theirs, step):
        with contextlib.suppress(FileNotFoundError):
            os.remove(path)
        return None
    return fused.load_wait(wt, n, stage + "-rejected")


def branch_base(where, wt, n):
    """The run's branch base as the conductor recorded it in the main working tree above <wt> (run_pins), handed to
    each verifier as `--branch-base`; a record missing or unreadable stops <where> with exit 2 naming it (#4375)."""
    try:
        main = run_dir.main_tree_from_files(wt)
        return run_pins.branch_base(n, main)
    except OSError:
        raise Stop(where, "branch-base record of issue %s" % n, 2) from None
