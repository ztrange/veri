"""tests-frozen.sh's record and check, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import collections
import hashlib
import os
import re
import sys

import case_history
import case_identity
import ledger
import renamed_case
import replaces_case
import run_dir
import tunables
import entry
from frozen_record import (body_digest, body_line, body_record, helper_records,
                           record_path, remove_pass_marker, work_tree_hash,
                           write_pass_marker)
import event
import frozen_record
from ledger import ITEM_RE, KIND_RE, carries_mark, trailing_markers
from case_reader import UnclosedCase, cut_cases, old_cut_cases_all, is_js_test_file, is_test_path

USAGE = ("usage: tests-frozen.sh record <record-file>|--step <step-text> [--red-case <red-test-id>] <test-file>... | "
         "check <record-file>|--step <step-text> | "
         "check-earlier <ledger> --step <step-text> [--except <case>]... | "
         "rerecord-earlier <ledger> --step <step-text> | "
         "rerecord-refactored <ledger> <green-sha> | "
         "rerecord-rebased <ledger> <pre-rebase-sha> | path <step-text>")
REPAIR_MARKS = ("suite-repair", "ci-repair", "fixture-repair")


def _digest(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def _toplevel():
    return case_history.toplevel()


def _has_head():
    return case_history.has_rev("HEAD")


def _enter_root(record, files):
    root = _toplevel()
    record = os.path.abspath(record)
    files = [os.path.relpath(os.path.realpath(name), os.path.realpath(root)) for name in files]
    os.chdir(root)
    return record, files


def _refused_outside_repository():
    if _toplevel() is not None:
        return False
    write(sys.stderr, "tests-frozen.sh: not inside a git repository")
    return True


def differing_tests():
    return case_history.changed_test_files()


_FIXTURE_FILE = re.compile(r"repairs the fixture '[^']*' in (\S+?),")


def _guard_subjects(step):
    return re.findall(r"⟦guard-subject: ([^⟧]+)⟧", trailing_markers(step))


def _accepted_per_digest(digests, nows, olds):
    """Each recorded digest's accepted bodies: the n-th digest for a name against that name's n-th case.

    Same-named twins are matched by order, never through a dict, whose last twin would hide the others.
    When the counts differ (a step recorded only the twin it edited), a digest is accepted against any twin."""
    def accepted(*bodies):
        return {body_digest(body) for body in bodies if body is not None}
    if len(digests) == len(nows):
        return [accepted(now, olds[i] if i < len(olds) else None) for i, now in enumerate(nows)]
    return [accepted(*nows, *olds)] * len(digests)


def _head_cases_all(name):
    return cut_cases(case_history.text_at("HEAD", name, quiet=True))


def _head_and_new_cases(name):
    with open(name, encoding="utf-8", errors="replace") as handle:
        new = handle.read()
    return case_history.cases_at("HEAD", name), cut_cases(new)


def _added_cases(name):
    before, new = _head_and_new_cases(name)
    names = [case for case, _ in new]
    if len(set(names)) == len(names):
        return [(case, body) for case, body in new if before.get(case) != body]
    held = {}
    for case, body in _head_cases_all(name):
        held.setdefault(case, set()).add(body)
    return [(case, body) for case, body in new if body not in held.get(case, ())]


def _recorded_digests(record, name):
    try:
        with open(record, encoding="utf-8") as handle:
            return {r[1]: r[2] for r in map(body_record, handle.read().splitlines()) if r and r[0] == name}
    except OSError:
        return {}


def _issue():
    """The issue whose ledger holds the step: VERI_ISSUE, else the number of a `tdd/<n>-…` branch."""
    issue = tunables.read("VERI_ISSUE")
    if issue:
        return issue
    branch = case_history.current_branch()
    found = re.match(r"tdd/(\d+)-", branch)
    return found.group(1) if found else ""


def _step_commits(step):
    """The commits that are `step`'s own (case_history.step_commits) in the issue VERI_ISSUE or the branch names."""
    return case_history.step_commits(step, _issue())


def _introduced_by(name, own):
    """The cases of `name` that the commits `own` introduced: in the file at the last of them that touched it,
    absent at the revision just before the first of them."""
    revs = case_history.revisions(name)
    mine = [at for at, rev in enumerate(revs) if rev in own]
    if not mine:
        return set()
    before = case_history.cases_at(revs[mine[-1] + 1], name) if mine[-1] + 1 < len(revs) else {}
    return set(case_history.cases_at(revs[mine[0]], name)) - set(before)


def _kept_cases(record, name, step=None, skip=()):
    """The recorded cases of `name` that HEAD still has, each recorded case gone from it replaced by its renamed
    successor, plus every other committed case whose first commit is one of `step`'s own. A case a later step
    added to the file is in no record of this step and in none of its commits, so it is never kept."""
    held = _recorded_digests(record, name)
    with open(name, encoding="utf-8", errors="replace") as handle:
        text = handle.read()
    new = cut_cases(text)
    names = {case for case, _ in new}
    owned = names & set(held)
    consumed = set(owned)
    for case, digest in held.items():
        if case not in names:
            other = case_identity.renamed_to(name, case, digest, text, consumed)
            if other and other in names:
                owned.add(other)
    extra = [case for case in names - owned - set(skip)] if held and step else []
    if extra:
        owned |= set(extra) & _introduced_by(name, _step_commits(step))
    return [(case, body) for case, body in new if case in owned]


def _recorded_cases_intact(record, name):
    with open(record, encoding="utf-8") as handle:
        held = [r for r in map(body_record, handle.read().splitlines()) if r and r[0] == name]
    with open(name, encoding="utf-8", errors="replace") as handle:
        now = cut_cases(handle.read())
    return bool(held) and all(digest in {body_digest(body) for c, body in now if c == case} for _, case, digest in held)


def _earlier_records(lines, step, strict=False):
    for line in lines:
        match = ledger.ITEM_RE.match(line)
        if not match or match.group(1) == " " or match.group(2) == step:
            continue
        path = record_path(match.group(2))
        if not os.path.exists(path):
            path = record_path(match.group(2).removesuffix(ledger.PENDING_MARK))
        try:
            with open(path, encoding="utf-8") as handle:
                records = handle.read().splitlines()
        except FileNotFoundError:
            continue
        except OSError:
            if strict:
                raise
            continue
        yield match.group(2), path, records


def _helpers_stale(releg, name, case, recorded, text, body):
    current = case_identity.helper_digest(text, body)
    if recorded == current:
        return False
    if recorded != case_identity.helper_digest(text, body, legacy=True):
        return True
    releg[(name, case)] = current
    return False


def _parse_replaces(step):
    return replaces_case.parse(step) if replaces_case.is_replaces_case_step(step) else None


def _check_earlier(ledger, step, exempt=(), sanctioned=()):
    root = _toplevel()
    if root is None:
        remove_pass_marker(step)
        write(sys.stderr, "tests-frozen.sh: not inside a git repository\n%s" % USAGE)
        return 2
    given = os.path.realpath(ledger)
    try:
        with open(ledger, encoding="utf-8") as handle:
            lines = handle.read().splitlines()
    except OSError as error:
        os.chdir(root)
        remove_pass_marker(step)
        write(sys.stderr, "tests-frozen.sh: %s\n%s" % (error, USAGE))
        return 2
    os.chdir(root)
    issue = _issue()
    run_ledger = run_dir.ledger("", issue)
    if issue and given != os.path.realpath(run_ledger):
        remove_pass_marker(step)
        write(sys.stderr, "tests-frozen.sh: %s is not the run's ledger %s" % (ledger, run_ledger))
        return 2
    parsed = _parse_replaces(step)
    exempt = list(exempt) + (parsed[0] if parsed else [])
    fixture = _FIXTURE_FILE.search(step) if carries_mark(trailing_markers(step), "fixture-repair") else None
    latest = {}
    helper_digests = {}
    for owner, _, records in _earlier_records(lines, step):
        helper_digests.update(helper_records(records))
        bodies = [r for r in map(body_record, records) if r]
        marked = frozen_record.is_marked(records)
        for name, case, digest in bodies:
            held = latest.get((name, case))
            latest[(name, case)] = (held[0] + [digest] if held and held[1] == owner else [digest], owner, marked)
    changed = []
    consumed = set()
    releg = {}
    for (name, case), (digests, owner, marked) in latest.items():
        try:
            moved = case_identity.moved_path(name, case, digests)
            with open(moved, encoding="utf-8", errors="replace") as handle:
                text = handle.read()
            nows = case_identity.bodies_of(text, case)
            olds = [body for c, body in old_cut_cases_all(text, marked) if c == case]
            if moved != name:
                nows = [case_identity.as_recorded(b, digests) for b in nows]
                olds = [case_identity.as_recorded(b, digests) for b in olds]
            digest = digests[-1]
            if not nows:
                other = case_identity.renamed_to(name, case, digest, text, consumed)
                if other:
                    nows = olds = [dict(cut_cases(text))[other].replace(other, case, 1)]
                elif not any(case in case_history.cases_at(rev, name) for rev in case_history.revisions(name)):
                    write(sys.stderr, "tests-frozen.sh: %s (%s, %s) is in no revision of this branch: skipped"
                          % (case, owner, record_path(owner)))
                    continue
        except OSError:
            nows = olds = []
        except UnclosedCase as error:
            remove_pass_marker(step)
            write(sys.stderr, "tests-frozen.sh: %s: %s" % (name, error))
            return 2
        accepted = _accepted_per_digest(digests, nows, olds) if nows else []
        if case not in exempt and (name, case) not in sanctioned and not (fixture and name == fixture.group(1)) and (
                not nows or any(d not in held for d, held in zip(digests, accepted))
                or ((name, case) in helper_digests
                    and _helpers_stale(releg, name, case, helper_digests[(name, case)], text, "\n".join(nows)))):
            entry = "%s (%s)" % (case, owner)
            if nows and case_identity.changed_by_refactor(name, case):
                entry += ": the record is stale against a verified refactor"
            changed.append(entry)
    for entry in changed:
        write(sys.stdout, entry)
    if releg and not changed:
        def rewrite(_, record, name, case, __):
            if (name, case) in releg:
                return record + "\n" + frozen_record.helpers_line(name, case, releg[(name, case)])
            return record
        if not rewrite_records(_earlier_records(lines, step), rewrite):
            return 2
        for name, case in releg:
            write(sys.stderr, "tests-frozen.sh: %s (%s): its helpers digest was re-recorded from the legacy formula"
                  % (case, name))
    if changed:
        remove_pass_marker(step)
    elif step:
        tree = work_tree_hash()
        if not tree:
            remove_pass_marker(step)
            write(sys.stderr, "tests-frozen.sh: the work-tree hash could not be computed: git add -A or git write-tree failed")
            return 2
        write_pass_marker(step, tree)
    return 1 if changed else 0


def is_diff_checked(line):
    kind = KIND_RE.search(trailing_markers(line))
    return bool(kind) and kind.group(1) == "diff-checked"


write_record = lambda path, out: frozen_record.write_record(path, out, open)
rewrite_records = lambda earlier, rewrite: frozen_record.rewrite_records(earlier, rewrite, open)


def rerecord_earlier(ledger, step):
    if not is_diff_checked(step):
        return 3
    root = _toplevel()
    if root is None:
        write(sys.stderr, "tests-frozen.sh: not inside a git repository\n%s" % USAGE)
        return 2
    try:
        with open(ledger, encoding="utf-8") as handle:
            lines = handle.read().splitlines()
    except OSError as error:
        write(sys.stderr, "tests-frozen.sh: %s\n%s" % (error, USAGE))
        return 2
    ledger = os.path.abspath(ledger)
    os.chdir(root)
    base = case_history.first_revision_with(step, ledger)
    if not base:
        write(sys.stderr, "tests-frozen.sh: no commit touches the ledger %s, so the step base is unknown" % ledger)
        return 2
    after = {}

    def recorded_base(name, case, digest):
        revs = case_history.revisions(name, since=base)
        for rev in revs:
            if body_digest(case_history.cases_at(rev, name).get(case, "")) == digest:
                return rev
        return base

    def rewrite(_, record, name, case, digest):
        if name not in after:
            after[name] = case_history.cases_at("HEAD", name)
        before = case_history.cases_at(recorded_base(name, case, digest), name)
        now = after[name].get(case)
        if now is not None and now != before.get(case):
            head_text = case_history.text_at("HEAD", name, quiet=True)
            body = "\n".join(case_identity.bodies_of(head_text, case))
            if not case_identity.helpers_in(head_text, body):
                return body_line(name, case, now)
            return body_line(name, case, now) + "\n" + frozen_record.helpers_line(
                name, case, case_identity.helper_digest(head_text, body))
        return record
    try:
        if not rewrite_records(_earlier_records(lines, step), rewrite):
            return 2
    except OSError as error:
        write(sys.stderr, "tests-frozen.sh: %s" % error)
        return 2
    return 0


def rerecord_committed(step, root):
    here = os.getcwd()
    os.chdir(root)
    try:
        return _rerecord_committed(step)
    finally:
        os.chdir(here)


def _rerecord_committed(step):
    path = record_path(step)
    if not os.path.exists(path):
        return 0
    with open(path, encoding="utf-8") as handle:
        records = handle.read().splitlines()
    held, out, changed = {}, [], False
    for record in records:
        parsed = body_record(record)
        if parsed:
            name, case = parsed[0], parsed[1]
            if name not in held:
                at_head = case_history.cases_at("HEAD", name)
                before = case_history.cases_at("HEAD~1", name) if case_history.has_rev("HEAD~1") else {}
                if os.path.exists(name):
                    tree = dict(_head_and_new_cases(name)[1])
                    if tree != at_head:
                        at_head, before = tree, case_history.cases_at("HEAD", name)
                recorded = {r[1] for r in map(body_record, records) if r and r[0] == name}
                held[name] = (at_head, [c for c in at_head if c not in recorded and c not in before])
            at_head, fresh = held[name]
            if case not in at_head and fresh:
                new = next((c for c in fresh if body_digest(at_head[c].replace(c, case)) == parsed[2]), None)
                if new is None and len(fresh) > 1:
                    write(sys.stderr, "tests-frozen.sh: %s: cannot pair %s with one of %d new cases" % (path, case, len(fresh)))
                    return 2
                new = new or fresh[0]
                fresh.remove(new)
                record = body_line(name, new, at_head[new])
                changed = True
        out.append(record + "\n")
    return 0 if not changed or write_record(path, out) else 2


# Spellings the process suite reads off this module (it never patches them); the rules live in case_identity.
_helper_digest = case_identity.helper_digest
_bodies_of = case_identity.bodies_of
_assertion_lines = case_identity.assertion_lines


def _is_suite_repair_green(lines, green):
    """True when `green` is one of the own commits of a ticked ⟦suite-repair⟧ step of the ledger `lines`: only
    then may a frozen case's body at `green^` stand for its record. A suite-repair step ticked elsewhere in the
    ledger vouches for its own commits, never for another step's green; any lookup that fails refuses."""
    try:
        sha = case_history.commit_of(green)
    except OSError:
        return False
    for line in lines:
        match = ledger.ITEM_RE.match(line)
        if not match or match.group(1) == " " or not carries_mark(trailing_markers(match.group(2)), "suite-repair"):
            continue
        try:
            if sha in _step_commits(match.group(2)):
                return True
        except (LookupError, OSError):
            continue
    return False


def rerecord_refactored(ledger, green):
    with open(ledger, encoding="utf-8") as handle:
        lines = handle.read().splitlines()
    os.chdir(_toplevel())
    try:
        with open(".tdd/verdict-refactor.exit", encoding="utf-8") as handle:
            if handle.read().strip() not in ("0", "skipped"):
                return 3
    except FileNotFoundError:
        return 3

    recorded_helpers = {}
    for _, __, records in _earlier_records(lines, ""):
        recorded_helpers.update(helper_records(records))

    def skip(name, case, record, reason):
        write(sys.stderr, "skipped: %s %s (%s)" % (name, case, reason))
        return record

    exempt = set()
    for line in lines:
        item = ITEM_RE.match(line)
        parsed = _parse_replaces(item.group(2)) if item else None
        if parsed:
            exempt.update((parsed[1], c) for c in parsed[0])
    seen = {}
    repaired = _is_suite_repair_green(lines, green)

    def nth(rev, name, case, k):
        found = case_identity.bodies_of(case_history.text_at(rev, name, quiet=True), case)
        return found[k] if k < len(found) else None

    def rewrite(_, record, name, case, digest):
        if (name, case) in exempt:
            return record
        k = seen[(name, case)] = seen.get((name, case), -1) + 1
        verified = nth(green, name, case, k)
        head = nth("HEAD", name, case, k)
        green_text = case_history.text_at(green, name, quiet=True)
        before = nth(green + "^", name, case, k) if repaired else None
        if verified is None or head is None or digest not in {body_digest(verified), body_digest(head), *map(
                body_digest, (b for c, b in old_cut_cases_all(green_text) if c == case)),
                *([body_digest(before)] if before else [])}:
            return skip(name, case, record, "body digest matches neither green nor HEAD")
        green_helpers = case_identity.helper_digest(green_text, verified)
        if (digest != body_digest(head) or digest == body_digest(verified)) and recorded_helpers.get(
                (name, case), green_helpers) != green_helpers:
            return skip(name, case, record, "helpers digest differs from green's")
        helpers = case_identity.called_helpers("HEAD", name, head)
        called = set(re.findall(r"^(?:func|def)\s+(\w+)", helpers, re.M))
        head_lines = [l for l in case_identity.checked_lines(head) if l.split("(")[0] not in called]
        verified_lines = case_identity.checked_lines(verified)
        verified_count = collections.Counter(verified_lines + case_identity.checked_lines(case_identity.called_helpers(green, name, verified + "\n" + head)))
        carried = collections.Counter(head_lines + case_identity.checked_lines(helpers))
        if head_lines != verified_lines and carried != verified_count:
            return skip(name, case, record, "assertion lines of case plus helpers differ from green's")
        if head_lines == verified_lines and len(case_identity.checked_lines(helpers)) \
                != len(case_identity.checked_lines(case_identity.called_helpers(green, name, verified))):
            return skip(name, case, record, "helper assertion count differs from green's")
        if not verified_lines and case_identity.squeezed(head) != case_identity.squeezed(verified):
            return skip(name, case, record, "case has no assertion lines and its body changed")
        head_text = case_history.text_at("HEAD", name, quiet=True)
        return body_line(name, case, head) + "\n" + frozen_record.helpers_line(
            name, case, case_identity.helper_digest(head_text, "\n".join(case_identity.bodies_of(head_text, case))))
    if not rewrite_records(_earlier_records(lines, ""), rewrite):
        return 2
    return _check_earlier(ledger, "", sanctioned=exempt)


def rerecord_rebased(ledger, pre):
    try:
        with open(ledger, encoding="utf-8") as handle:
            lines = handle.read().splitlines()
    except FileNotFoundError:
        return 3
    os.chdir(_toplevel())
    upstream = "origin/" + case_history.default_branch()
    refused, missing, stale = [], [], False
    try:
        earlier = list(_earlier_records(lines, "", strict=True))
    except OSError as error:
        write(sys.stderr, "tests-frozen.sh: a record could not be read: %s" % error)
        return 2

    latest_owner = {}
    for who, _, records in earlier:
        for body in filter(None, map(body_record, records)):
            latest_owner[(body[0], body[1])] = who

    def rewrite(owner, record, name, case, digest):
        nonlocal stale
        if latest_owner.get((name, case), owner) != owner:
            return record
        head = case_history.cases_at("HEAD", name).get(case)
        if head is None and not case_history.cases_at(pre, name).get(case):
            return None
        if head is None:
            paths = [path for who, path, _ in earlier if who == owner]
            missing.append("tests-frozen.sh: record %s names case %s, which %s does not hold at HEAD"
                           % (paths[0], case, name))
            return record
        if body_digest(head) == digest:
            return record
        if (body_digest(case_history.cases_at(pre, name).get(case, "")) != digest
                or head != case_history.cases_at(upstream, name).get(case)):
            refused.append("%s (%s)" % (case, owner))
            return record
        stale = True
        return body_line(name, case, head)
    if not rewrite_records(earlier, rewrite):
        return 2
    if missing:
        write(sys.stderr, "\n".join(missing))
        return 2
    for line in refused:
        write(sys.stdout, line)
    return 1 if refused else 0 if stale else 3


_said = []


def write(stream, text):
    _said.append(text)
    entry.write(stream, text)


def _log_refusal(code):
    """Journal a refused `record` (exit 1 or 2) as a tests-frozen-refused event: the exit code and the last thing said."""
    reason = " ".join(_said[-1].split()) if _said else ""
    event.mark(".", event.context(os.environ), "tests-frozen-refused", ["exit=%d" % code, "reason=" + reason])


def _take_red_case(files):
    if "--red-case" not in files:
        return None
    at = files.index("--red-case")
    if at + 1 == len(files):
        write(sys.stderr, "tests-frozen.sh: --red-case needs a <red-test-id>\n%s" % USAGE)
        return 2
    value = files[at + 1]
    if not all(value.partition("::")[::2]):
        write(sys.stderr, "tests-frozen.sh: --red-case %s needs a path and a case around '::'" % value)
        return 2
    path, _, case = value.partition("::")
    try:
        with open(path, encoding="utf-8", errors="replace") as handle:
            present = case in dict(cut_cases(handle.read()))
    except FileNotFoundError:
        present = False
    if not present:
        write(sys.stdout, "tests-frozen.sh: red case %s::%s no longer exists\n" % (path, case))
        return 1
    del files[at:at + 2]
    return None


def main(argv):
    del _said[:]
    code = _main(argv)
    if argv[:1] == ["record"] and code in (1, 2):
        _log_refusal(code)
    return code


def record(record_file, files, step=None):
    """`record`: freeze `files` (and the steps's cases when `step` is given) in `record_file`; the exit code.

    `files` may hold `--red-case <test-id>`, which is taken off it. Without `step` it writes one digest line per file;
    with it, it enters the repository root, adds the test files that differ from HEAD and records the step's cases."""
    by_step = step is not None
    files = list(files)
    refused = _take_red_case(files)
    if refused is not None:
        return refused
    if by_step and _refused_outside_repository():
        return 2
    deleted = []
    if by_step:
        record_file, files = _enter_root(record_file, files)
        try:
            differing = differing_tests()
        except OSError as error:
            write(sys.stderr, "tests-frozen.sh: %s" % error)
            return 2
        for name in differing:
            if name in files or name in deleted:
                continue
            (files if os.path.exists(name) else deleted).append(name)
    if not files and not deleted:
        write(sys.stderr, "tests-frozen.sh: record needs at least one test file")
        return 2
    try:
        lines = ["%s  %s\n" % (_digest(name), name) for name in files]
        lines += ["deleted  %s\n" % name for name in deleted]
        if by_step:
            if files:
                lines.append(frozen_record.format_line())
            for name in files:
                try:
                    added = _added_cases(name)
                    if name in _guard_subjects(step):
                        added = [c for c in added if c[0] not in _head_and_new_cases(name)[0]]
                    kept = [c for c in _kept_cases(record_file, name, step, [a[0] for a in added]) if c[0] not in {a[0] for a in added}]
                except UnclosedCase as error:
                    raise LookupError("%s: %s" % (name, error))
                if _recorded_digests(record_file, name) and not kept and not added:
                    write(sys.stderr, "tests-frozen.sh: step %s: every case recorded for %s is gone from HEAD "
                          "with no renamed successor: nothing left to record\n" % (step, name))
                    return 2
                for case, body in added + kept:
                    lines += frozen_record.case_lines(name, case, body)
        with open(record_file, "w") as handle:
            handle.writelines(lines)
    except (OSError, LookupError) as error:
        write(sys.stderr, "tests-frozen.sh: %s" % error)
        return 2
    return 0


def check(record_file, step=None):
    """`check`: the exit code of comparing `record_file`'s files with the tree (0 intact, 1 changed, 2 no answer),
    naming each changed file on stdout; with `step`, also the test files that differ from HEAD and are not recorded."""
    by_step = step is not None
    if by_step and _refused_outside_repository():
        return 2
    if by_step and not _has_head():
        write(sys.stderr, "tests-frozen.sh: repository has no HEAD commit")
        return 2
    if by_step:
        record_file, _ = _enter_root(record_file, [])
    try:
        with open(record_file) as handle:
            entries = [entry for entry in map(frozen_record.digest_entry, handle) if entry]
    except OSError:
        write(sys.stderr, "tests-frozen.sh: record %s is missing" % record_file)
        return 2
    if not entries or any(len(entry) != 2 for entry in entries):
        write(sys.stderr, "tests-frozen.sh: record %s is malformed" % record_file)
        return 2
    fixture = _FIXTURE_FILE.search(step) if by_step and carries_mark(trailing_markers(step), "fixture-repair") else None
    loose = fixture.group(1) if fixture else None
    subjects = _guard_subjects(step) if by_step else []
    changed = []
    for expected, name in entries:
        if expected == "deleted":
            if os.path.exists(name):
                changed.append(name)
            continue
        try:
            if _digest(name) != expected and not (name == loose and _recorded_cases_intact(record_file, loose)) and name not in subjects:
                changed.append(name)
        except OSError:
            changed.append(name)
        except UnclosedCase as error:
            write(sys.stderr, "tests-frozen.sh: %s: %s" % (name, error))
            return 2
    if by_step:
        recorded = {name for _, name in entries}
        parsed = _parse_replaces(step)
        exempt = {parsed[1]} if parsed else set()
        if fixture:
            exempt.add(fixture.group(1))
        exempt.update(subjects)
        try:
            differing = differing_tests()
        except OSError as error:
            write(sys.stderr, "tests-frozen.sh: %s" % error)
            return 2
        changed += [name for name in differing
                    if name not in recorded
                    and (name not in exempt
                         or (name in subjects and not os.path.exists(name)))]
    for name in changed:
        write(sys.stdout, name)
    return 1 if changed else 0


def _main(argv):
    rest = argv[4:]
    if argv[:1] == ["rerecord-earlier"] and len(argv) == 4 and argv[2] == "--step" and argv[3]:
        return rerecord_earlier(argv[1], argv[3])
    if argv[:1] == ["rerecord-refactored"] and len(argv) == 3:
        return rerecord_refactored(argv[1], argv[2])
    if argv[:1] == ["rerecord-rebased"] and len(argv) == 3:
        return rerecord_rebased(argv[1], argv[2])
    if (argv[:1] == ["check-earlier"] and len(argv) >= 4 and argv[2] == "--step" and argv[3]
            and len(rest) % 2 == 0 and all(flag == "--except" and name for flag, name in zip(rest[::2], rest[1::2]))):
        return _check_earlier(argv[1], argv[3], rest[1::2])
    mode = argv[0] if argv else ""
    if mode == "check-earlier":
        write(sys.stderr, USAGE)
        return 2
    record_file = argv[1] if len(argv) > 1 else ""
    if not record_file:
        write(sys.stderr, USAGE)
        return 2
    if mode == "path":
        write(sys.stdout, record_path(record_file))
        return 0
    step, files = None, argv[2:]
    if record_file == "--step":
        step = argv[2] if len(argv) > 2 else ""
        if not step:
            write(sys.stderr, USAGE)
            return 2
        if any(carries_mark(trailing_markers(step), mark) for mark in REPAIR_MARKS if mark != "fixture-repair"):
            return 0
        record_file, files = record_path(step), argv[3:]
    if mode == "record":
        return record(record_file, files, step)
    if mode == "check":
        return check(record_file, step)
    write(sys.stderr, USAGE)
    return 2


if __name__ == "__main__":
    entry.run(main, sys.argv[1:])
