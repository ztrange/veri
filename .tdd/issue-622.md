# Plan for #622 — detach-command.sh leaves SIGPIPE ignored for every process it starts

- [x] a writer started through `detach-command.sh start` whose reader closes early is killed by SIGPIPE (status 141) and prints nothing on stderr, as it does when started from a shell ⟦criterion 1⟧
- [x] `detach-command.sh start` still runs its command in a session of its own, records its exit code in `.tdd/<name>.exit` and its output in `.tdd/<name>.out`, and `wait` keeps its exit codes 0/1/2/3 ⟦criterion 2⟧
- [ ] every case `detach-command.test.sh` already holds is still in the suite with its assertions unchanged by the branch's diff ⟦diff-checked⟧ ⟦criterion 3⟧
