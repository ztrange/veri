**This step repairs a failure that reproduces only on CI.** Its local suites are green both
before and after the fix, so it is not judged by the local check that the target goes red
when the fix is removed: skip that check. The evidence is CI's — the failing CI job's log
before the fix, and a green CI run on the pushed fix. PASS only when both are present and
the run is green; a missing log or a run still red is a REJECT.
