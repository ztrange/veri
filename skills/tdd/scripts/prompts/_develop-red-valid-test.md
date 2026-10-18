### What counts as a valid test

A case must hold all four of these, or it is not a test you may write:

1. **Behaviour, not mechanism.** It asserts the unit's output, exit code, the files or
   events it writes, or the error it names — never a process count, a fork count, or a
   timing across a suite run. Those are observed with `make profile` and reported in the PR
   body; a test never asserts on them. The one exception is a call count the criterion
   itself names as the behaviour (e.g. "the launcher is called once"): pin that with an
   **in-process spy** — replace the one wrapper function the code under test calls with a
   same-named function that records its calls, and assert on that record — never a `PATH`
   shim that counts real process launches across a suite run. A spy on one function call is
   behaviour; a shim counting real processes over a whole suite is the mechanism rule 2 and
   3 forbid.
2. **Lightweight.** It targets ~100ms. A costly dependency — network, a git remote, the
   `claude` binary, a real sleep or wait, a server — is replaced with a stub, a same-named
   fake, or the injected clock, unless the behaviour under test IS that dependency's real
   use, in which case one case may exercise it for real.
3. **Self-contained.** It never runs another test suite, whole or sliced, and never re-runs
   the suite it lives in.
4. **On-target.** It fails for the reason the criterion names, not an unrelated error.

If the step's criterion can only be pinned by a test that breaks 1–3 — e.g. "the suite
starts at most N processes" has no assertion that isn't a process count — **do not write
that test.** Skip straight to the report below with `AGAINST_UNMODIFIED: UNTESTABLE` and a
`WHY:` line naming which rule the only available test would break. Do not weaken the
criterion into something else it does not say, and do not write the costly or
implementation-pinning test anyway to force a pass.

A helper the test needs, which only the test uses, is defined in Red, inside the test file:
Green cannot write it there, because the test file is frozen once Red is verified. A failure
caused only by an undefined name in the test file (a NameError, or an ImportError of a name
the test file defines nowhere) is not a red, because the case fails for a missing helper and
not for the behaviour.