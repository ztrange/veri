"""What a pull request head's CI state means for wait-ci.sh: values in, a decision out, no I/O.

`decide(observation, marks, now, loop, options)` maps one answered read of the head, the marks kept on disk for
it, the clock (None until a `Need("now")` asks for it) and what earlier polls of this call carried (`Loop`) to a
`Decision`: the marks to write or remove,
then the outcome (`Exit`, `Sleep`, a `Need` to answer first, or a `Crash`) and the `Loop` for the next poll.
Reading GitHub, the marks and the clock, and sleeping, are wait_ci's and ci_marks's."""
import re
from dataclasses import dataclass, replace

RETRY_CAP = 60
UNREAD_LIMIT = 3


@dataclass(frozen=True)
class Options:
    """What the arguments and tunables fix for the whole call."""
    pr: str
    want: str
    explicit: bool
    on_pr: str
    no_run_wait: int
    queue_wait: str
    poll: str
    span: int
    total: int
    head_wait: int = 600


@dataclass(frozen=True)
class Observation:
    """One read of the head that answered: <state> is none, skipped, pending, green or red.
    <no_workflow> is None until the probe for a pull_request workflow was made."""
    state: str
    head: str
    failed: str = ""
    queued: bool = False
    mergeable: object = None
    draft: bool = False
    no_workflow: object = None


@dataclass(frozen=True)
class Loop:
    """What polls of one call carry: the deadline (a decimal string) with the key and whether it was inherited,
    the end of the slice, and the first none sighting with the head it was for."""
    deadline: str = ""
    key: str = ""
    inherited: bool = False
    slice_end: object = None
    first_none: object = None
    none_head: object = None


@dataclass(frozen=True)
class Exit:
    code: int
    out: str = ""
    err: str = ""


@dataclass(frozen=True)
class Sleep:
    seconds: str


@dataclass(frozen=True)
class Need:
    """A fact decide asks for before it can answer: decide again with it supplied. <what> is `workflow` (set
    `no_workflow` on the observation: whether nothing under .github/workflows triggers on pull_request) or `now`
    (pass the clock). A fact is asked for only on the paths that use it, so a caller reads it only then."""
    what: str


@dataclass(frozen=True)
class Crash:
    """An unreadable tunable met mid-decision: apply the effects, then raise <error>."""
    error: Exception


@dataclass(frozen=True)
class Record:
    kind: str
    key: str
    value: str


@dataclass(frozen=True)
class Remove:
    kind: str
    key: str


@dataclass(frozen=True)
class Decision:
    outcome: object
    effects: tuple
    loop: Loop


def decimal(text):
    return str(int(text)) if re.fullmatch(r"[0-9]+", text) else None


def retry_sleep(poll, unread, backoff):
    if backoff != "1":
        return poll
    try:
        return "%g" % min(RETRY_CAP, float(poll) * 2 ** (unread - 1))
    except ValueError:
        return poll


def _warn(message):
    return "wait-ci.sh: %s\n" % message


def decide(obs, marks, now, loop, opts):
    state, head = obs.state, obs.head
    if state in ("none", "skipped") and obs.mergeable is False:
        return Decision(
            Exit(2, "", _warn("%s conflicts with its base branch; no workflow will start until it is rebased"
                              % opts.pr)), (), loop)
    mismatched = bool(opts.want and head != opts.want)
    cleared = (Remove("head", opts.want),) if opts.want and marks.head is not None else ()
    matched = () if mismatched else cleared
    if state == "none" and opts.on_pr == "0" and not mismatched:
        return Decision(Exit(0, "", _warn("%s has no checks and VERI_CI_ON_PR=0 says none will come" % opts.pr)),
                        matched, loop)
    if state == "none" and not opts.explicit:
        if obs.no_workflow is None:
            return Decision(Need("workflow"), (), loop)
        if obs.no_workflow:
            return Decision(
                Exit(0, "", _warn("%s has no checks and no workflow triggers on pull_request; no check will come"
                                  % opts.pr)), cleared, loop)
    none = state == "none"
    effects = ([] if none else [Remove("none", head)]) + list(matched)
    if state == "skipped" or mismatched:
        state = "pending"

    def done(outcome):
        return Decision(outcome, tuple(effects), loop)

    if state == "green":
        return done(Exit(0))
    if state == "red":
        return done(Exit(1, obs.failed + "\n" if obs.failed else ""))
    if now is None:
        return Decision(Need("now"), (), loop)
    if mismatched:
        first = now if marks.head is None else marks.head
        if marks.head is None:
            effects.append(Record("head", opts.want, str(now)))
        if now - first >= opts.head_wait:
            return done(Exit(2, "", _warn("%s still reports head %s, not the expected %s, "
                                          "%d s after it was first seen differing"
                                          % (opts.pr, head, opts.want, now - first))))
    if none and obs.mergeable:
        if loop.none_head != head:
            first = now if marks.none is None else marks.none
            if marks.none is None:
                effects.append(Record("none", head, str(now)))
            loop = replace(loop, none_head=head, first_none=first)
        if now - loop.first_none >= opts.no_run_wait:
            return done(Exit(2, "", _warn("no CI run for %s" % head)))
    if loop.slice_end is None:
        loop = replace(loop, slice_end=now + opts.span)
    if obs.queued and not mismatched:
        key = opts.want or head
        first = now if marks.queued is None else marks.queued
        if marks.queued is None:
            effects.append(Record("queued", key, str(now)))
        try:
            patience = int(opts.queue_wait)
        except ValueError as error:
            return done(Crash(error))
        if now - first > patience:
            return done(Exit(2, "", _warn("checks of %s never started: queued since %s" % (opts.pr, first))))
    if mismatched or obs.queued:
        return done(Exit(3) if now >= loop.slice_end else Sleep(opts.poll))
    if not loop.deadline:
        key = opts.want or head
        inherited = marks.deadline is not None
        if inherited:
            deadline = decimal(marks.deadline.rstrip("\n"))
            if deadline is None:
                return done(Exit(2, "", _warn("deadline file %s is unreadable or not a non-negative whole number"
                                              % marks.deadline_path)))
        elif obs.draft:
            return done(Exit(2, "", _warn("%s is a draft; mark it ready before waiting on its checks" % opts.pr)))
        else:
            deadline = str(now + opts.total)
            effects.append(Record("deadline", key, deadline))
        loop = replace(loop, deadline=deadline, key=key, inherited=inherited)
    if now >= int(loop.deadline):
        if loop.inherited:
            return done(Exit(2, "", _warn("checks of %s still pending past the deadline recorded for %s"
                                          % (opts.pr, loop.key))))
        return done(Exit(3))
    return done(Exit(3) if now >= loop.slice_end else Sleep(opts.poll))
