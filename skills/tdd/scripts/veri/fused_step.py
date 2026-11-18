"""The step helpers the fused halves of a step share (PRD 027.4-027.6), above what `fused` holds: their inputs, the
step they take, the step's cost check and whether the run switched a phase's verifier off."""
import os
import sys
from decimal import Decimal, InvalidOperation

import event
import event_log
import run_dir
import run_pins
import run_start
from fused import Stop, call, checked, label, read_settled, script
import ledger
from ledger import ledger_steps


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
        raise Stop("cost-check", "spent %s budget %s unreadable" % (out.strip(), budget), 2)
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


def verdict_log(wt):
    """The sha256 of `.tdd/verify-refactor.log` as it now stands, or `none` without one: which verify-refactor verdict
    a refactor-half file was settled after, so step-close can refuse one a later verdict has superseded."""
    import hashlib
    try:
        with open(os.path.join(wt, ".tdd", "verify-refactor.log"), "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except FileNotFoundError:
        return "none"


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


def record(stage, wt, n, step, facts=()):
    """The {key: value} of the record <stage> reads (seam_contract.READS), its step and each of <facts> (key, value)
    refreshed from their committed sources; None, the seam line printed, when the record is missing or names another
    step than <step> by ledger.same_step (PRD 038.1 SC3, SC4). A record that exists but cannot be read raises OSError."""
    import seam_contract
    writer = seam_contract.READS[stage]
    path = os.path.join(wt, ".tdd", "issue-%s-%s" % (n, writer))
    try:
        values = read_settled(path)
    except FileNotFoundError:
        values = None
    if values is None or not ledger.same_step(values.get("step", ""), step):
        sys.stdout.write("seam=%s code=1 reason=record next=seam-settle.sh %s %s%s\n" % (
            stage, n, writer, "".join(" %s=…" % key for key in seam_contract.CONTRACTS[writer])))
        return None
    refresh(stage, wt, n, writer, dict((("step", step),) + tuple(facts)))
    return read_settled(path)
