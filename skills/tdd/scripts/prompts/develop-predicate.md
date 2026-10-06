{{SHARED}}

## Phase: develop-predicate

{{INCLUDE:_develop-structural-pass.md}} Before a transform leaf applies the
candidate below, it needs a check its verifier can run. Write **one shell predicate** for
it — a command that fails (exits non-zero) on the current tree, and succeeds (exits 0) once
the candidate is applied. Apply nothing yourself, and change no file.

### The candidate

{{STEP}}

### Bounds

The transform may change only the files this issue touched:

{{TOUCHED_FILES}}

{{INCLUDE:_develop-spec-context-only.md}}

1. Read the candidate and the files it names.
2. Write one shell command, runnable from the repository root, that observes the candidate's
   end state in those files — a `grep`, a `test`, a count compared — and nothing else.
3. Run it on the current tree and confirm it fails. When the candidate is already applied on
   the current tree, report the predicate that observes its end state anyway — it then
   succeeds — and never PREDICATE: NONE.
4. Keep PREDICATE: NONE for a candidate no single command can observe: when no command can
   tell the tree before the candidate from the tree after it, say why instead of writing one.

### Report (last line of your output)

PREDICATE: <command>

or

PREDICATE: NONE — <why>
