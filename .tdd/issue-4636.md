# Plan for #4636 — A vish lane agent ends its turn on a progress line or while a background child runs, and the lane stalls

- [x] `## Who does what` says a vish agent's turn ends only on its final report or a blocker, never on a progress line or on waiting for a child (VSH32) ⟦criterion 1⟧
- [x] `## Who does what` says every subagent (cycle agent, suite runner) and the CI watch run in the foreground (VSH31) ⟦criterion 2⟧
