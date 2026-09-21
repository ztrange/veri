# Plan for #384 — dashboard: the Chatter pane is blank for every verifier leaf and for every finished leaf

- [x] While the run's current leaf is a verifier, /api/chatter renders that verifier's transcript rather than the empty string ⟦criterion 1⟧
- [x] A leaf transcript carrying the plain-text result appended after its stream-json records renders that transcript, rather than the empty string ⟦criterion 2⟧
- [x] A run on no leaf, and a leaf that has written nothing yet, each still answer {"chatter": ""} ⟦criterion 3⟧
- [ ] render-leaf-log.sh's header states what the script actually does with a line that is not JSON
