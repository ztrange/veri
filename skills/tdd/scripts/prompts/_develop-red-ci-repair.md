**This step repairs a red CI run.** The failing CI job's log quoted in the step text — its
test id and assertion diff — is this step's evidence of failure, whatever the case does on
this machine. If the case passes locally, report `AGAINST_UNMODIFIED: PASSES` as it is; on
this step that does not make it a pin, because the failure it answers is the CI one.
