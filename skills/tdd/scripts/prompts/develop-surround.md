{{SHARED}}

## Phase: develop-surround

This is a **legacy** run: the step below names one **region** of code no test covers (a file and a
symbol or line range) and one **seam**, a command or callable outside the region that drives it;
an earlier leaf confirmed that the seam reaches the region. Surround the region with
**characterization tests**: black-box cases that pin what the code does **now**, driven from
outside it.

### The step whose region to surround

{{STEP}}

{{INCLUDE:_develop-spec-context-only.md}}

1. Read the region and the seam the step names, and choose inputs that drive the seam through
   the region's behaviour: its ordinary paths, its branches and its edge cases.
2. Write the cases in one test file. Each case drives the region **only through the named
   seam** and asserts only on what the seam lets an outside caller observe (output, exit status,
   return value, files written). It imports or calls nothing inside the region but the seam.
3. Each case pins what the **unmodified** code does: run it and record what it observes, even
   where that looks wrong. A characterization test describes the code as it is; it does not fix it.
4. Edit **no production file**: the region, the seam and every other non-test file stay exactly
   as you found them. Add or edit test files only.
5. A case that starts a process (runs a CLI, a server, a subprocess) carries the target suite's
   slow-tier mark when that suite declares one: in veri, `@pytest.mark.process("<boundary>")`.
   Where the suite declares no such mark, none is owed.
6. Run the new test file, and the suites that cover the files you touched, through the wrapper
   `{{TIMED_TEST_RUN}}`:

       {{INCLUDE:_timed-test-run-affected.md}}

   Every case must **pass** on the unmodified code. A case that fails pins nothing yet: fix the
   case, never the code.
7. Commit the new test file, and nothing else, as its own commit, its subject ending in
   `(#<issue>)`: it is the step's Surround commit, which the verifier judges.
8. Propose the region's mutant table: one `MUTANT: <file> | <old> | <new>` line per mutant, each
   a literal replacement inside the region (`<old>` is text of `<file>`, `<new>` what replaces it)
   that your cases should catch: a flipped condition, a dropped branch, a changed constant. A
   script, not you, runs every row against your cases; a mutant they leave green sends the step
   back, and a table shorter than `VERI_SURROUND_MUTANTS` (default 5) rows is owed more.
   When the spec's acceptance criteria carry `MUTATION:` lines (the criteria `coverage-blocker.sh`
   writes when a refactor refused this region), each is a row your table owes: write it as a
   `MUTANT:` line beside the rows you propose, and make your cases catch it.

### Report (last lines of your output)

TEST_PATH: <the test file holding the cases>
MUTANT: <file> | <old> | <new>     (one line per mutant)
SUITE: GREEN | RED — <the final summary line of that run>

REPORT-FORMAT surround | keys TEST_PATH: MUTANT: SUITE: | suite required
