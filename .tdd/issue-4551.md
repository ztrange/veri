# Plan for #4551 — REVISE.md's green PASS branch runs seam-settle.sh green-half, which exits 2 since nothing ticks green after revise

- [ ] after a green `revise.sh` cycle that PASSed (green-half's wait record re-saved with `revised`, no step ticked), `seam-settle.sh <n> green-half` finishes Green 3 from that record (tick with `⟂ refactor pending`, commit), writes its record and exits 0 ⟦criterion 1⟧
