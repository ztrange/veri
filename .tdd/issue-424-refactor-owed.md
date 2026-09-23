### A background process a veri script or test starts is killed by its recorded PID, never by a job spec, so it dies whether or not the starting shell is still alive
- inline the single-use `report` helper in background-kill.test.sh
