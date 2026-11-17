{{SHARED}}

## Phase: develop-seam

This is a **legacy** run: the step below names one **region** of code no test covers (a file and a
symbol or line range) and one **seam**, a command or callable outside the region that is meant to
drive it, such as an entry-point CLI, an exported function or an HTTP handler. Confirm that the
named seam drives the named region from outside it, **without editing the region**. Write **NO**
test and edit **NO** file: leave the working tree exactly as you found it.

### The step whose seam to confirm

{{STEP}}

{{INCLUDE:_develop-spec-context-only.md}}

1. Read the step; find the region and the seam it names.
2. Trace, by reading the code, the path from the seam into the region: the calls, imports or
   routes through which driving the seam runs the region's code.
3. If the seam can be run without side effects outside the working tree, run it once with an
   input that reaches the region, and note what it printed or returned. Do not edit any file to
   make it run: an edit is not a seam.
4. Check `git status --porcelain` prints what it printed before you began.
5. Answer `REACHES: yes` only when driving the seam runs the region's code, the seam lying outside
   the region. Answer `REACHES: no` when no path from the seam reaches the region, or when it does
   only through an edit; say why on the `PROOF:` line.

REPORT-FORMAT seam | keys SEAM: REACHES: PROOF: | suite exempt: the leaf confirms a seam and writes no test, it runs no suite to report

### Report (last lines of your output)

SEAM: <the command or callable the step names as its seam>
REACHES: yes | no
PROOF: <one line: the path from the seam into the region, or why none reaches it without an edit>
