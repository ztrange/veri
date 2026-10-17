{{SHARED}}

## Phase: develop-replaces-report

Your earlier Red report is the file `{{REPORT_FILE}}`. It carries no `REPLACES:` line for
each of the cases below, so the step cannot be checked. Read the report, and answer with a
corrected one that carries a `REPLACES: <case> => <test id>` line for every one of them,
the case name exactly as the step spells it. {{NODE_ID_RULE}} The listed case names are the exact strings to copy into the
REPLACES: lines, and they take precedence over anything the issue's prose says about how
to spell a case name.

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
