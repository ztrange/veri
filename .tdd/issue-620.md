# Plan for #620 — step-cost.sh never matches a step whose title contains a double quote

- [x] step-cost.sh given a step title containing a double quote (prints «ok» on success, with real double quotes) prints the sum of that step's usage events and exits 0 ⟦criterion 1⟧
- [x] step-cost.sh given a step title containing a backslash followed by a double quote (stored in JSON as an escaped backslash then an escaped quote) prints that step's sum and exits 0 ⟦criterion 2⟧
- [x] step-cost.sh given a step title ending in a backslash prints that step's sum and exits 0 ⟦criterion 3⟧
- [x] step-cost.sh --steps prints two separate rows, each with its own dollars and leaf count, for two steps whose titles are identical up to their first double quote ⟦criterion 4⟧
- [x] for every step in a log holding a quoted title, the figure step-cost.sh prints for that title equals the dollars on that step's --steps row ⟦criterion 5⟧
- [x] step-cost.sh --run sums events whose step titles contain double quotes, counting each event once ⟦criterion 6⟧
- [x] a title carrying an em dash and a double-bracketed criterion mark (stored as JSON unicode escapes, the #521 case) is still summed by step-cost.sh to the figure --steps prints for it ⟦criterion 7⟧
- [ ] step-cost.sh given a step no event carries still prints nothing and exits 3 ⟦criterion 8⟧
