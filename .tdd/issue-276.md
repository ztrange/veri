# Plan for #276 — A leaf can change the operator's global git config

- [x] A leaf launched through run-leaf.sh that runs `git config --global <key> <value>` leaves the operator's global config byte-identical, and the leaf reads the value back ⟦criterion 1⟧
- [x] The leaf's private global config starts as a copy of the operator's, so a key already present there is visible to the leaf ⟦criterion 2⟧
- [x] verify.sh exits 2 naming the file when the operator's global git config changed between a verifier's launch and its exit ⟦criterion 3⟧
- [x] prompts/_shared.md forbids changing global or user-level configuration and names environment variables and throwaway directories as the way to simulate conditions ⟦criterion 4⟧
- [x] prompts/_develop-shared.md carries the same prohibition, so developer leaves — whose reach is the same — are told it too
