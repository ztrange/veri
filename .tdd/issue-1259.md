# Plan for #1259 — PRD 009 C2: pytest drives a script's CLI in-process through one run_cli fixture, tests the 72 shims once, and splits small from medium by marker

- [x] A `@pytest.mark.process` mark with no boundary string, or with an empty one, fails collection with an error naming the test ⟦criterion 5⟧
- [x] An unregistered mark on a pytest case under tests/py/ fails collection, naming the test and the mark (`process` registered under `--strict-markers`) ⟦criterion 5⟧
- [x] The shared `run_cli` fixture calls a module's `main(argv)` in the test process with the given argv, stdin text, environment additions and cwd, and returns the exit code, stdout and stderr that running that module's `.sh` gives ⟦criterion 1⟧ ⟂ refactor pending
- [ ] `run_cli` answers `n` for a `main` that raises `SystemExit(n)` ⟦criterion 1⟧
- [ ] `run_cli` includes, in order with the module's own output, what a child process the module starts writes to the inherited stdout and stderr descriptors ⟦criterion 1⟧
- [ ] No environment change and no cwd change made through `run_cli` or by the `main` it drives outlives the case ⟦criterion 1⟧
- [ ] One small pytest case checks every top-level `skills/tdd/scripts/*.sh` is the canonical two-line shim naming a module that exists under `veri/`, and fails naming the script and what is wrong for a script with logic in it or a missing module ⟦criterion 2⟧
- [ ] The shim test's exemption table lists the six non-canonical shims with one reason each, and a stale row (a script now canonical, or gone) fails naming the script ⟦criterion 2⟧
- [ ] `make unit` runs only the small (unmarked) pytest cases; a case marked `process("<boundary>")` is not run by it ⟦criterion 4⟧
- [ ] `make test` runs the small and the medium pytest cases, and a medium case may start real `git`, a real child process or send a signal without the PATH guard refusing it ⟦criterion 4⟧
- [ ] Under both `make unit` and `make test`, an unmarked pytest case that starts `git`, `gh` or `curl` fails, naming the command ⟦criterion 4⟧
- [ ] One medium pytest case runs one shim through a symlink to the skills directory, from another working directory, and gets the exit code and stdout `run_cli` gives for that module ⟦criterion 3⟧
