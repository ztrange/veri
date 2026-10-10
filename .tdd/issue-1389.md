# Plan for #1389 — run_cli reports None where the shim exits 0, and a sys.exit message as the code

- [x] run_cli answers the integer itself as the exit code when a throwaway module's main returns an integer, and when it raises SystemExit carrying an integer ⟦criterion 1⟧
- [x] run_cli answers exit code 0 when a throwaway module's main returns None, raises SystemExit with no code, or raises SystemExit(None) ⟦criterion 1⟧
- [x] run_cli answers exit code 1 when a throwaway module's main raises SystemExit carrying a non-integer object such as a message string, and the captured stderr ends with that object's text followed by a newline ⟦criterion 1⟧
- [x] run_cli answers exit code 1 and writes the object's text followed by a newline to the captured stderr when main raises SystemExit carrying an object that is neither an integer nor a string, such as a float or a tuple ⟦added⟧ ⟦criterion 1⟧
- [x] CLAUDE.md's description of the run_cli fixture states that its exit code is the status the module's .sh entry point would exit with, replacing "takes a SystemExit's code as the exit code" ⟦diff-checked⟧
