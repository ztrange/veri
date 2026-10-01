# Plan for #497 — the usage and exit-code contract lives in one module

- [ ] lib/exit-contract.sh, sourced not run, provides refuse: it prints its message (if given) then the caller's $USAGE on stderr and exits 2 ⟦criterion 1⟧
- [ ] lib/exit-contract.sh provides require_args <n> "$@": it refuses with the caller's $USAGE unless the first n arguments are present and non-empty, and returns 0 otherwise ⟦criterion 1⟧
- [ ] lib/exit-contract.sh provides to_contract <code>: it prints the code unchanged when it is 0, 1, 2 or 3 and prints 2 for any other code ⟦criterion 3⟧
- [ ] The missing-argument audit finds its own subjects: every script whose source prints a usage line is called without its required arguments and must exit 2 with its own usage text on stderr, with no hand-kept roster ⟦criterion 2⟧
- [ ] Every script under scripts/ whose name sorts a–l and that refuses a missing or bad argument sources lib/exit-contract.sh and refuses through refuse or require_args, with no hand-built usage-and-exit idiom left ⟦criterion 1⟧
- [ ] Every script under scripts/ whose name sorts m–z and that refuses a missing or bad argument sources lib/exit-contract.sh and refuses through refuse or require_args, with no hand-built usage-and-exit idiom left ⟦criterion 1⟧
- [ ] A pass-through audit fails any `exit "$var"` or `exit $?` in a script that neither maps through to_contract nor carries a `# pass-through: <why>` marker, and every such site in scripts/ passes it ⟦criterion 3⟧
- [ ] A script whose child command exits with a code outside 0–3 at a mapped site (run-leaf.sh's claude, tick-ledger.sh's and clear-refactor-pending.sh's ledger call) exits 2, never the foreign code ⟦criterion 4⟧
- [ ] Every script's behaviour is otherwise unchanged ⟦full-suite⟧ ⟦criterion 5⟧
