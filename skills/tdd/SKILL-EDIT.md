## The skill-edit step

Run `$S/skill-edit-step.sh` on the issue body and the step's unit.

On exit 0 or 3, tick the step and commit the ticked ledger.

On exit 1, bail with `cause=revise-exhausted`, as an exhausted revise.

On exit 2 (a bad argument, budget or heading, or no answer), bail at once as a system failure with `cause=no-verdict`, and never relaunch the runner or spend `VERI_STUCK_RETRIES` on it.

A killed or stuck author leaf is still retried under `VERI_STUCK_RETRIES` by the `supervise.sh` launch inside the runner, before that exit 2 reaches the conductor.

A resumed run redoes an unfinished skill-edit step from its start, with its budget reset.
