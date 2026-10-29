4. **The fast command still passes.** Run `{{FAST_CMD}}` once on this tree. Green may not
   edit a test, so a red whose own file fails that command for any reason other than the
   target test's expected failure (a lint error, a type error, another case that fails)
   leaves a step no green can pass. REJECT it, naming the file and the error.
