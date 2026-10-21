## The skill-edit step

Run `$S/skill-edit-step.sh` on the issue body and the step's unit.

On exit 0 or 3, tick the step and commit the ticked ledger.

On exit 1, bail with `cause=revise-exhausted`, as an exhausted revise.

On exit 2, treat it as no answer and handle it as a killed-stuck leaf.
