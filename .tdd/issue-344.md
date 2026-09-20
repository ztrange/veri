# Plan for #344 — dashboard.html polls on a fixed 2 s clock against a one-request-at-a-time server, so a slow endpoint starves every pane

- [x] dashboard.html schedules each pane's next request only from the previous request's settlement — both the resolve and the reject path — and carries no setInterval anywhere on the page ⟦criterion 1⟧ ⟂ refactor pending
- [ ] the server answers /api/events while a /api/runs request is still blocked inside status.sh, asserted by ordering rather than by elapsed time ⟦criterion 2⟧
