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
7. Make no commit: leave the new test file in the working tree for the verifier.

### Report (last lines of your output)

TEST_PATH: <the test file holding the cases>
SUITE: GREEN | RED — <the final summary line of that run>

REPORT-FORMAT surround | keys TEST_PATH: SUITE: | suite required
