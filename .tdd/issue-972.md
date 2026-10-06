# Plan for #972 — flaky: supervise.test.sh's #472 awake-time case fails under full make test load (survived inside the timeout=no)

- [x] supervise.test.sh's #472 awake-runaway case still sees the leaf survive inside the 4s VERI_TIMEOUT and then get killed on the hard timeout when machine load stretches the real wall time between the leaf's injected clock jumps by several seconds ⟦criterion 1⟧
