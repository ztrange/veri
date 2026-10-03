{{SHARED}}

## Phase: develop-predicate

This is the issue's **structural pass**: every step is green, and the structural candidates
the steps recorded instead of applying are now due. Before a transform leaf applies the
candidate below, it needs a check its verifier can run. Write **one shell predicate** for
it — a command that fails (exits non-zero) on the current tree, and succeeds (exits 0) once
the candidate is applied. Apply nothing yourself, and change no file.

### The candidate

{{STEP}}

### Bounds

The transform may change only the files this issue touched:

{{TOUCHED_FILES}}

### The issue's behavior spec (context only)

{{ISSUE_SPEC}}

### The test command

{{TEST_CMD}}

### What to do

1. Read the candidate and the files it names.
2. Write one shell command, runnable from the repository root, that observes the candidate's
   end state in those files — a `grep`, a `test`, a count compared — and nothing else.
3. Run it on the current tree and confirm it fails. A predicate that already succeeds says
   nothing about the transform.
4. When no single command can tell the tree before the candidate from the tree after it,
   say why instead of writing one.

### Report (last line of your output)

PREDICATE: <command>

or

PREDICATE: NONE — <why>
