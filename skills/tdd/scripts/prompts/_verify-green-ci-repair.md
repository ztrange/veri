**This step repairs a failure that reproduces only on CI.** Its local suites are green both
before and after the fix, so it is not judged by the local check that the target goes red
when the fix is removed: skip that check. The evidence is what exists before the push: the
failing CI job's log before the fix. PASS when the step quotes that log, the diff touches
what the failure names, and the local suites are green. Never require a CI run on the fix:
until after the push, no CI run exists, and the step's latest CI run being the red one that
created it is expected. A green CI run on the pushed fix is the verdict of `wait-ci.sh`
after your PASS, where red bails `ci-red`.
