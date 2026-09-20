# Plan for #255 — Dashboard, part 2: the stream-json renderer, and the Tests and Chatter panes

- [x] The renderer, fed a captured leaf log fixture, prints assistant text, each tool call's name and first input line, and a truncated tool result, one per line ⟦criterion 1⟧
- [x] The renderer exits 2 on a line that is not JSON ⟦criterion 1⟧
- [ ] The Tests endpoint lists the selected run's leaf test runs — command, pass/fail from the tool result's exit status, output tail — extracted from fixture leaf logs ⟦criterion 2⟧
- [ ] The Tests endpoint never executes a suite: a test command whose execution would leave a trace leaves none when the endpoint is queried ⟦criterion 2⟧
- [ ] The Chatter endpoint returns the rendered log of the leaf the selected run is currently on ⟦criterion 3⟧
- [ ] A fixture run whose current leaf changes switches the Chatter endpoint to the new leaf ⟦criterion 3⟧
- [ ] The served page has Tests and Chatter panes, each scheduling its next request only from the settlement of its previous one, like the existing panes
