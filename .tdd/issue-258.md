# Plan for #258 — run-conductor.test.sh cases 1-5 fetch this repo's real origin over the network

- [x] Cases 1–5 of run-conductor.test.sh pass with origin unreachable and regardless of what origin/main holds, because they launch from a fixture clone whose origin the case controls ⟦criterion 1⟧
- [x] No suite under skills/tdd/scripts/tests launches run-conductor.sh against this repository's own origin; every fetch-and-pin launch uses a fixture clone ⟦criterion 2⟧
- [x] make test passes with network fetches made unreachable for the duration of the run ⟦criterion 3⟧
