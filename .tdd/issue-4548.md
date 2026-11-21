# Plan for #4548 — PIN.md asks for pin and retirement comments that no comment.sh kind posts

- [x] `comment.sh <n> pin` posts `### 📌 Already satisfied — <STEP>`, the last done step, carrying `.tdd/verify-pin.reason`, and records a `comment` event of kind `pin` ⟦criterion 1⟧
- [x] `comment.sh <n> pin` with `.tdd/verdict-pin.exit` reading `skipped` carries `verify-pin — SKIPPED (switched off)` in place of the reason
- [x] `comment.sh <n> retire` posts `### 🪦 Retired — <STEP>`, the last retired step, carrying `.tdd/verify-pin.reason`, and records a `comment` event of kind `retire` ⟦criterion 2⟧
- [x] `comment.sh <n> retire` with no retired step in the ledger exits 2 and posts nothing
- [x] PIN.md names `comment.sh <n> pin` and `comment.sh <n> retire`; SCRIPTS.md lists both kinds
