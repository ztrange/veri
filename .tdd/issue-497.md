# Plan for #497 — the usage and exit-code contract lives in one module

- [ ] lib/exit-contract.sh, sourced not run, provides refuse: it prints its message (if given) then the caller's $USAGE on stderr and exits 2 ⟦criterion 1⟧
- [ ] lib/exit-contract.sh provides require_args <n> "$@": it refuses with the caller's $USAGE unless the first n arguments are present and non-empty, and returns 0 otherwise ⟦criterion 1⟧
- [ ] lib/exit-contract.sh provides to_contract <code>: it prints the code unchanged when it is 0, 1, 2 or 3 and prints 2 for any other code ⟦criterion 3⟧
- [ ] A script that sources lib/exit-contract.sh and then ends with a code outside 0–3 — a `set -e` abort on a failing command, or a last command's status — exits 2 instead, unless that exit is a declared pass-through ⟦criterion 4⟧
- [ ] The missing-argument audit finds its own subjects: every script whose source prints a usage line is called without its required arguments and must exit 2 with its own usage text on stderr, with no hand-kept roster ⟦criterion 2⟧
- [ ] Every script under scripts/ whose name starts with a, b or c sources lib/exit-contract.sh, and those that refuse a missing or bad argument refuse through refuse or require_args with no hand-built usage-and-exit idiom left ⟦criterion 1⟧
- [ ] Every script under scripts/ whose name starts with d through l sources lib/exit-contract.sh, and those that refuse a missing or bad argument refuse through refuse or require_args with no hand-built usage-and-exit idiom left ⟦criterion 1⟧
- [ ] Every script under scripts/ whose name starts with m through r sources lib/exit-contract.sh, and those that refuse a missing or bad argument refuse through refuse or require_args with no hand-built usage-and-exit idiom left ⟦criterion 1⟧
- [ ] Every script under scripts/ whose name starts with s sources lib/exit-contract.sh, and those that refuse a missing or bad argument refuse through refuse or require_args with no hand-built usage-and-exit idiom left ⟦criterion 1⟧
- [ ] Every script under scripts/ whose name starts with t through z sources lib/exit-contract.sh, and those that refuse a missing or bad argument refuse through refuse or require_args with no hand-built usage-and-exit idiom left ⟦criterion 1⟧
- [ ] A pass-through audit fails any `exit "$var"` or `exit $?` in a script whose name starts with a through r that neither maps through to_contract nor carries a `# pass-through: <why>` marker, and every such site there passes it ⟦criterion 3⟧
- [ ] The pass-through audit covers every script under scripts/, and every `exit "$var"` or `exit $?` site in the scripts starting with s through z maps through to_contract or carries a `# pass-through: <why>` marker ⟦criterion 3⟧
- [ ] A script whose child command exits with a code outside 0–3 at a mapped site (run-leaf.sh's claude, tick-ledger.sh's and clear-refactor-pending.sh's ledger call) exits 2, never the foreign code ⟦criterion 4⟧
- [ ] Every script's behaviour is otherwise unchanged ⟦full-suite⟧ ⟦criterion 5⟧
