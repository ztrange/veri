# Plan for #3734 — Cover the behaviour #3711 refactors

- [ ] Pin that `tick_ledger.run_case` looks up `detect-test-command.sh` in the scripts directory (the parent of `veri/`), not under `veri/`: a small in-process case in a new unit test file that fakes only the process boundary (`subprocess.run`) and observes the detect command path `run_case` invokes (or the command it then runs), passing on today's code and going red when the lookup is mutated to `os.path.dirname(os.path.realpath(__file__))`; no production change ⟦criterion 1⟧
