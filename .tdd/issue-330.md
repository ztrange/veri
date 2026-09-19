# Plan for #330 — dashboard.test.sh calls the endpoint functions directly instead of starting a server for every case

- [x] The dashboard's python server lives in a module file beside dashboard.sh that dashboard.sh execs; importing it and calling runs_json, metrics_json or events_json never binds a port — a case imports it, calls a function, then confirms the default port 8765 is still free ⟦criterion 1⟧
- [ ] /api/runs's payload is asserted by calling runs_json directly against a fixture repo, byte-identical to status.sh --json on the same fixture, with no HTTP request and no server process for that case ⟦criterion 2⟧
- [ ] /api/metrics's payload is asserted by calling metrics_json directly — recomputed live for a running run, and the committed .tdd/issue-<n>-metrics.md verbatim for a finished one — with no server for that case ⟦criterion 3⟧
- [ ] /api/events's payload is asserted by calling events_json directly, including the empty list for an issue no run holds a ledger for, with no server for that case ⟦criterion 4⟧
- [ ] The static-HTML polling contract (the page polls all 3 endpoints every 2 s) is asserted by reading dashboard.html directly off disk, with no server started for that case ⟦criterion 5⟧
- [ ] At most 2 dashboard.sh server processes are started across the whole dashboard suite, counted deterministically by a PATH-first counting shim or a bind marker file, never by wall clock ⟦criterion 6⟧
- [ ] The remaining server-dependent cases together assert: default port 8765 with no argument; an explicit port argument bound instead; loopback only, unreachable from a non-loopback attempt; clean exit 0 on SIGINT; one server process answering more than one request across its life ⟦criterion 7⟧
- [ ] Every assertion dashboard.test.sh made before this issue is still made by some case afterwards, and make test is green ⟦criterion 8⟧
