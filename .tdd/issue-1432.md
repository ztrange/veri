# Plan for #1432 — SKILL.md's script reference drifts from each script's usage line, and nothing checks it

- [ ] For every script with a `$S/<script>` entry in SKILL.md's script reference, a suite fails naming the script and the flag when that script's usage line names a `--` flag the entry's synopsis does not, and the entries stale today are brought in line ⟦criterion 1⟧
- [ ] For every script with a `$S/<script>` entry in SKILL.md's script reference, the same suite fails naming the script and the verb when that script's usage line names a verb (a literal subcommand word, or one alternative of an `a|b|c` choice) the entry's synopsis does not, and the entries stale today are brought in line ⟦criterion 1⟧
- [ ] Watched red by deleting one flag from one entry: the suite was run with one flag removed from one SKILL.md entry, went red naming that script and flag, and went green again once restored ⟦human-owed⟧ ⟦criterion 1⟧
