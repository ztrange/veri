### A background process a veri script or test starts is killed by its recorded PID, never by a job spec, so it dies whether or not the starting shell is still alive
- inline the single-use `report` helper in background-kill.test.sh
### A background process that is still running when its starting shell exits is reported, naming its PID and what started it, rather than being left silently
- the three "recorded no pid / recorded nothing in <record> (exit …, stderr: …)" problem messages in cases 1, 2 and 3 are one assertion spelled three times; a helper taking the record, the exit code and the stderr file would say it once
