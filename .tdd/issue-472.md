# Plan for #472 — supervise.sh must not count a suspended machine as leaf silence

- [x] A leaf that is silent only across a simulated suspend longer than VERI_HEARTBEAT (injected clock: suspended time advances, awake time does not) is not killed for silence and finishes with its own exit code ⟦criterion 1⟧
- [x] With VERI_AWAKE_CLOCK unset, supervise.sh still measures awake time on a real clock that does not advance while the machine is suspended, on macOS and on Linux, so a run nobody configured does not count a suspend as leaf silence ⟦added⟧ ⟦criterion 1⟧
- [x] A leaf whose run spans a simulated suspend that would put wall time past VERI_TIMEOUT, while its awake time stays under it, is not killed for the timeout and finishes with its own exit code ⟦criterion 1⟧
- [x] A leaf silent while the machine is awake (injected clock, no suspend) is still killed as stuck once its awake silence passes VERI_HEARTBEAT, at the same threshold as today ⟦criterion 2⟧
- [x] A noisy leaf running while the machine is awake (injected clock, no suspend) is still killed once its awake run time passes VERI_TIMEOUT, at the same threshold as today ⟦criterion 2⟧
- [x] The injected clock a suite drives can simulate a suspend with no real sleep and no real suspend, and the two suspend cases (heartbeat and timeout) run on it, each having been watched failing against the pre-fix supervisor ⟦criterion 3⟧
- [x] supervise.sh's header names the clock source the watchdog measures with and states why it pauses while the machine is suspended, for macOS and for Linux ⟦criterion 4⟧
