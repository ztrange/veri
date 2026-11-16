# Plan for #3246 — PRD 012.5c: veri reports what a reset really costs and the growth knob each role's measured cost calls for

- [x] reset-cost.sh dev prints one line per recorded reset: its local time, K from the requests after the clear through the one at recovered-at, and g from the recovery's baseline to the next reset ⟦criterion 1⟧
- [ ] reset-cost.sh conductor <n> prints one line per conductor-restart event: K the price of the relaunch's first request, g its mean growth per request ⟦criterion 2⟧
- [ ] after the per-reset lines it prints the medians of K and g, r and the optimum growth √(2·K·g / r) next to the knob's current value, and names its sources ⟦criterion 3⟧
- [ ] with no reset recorded it prints nothing and exits 3 ⟦criterion 4⟧
- [ ] an unreadable transcript or conductor log exits 2 naming it ⟦criterion 4⟧
- [ ] a role other than dev or conductor, a bad lane or a bad <n> exits 2 with a usage line ⟦criterion 4⟧
- [ ] SKILL catalogue SCRIPTS.md has the reset-cost.sh entry, graded by SC220 ⟦criterion 5⟧
