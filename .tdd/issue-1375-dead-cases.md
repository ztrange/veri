# Dead cases for #1375

The pairs table's dead rows: cases deleted, not ported. Their subject is lib/missing-argument-exit.sh, which leaves with the audit, or positional parsing in shell, which no scripts/*.sh shim does (every one is a /bin/sh shim exec'ing python3).

| suite | name= text | why dead |
|---|---|---|
| missing-argument-exit.test.sh | `the missing-argument audit covers a script added to the scripts/ directory whose usage line names a required argument` | its subject is lib/missing-argument-exit.sh's discovery, which leaves with the audit; the run_cli no-argument case discovers its own subjects |
| missing-argument-exit.test.sh | `the missing-argument audit returns 1 when a script it audits is an offender` | its subject is lib/missing-argument-exit.sh's return status, which leaves with the audit |
| missing-argument-exit.test.sh | `the missing-argument audit over a directory holding no script prints nothing and returns 0` | its subject is lib/missing-argument-exit.sh's empty-directory answer, which leaves with the audit |
| missing-argument-exit.test.sh | `the missing-argument audit calls only scripts whose usage line names a required argument, and wants each one's usage line to name it` | its subject is lib/missing-argument-exit.sh's subject selection, which leaves with the audit |
| missing-argument-exit.test.sh | `no script guards a required positional argument with a bare \${N:?…} expansion` | its subject is positional parsing in shell, which no scripts/*.sh shim does |
| unit/missing-argument-guard.test.sh | `the guard names a script that exits 1, not 2, when its required argument is missing` | its subject is lib/missing-argument-exit.sh's offender report, which leaves with the audit |
| unit/missing-argument-guard.test.sh | `the guard names a script guarding a required argument with a bare \${N:?…} expansion` | its subject is the bare-expansion scan of positional parsing in shell, which no scripts/*.sh shim does |
| unit/missing-argument-guard.test.sh | `the audit finds its own subjects: every script printing a usage line that does not exit 2 with its own usage text when its required argument is missing` | its subject is lib/missing-argument-exit.sh's discovery, which leaves with the audit |
| unit/missing-argument-guard.test.sh | `the audit over a directory with no scripts prints nothing, on either stream, and returns 0` | its subject is lib/missing-argument-exit.sh's empty-directory answer, which leaves with the audit |
