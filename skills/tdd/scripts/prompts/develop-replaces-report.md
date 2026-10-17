{{SHARED}}

## Phase: develop-replaces-report

Your earlier Red report is the file `{{REPORT_FILE}}`. It carries no `REPLACES:` line for
each of the cases below, so the step cannot be checked. Read the report, and answer with a
corrected one that carries a `REPLACES: <case> => <test id>` line for every one of them,
the case name exactly as the step spells it. The test id is the pytest node id,
<path from the repository root>::<test name>, and each line starts at column 0 with
no bullet or other prefix.

### The cases with no REPLACES: line

{{MISSING_CASES}}

### The step

{{STEP}}

### The issue's behavior spec (context)

{{ISSUE_SPEC}}

### What to do

Change no test and no production file: only the report is wrong. Do not run a suite.

### Report (last lines of your output)

REPLACES: <case> => <test id>

REPORT-FORMAT replaces-report | keys REPLACES: | suite exempt: the report is corrected and no file changed
