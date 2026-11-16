"""The process fake behind conftest's `fake_processes` fixture: a case that starts no process answers every way `subprocess` starts one.

Ask for it with the fixture, `fake_processes.answers({...})`; this docstring is its whole interface. conftest.py holds only
the fixture, a thin wrapper over `installer` here. The table-driven form is the one to use; the legacy form below is kept
for the cases that still call it.

fake_processes.answers(table, default=None, exact=False) -> fake
    <table> maps a command-line prefix to what that command does; the longest matching prefix wins. The command line is
    argv[0] by basename and the other arguments as str, joined by spaces ("git rev-parse HEAD"). exact=True: a key matches
    only the whole command line, so a longer command is unexpected (an empty key still matches nothing then).

    The answers (the value of a table entry):
        "git rev-parse": (0, "sha\\n", "")           (returncode, stdout, stderr), every time
        "git log": [(0, "a", ""), (0, "b", "")]      a sequence: successive calls take successive answers, across entry
                                                     points ("fails first, then succeeds"); once spent the call fails
                                                     loudly, naming the command
        "gh ": FileNotFoundError(2, "no gh")         an exception instance, or a class, is raised as the OS would raise it
        "git": lambda line, **kwargs: (0, "", "")    a callable is handed the command line and the keyword arguments the
                                                     caller passed (cwd, env, input, capture_output, check ...)
        "git ls-remote": HANGS                       a child that never finishes: run raises TimeoutExpired when given a
                                                     timeout; Popen hands back a hanging FakePopen (below); with no
                                                     timeout to bound it either way, the case fails with NeverReturns
    A list may mix tuples, exception instances and callables. A callable needing the unjoined argv (an argument holding
    spaces) reads fake.argvs[-1]: the call is recorded before it is answered. A call no prefix matches fails the case with
    AssertionError("unexpected process: <line>") unless <default> (any of the answers above) answers it.

    One table serves five entry points, each recorded alike:
        subprocess.run           CompletedProcess(argv, code, stdout, stderr)
        subprocess.call          the return code (an int)
        subprocess.check_call    0, or CalledProcessError(code, argv) on a non-zero code
        subprocess.check_output  stdout (bytes; str under text=/universal_newlines=/encoding=), or
                                 CalledProcessError(code, argv, output, stderr) on a non-zero code
        subprocess.Popen         a finished FakePopen, also listed in fake.popens
    Output is handed back in the caller's mode (str under text=True, bytes otherwise); stderr=STDOUT merges stderr into
    stdout; check=True on run raises CalledProcessError. An exception answer is raised by whichever entry point was
    called, Popen's constructor included: the command was still recorded.

    What the returned fake records, one entry per call, in order:
        fake.calls    the command lines (str)
        fake.argvs    the same calls as argv lists
        fake.seen     (argv, kwargs): argv as the caller passed it (full path kept), kwargs as passed
        fake.rests    the extra positional arguments after the command (subprocess.run(argv, *rest)); () for none
        fake.popens   the FakePopen objects handed out, in order

FakePopen models: pid (fixed, 4242); returncode (None until poll/wait/communicate/__exit__, then the answered code: it never
    runs); communicate(input=None, timeout=None) -> (stdout, stderr), None for a stream not asked as PIPE, stderr=STDOUT merged
    into stdout; wait(timeout=None); poll(); stdout/stderr readable streams (read, readline, iteration by line; str under text
    mode) when asked as PIPE, else None; stdin a writer when asked as PIPE, whose text stays on .stdin.written after close
    (and communicate(input=) appends to it); kill/terminate/send_signal appended to .signals, nothing else happens; a
    with-block waits on exit.
    A hanging FakePopen (a HANGS answer) is the one exception: until it is signalled, communicate/wait given a timeout raise
    TimeoutExpired and without one raise NeverReturns; once signalled they finish with returncode -<signal> and empty
    output. A signal reaches it through kill/terminate/send_signal; a case faking os.killpg forwards it by pid itself.
    NOT modelled: a running child, timeouts on a finished child (the timeout argument is ignored), a signal changing returncode,
    fileno() on the streams (a caller using os.read on them needs a process case), preexec_fn/start_new_session effects,
    pass_fds, a real pid. There is no real-process passthrough: a case needing one is a `process` case with its own setup.

The legacy form, fake_processes(answer=None) -> calls
    <answer>(line, **kwargs) -> (returncode, stdout, stderr) answers subprocess.run only. Popen, call, check_call and
    check_output refuse, naming the command (use .answers for them). With no <answer>, every entry point records and answers
    0 with empty output. Returns the list of command lines run. New cases use .answers.

Files that install their own fake on `subprocess` are a shrinking list: unit/test_local_process_fakes.py.
"""
import io
import os
import signal
import subprocess

HANGS = object()


class NeverReturns(BaseException):
    """A hanging fake child waited on with no timeout: the caller would hang without bound. A BaseException, so no
    `except Exception` in the code under test can swallow it."""


class _Written:
    """A stdin stand-in: what was written stays readable as .written after the caller closes it."""

    def __init__(self, text):
        self._stream = io.StringIO() if text else io.BytesIO()
        self.written = self._stream.getvalue()

    def write(self, data):
        count = self._stream.write(data)
        self.written = self._stream.getvalue()
        return count

    def flush(self):
        pass

    def close(self):
        self._stream.close()


class FakePopen:
    """The Popen object fake_processes.answers hands back: already finished, see this module's docstring."""
    pid = 4242

    def __init__(self, args, kwargs, code, out, err, hangs=False):
        self.args, self.returncode, self.signals = args, None, []
        self._code, self._hangs = code, hangs
        text = kwargs.get("text") or kwargs.get("encoding") or kwargs.get("universal_newlines")
        stream = io.StringIO if text else io.BytesIO
        piped = {name: kwargs.get(name) == subprocess.PIPE for name in ("stdin", "stdout", "stderr")}
        self._out = out if piped["stdout"] else None
        self._err = err if piped["stderr"] and err is not None else None
        self.stdin = _Written(text) if piped["stdin"] else None
        self.stdout = stream(self._out) if self._out is not None else None
        self.stderr = stream(self._err) if self._err is not None else None

    def _finish(self, timeout=None):
        if self._hangs and not self.signals:
            if timeout is None:
                raise NeverReturns("%r never returns, and no timeout bounds it" % (self.args,))
            raise subprocess.TimeoutExpired(self.args, timeout)
        if self._hangs:
            self._code = -self.signals[-1]
        self.returncode = self._code
        return self._code

    def communicate(self, input=None, timeout=None):
        if input is not None and self.stdin is not None:
            self.stdin.write(input)
        self._finish(timeout)
        return self._out, self._err

    def wait(self, timeout=None):
        return self._finish(timeout)

    def poll(self):
        if self._hangs and not self.signals:
            return None
        return self._finish()

    def send_signal(self, signum):
        self.signals.append(signum)

    def terminate(self):
        self.send_signal(signal.SIGTERM)

    def kill(self):
        self.send_signal(signal.SIGKILL)

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self._finish()


class FakeProcesses:
    """What fake_processes.answers hands back: the command lines run, and (argv, kwargs) per call."""

    def __init__(self, calls, seen, popens=(), rests=()):
        self.calls, self.seen, self.popens, self.rests = calls, seen, popens, rests

    @property
    def argvs(self):
        return [argv for argv, _ in self.seen]


def installer(monkeypatch):
    """The callable the fixture returns: it fakes `subprocess` through <monkeypatch>, and carries `.answers`."""
    def install(answer=None, seen=None, popens=None, every_entry=False, rests=None):
        calls = []
        rests = [] if rests is None else rests
        seen = [] if seen is None else seen
        popens = [] if popens is None else popens

        def line_of(args, kwargs=None, rest=()):
            line = " ".join([os.path.basename(str(args[0]))] + [str(a) for a in args[1:]])
            calls.append(line)
            seen.append((list(args), dict(kwargs or {})))
            rests.append(tuple(rest))
            return line

        def record(args, *rest, **kwargs):
            line_of(args, kwargs, rest)
            return subprocess.CompletedProcess(args, 0, "", "")

        def answered(args, kwargs, rest=()):
            """What the answer table says <args> did: (returncode, stdout, stderr) in the caller's mode; HANGS for a
            child that never finishes."""
            got = answer(line_of(args, kwargs, rest), **kwargs)
            if got is HANGS:
                return HANGS
            code, out, err = got
            encoding = kwargs.get("encoding") or "utf-8"
            text = kwargs.get("text") or kwargs.get("encoding") or kwargs.get("universal_newlines")

            def in_mode(value):
                if text and isinstance(value, bytes):
                    return value.decode(encoding)
                if not text and isinstance(value, str):
                    return value.encode(encoding)
                return value

            out, err = in_mode(out), in_mode(err)
            if kwargs.get("stderr") == subprocess.STDOUT:
                out, err = out + err, None
            return code, out, err

        def finished(args, kwargs, rest=()):
            """answered, for an entry point that waits for the child: a HANGS child times out, or never returns."""
            got = answered(args, kwargs, rest)
            if got is HANGS:
                if kwargs.get("timeout") is None:
                    raise NeverReturns("%r never returns, and no timeout bounds it" % (list(args),))
                raise subprocess.TimeoutExpired(list(args), kwargs["timeout"])
            return got

        def run(args, *rest, **kwargs):
            code, out, err = finished(args, kwargs, rest)
            if kwargs.get("check") and code:
                raise subprocess.CalledProcessError(code, args, out, err)
            return subprocess.CompletedProcess(args, code, out, err)

        def call(args, *rest, **kwargs):
            return finished(args, kwargs, rest)[0]

        def popen(args, *rest, **kwargs):
            got = answered(args, kwargs, rest)
            if got is HANGS:
                empty = "" if kwargs.get("text") or kwargs.get("encoding") or kwargs.get("universal_newlines") else b""
                child = FakePopen(args, kwargs, None, empty, empty, hangs=True)
            else:
                child = FakePopen(args, kwargs, *got)
            popens.append(child)
            return child

        def check_call(args, *rest, **kwargs):
            code = finished(args, kwargs, rest)[0]
            if code:
                raise subprocess.CalledProcessError(code, args)
            return 0

        def check_output(args, *rest, **kwargs):
            code, out, err = finished(args, kwargs, rest)
            if code:
                raise subprocess.CalledProcessError(code, args, out, err)
            return out

        def refuse(args, *rest, **__):
            raise AssertionError("unexpected process: %s" % line_of(args, None, rest))

        answering = {"run": run}
        if every_entry:
            answering.update(call=call, check_call=check_call, check_output=check_output, Popen=popen)
        for name in ("run", "Popen", "call", "check_call", "check_output"):
            entry = record if answer is None else answering.get(name, refuse)
            monkeypatch.setattr(subprocess, name, entry)
        return calls

    def answers(table, default=None, exact=False):
        every = dict(table, **({} if default is None else {"": default}))
        remaining = {prefix: list(what) if isinstance(what, list) else what for prefix, what in every.items()}

        def answer(line, **kwargs):
            matching = [prefix for prefix in remaining if line == prefix or not (exact and prefix) and line.startswith(prefix)]
            if not matching:
                raise AssertionError("unexpected process: %s" % line)
            what = remaining[max(matching, key=len)]
            if isinstance(what, list):
                if not what:
                    raise AssertionError("unexpected process: %s (every answer for it is spent)" % line)
                what = what.pop(0)
            if isinstance(what, BaseException) or isinstance(what, type) and issubclass(what, BaseException):
                raise what
            return what(line, **kwargs) if callable(what) else what

        seen, popens = [], []
        rests = []
        calls = install(answer, seen, popens, every_entry=True, rests=rests)
        return FakeProcesses(calls, seen, popens, rests)

    install.answers = answers
    return install
