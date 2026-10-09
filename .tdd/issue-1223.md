# Plan for #1223 — Verifier prompts carry #1174's rule: signal only processes you started, never kill by pattern

- [ ] Every verifier prompt build-verify-prompt.sh produces, for every phase it accepts, states the rule the develop prompts state — signal only processes you started, by the pid you recorded, never by name or pattern (pkill, killall, kill $(pgrep …)) — and both take it from one shared partial under prompts/ that each includes, so the rule's text is spelled in exactly one prompt file ⟦criterion 1⟧
