# Plan for #300 — supervise.test.sh case 4 fails about 1 run in 10, blocking preflight at random

- [ ] A slow-but-alive leaf's heartbeat premise never depends on real elapsed time: every silence supervise.test.sh puts in front of the supervisor is injected onto its clock, so a scheduling delay near a whole-second boundary cannot be read as a stall ⟦criterion 1⟧
- [ ] A case in supervise.test.sh that reaches its silence by real waiting rather than by an injected clock jump fails the run, named, against an exemption table carrying a reason for each deliberate real-clock dependence ⟦criterion 3⟧
