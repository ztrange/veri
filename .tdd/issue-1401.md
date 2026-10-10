# Plan for #1401 — run_cli lets an uncaught exception propagate where the shim exits 2

- [x] run_cli over a throwaway module whose main raises an uncaught exception (not SystemExit) gives exit 2 and exactly the one stderr line `<script>.sh: <Type>: <reason>` that entry.run(main, argv) gives a shell caller ⟦criterion 1⟧
- [ ] run_cli over a throwaway module whose main returns a string gives exit 1 and that string on stderr, as entry.run(main, argv) does ⟦criterion 1⟧
- [ ] run_cli over a throwaway module whose main raises BrokenPipeError gives exit 141, as entry.run(main, argv) does ⟦criterion 1⟧
