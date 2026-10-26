**A rewritten test is a new test, and owes a new prediction**: predict its failure
   before you run any suite, in `.tdd/red-prediction.md` — which assertion fires first against the unmodified
   production code, the observed-versus-expected values it fires on, and the shape of the
   message the suite will print — then run, saving the run's output to `.tdd/red-run-output.txt`, and compare what it printed against that
   prediction; never adjust the prediction to fit what you saw. The leaf whose attempt was
   rejected predicted a different test, so there is nothing here for you to inherit.
