# Plan for #4154 — PRD 033.1a: github-status.sh says whether GitHub has an incident on what veri needs

- [x] with no argument reads `<VERI_GITHUB_STATUS_URL>/api/v2/incidents/unresolved.json` and matches the five default components; with arguments, those only ⟦criterion 1⟧
- [x] an incident opened exactly `VERI_GITHUB_OUTAGE_MIN` minutes ago counts whatever its impact and status; one a minute younger does not ⟦criterion 2⟧
- [ ] two counting incidents exit 1 with one tab-separated line each: name, matched components, local start, age in minutes ⟦criterion 3⟧
- [ ] no incident naming a component exits 0 printing `up`; only young ones exit 0 printing `young <minutes> <name>` each ⟦criterion 4⟧
- [ ] an incident with empty or absent `components` never counts ⟦criterion 5⟧
- [ ] no response within `VERI_GITHUB_STATUS_TIMEOUT`, a non-200 status, a body not in the feed's shape, or an unparseable `created_at` exits 2 naming the cause ⟦criterion 6⟧
- [ ] a `VERI_GITHUB_OUTAGE_MIN` or `VERI_GITHUB_STATUS_TIMEOUT` that is not a positive integer exits 2 naming it before any fetch ⟦criterion 7⟧
- [ ] a component argument not among GitHub's component names exits 2 naming it and listing them, before any fetch ⟦criterion 8⟧
- [ ] the three tunables are `TUNABLES` keys with their rows in veri/README.md's table ⟦criterion 9⟧
- [ ] `github-status.sh` is a `/bin/sh` shim over `veri/github_status.py`, answering `--help` ⟦criterion 10⟧
- [ ] SCRIPTS.md catalogues `$S/github-status.sh [<component>…]`, graded ⟦criterion 11⟧
