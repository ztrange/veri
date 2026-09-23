### A background process a veri script or test starts is killed by its recorded PID, never by a job spec, so it dies whether or not the starting shell is still alive
- inline the single-use `report` helper in background-kill.test.sh
### A background process that is still running when its starting shell exits is reported, naming its PID and what started it, rather than being left silently
- the three "recorded no pid / recorded nothing in <record> (exit …, stderr: …)" problem messages in cases 1, 2 and 3 are one assertion spelled three times; a helper taking the record, the exit code and the stderr file would say it once
### A guard names `<file>:<line>` and fails the run when a file under `skills/` kills a background process by job spec (`kill %…`), with an exemption table carrying a reason per entry
- job-spec-guard.test.sh's driver repeats a four-line `exempt` → `probe_entry_is_in_the_table` → `run_guard` → probe shape twice, varying only the reason and the probe; folding it into one helper would need the probe passed by name, and indirect dispatch reads worse here than the repetition
