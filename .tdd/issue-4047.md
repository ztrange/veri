# Plan for #4047 — PRD 025.7: every knob is in TUNABLES

- [ ] VERI_MISSING_REROUTE_BUDGET, VERI_TEST_LOCK, VERI_PYTEST_WORKERS, VERI_PYTEST_LEGS, VERI_PYCACHE and VERI_NEW_SKILL are keys of TUNABLES, each with the default its reader used when unset ⟦criterion 2⟧
- [ ] the other names an operator sets that are read outside TUNABLES (VERI_PARALLEL, VERI_RUN_TIMEOUT, VERI_MAX_ISSUES, VERI_SELF_UPDATE, VERI_MUTATION_ADDRESS_DOMAIN, VERI_SESSION_TRANSCRIPTS, VERI_HOME) are keys of TUNABLES, each with the default its reader used when unset
- [ ] a unit case fails naming any name passed to tunables.read, read_bytes or pop in veri/ that is a key of neither TUNABLES nor the new NOT_KNOBS, whose values are `run state` or `test stand-in` ⟦criterion 1⟧
- [ ] unreachable.sh counts a read through the tunables module as a read: no `promised-unread: VERI_NO_VERDICT_RETRIES`, while a promised name nothing reads is still printed ⟦criterion 4⟧
