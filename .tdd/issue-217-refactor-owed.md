### orchestrate.sh exits 2 without launching any conductor when solvable-issues.sh exits with anything other than 0 or 3, since then no answer about the solvable set could be obtained ⟦added⟧ ⟦criterion 1⟧
- the call-counter-and-cap preamble (`calls=$(( … ))`, write back to `$SOLVABLE.calls`, exit 3 past a threshold) is repeated between the main solvable-issues.sh stub and case 2's broken stub; one shared stub body would remove it, but with only two copies it is marginal
### a conductor whose stream crosses VERI_CONDUCTOR_CTX_BUDGET mid-step is not stopped until a step-done is seen, and is stopped after it ⟦criterion 3⟧
- the first-incarnation guard `[ "$(wc -l < "$LAUNCHES")" -eq 1 ] || exit 0` is repeated in the stubs of cases 4–6 and could move into `conductor_stub`; I left it because that would change case 3's stub too
- the `export VERI_CONDUCTOR_CTX_BUDGET=100000` … `unset` wrapped around `orchestrate` in cases 4 and 6 could become an argument to `orchestrate`
