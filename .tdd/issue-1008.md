# Plan for #1008 — run-suite.sh doesn't set maintenance.auto=false, so leaves see run-conductor.test.sh go falsely red

- [x] A suite run through run-suite.sh reads maintenance.auto=false from its git config (git config --get maintenance.auto prints false inside the suite), as it does under make test ⟦criterion 1⟧ ⟂ refactor pending
