### run_cli answers exit code 0 when a throwaway module's main returns None, raises SystemExit with no code, or raises SystemExit(None) ⟦criterion 1⟧
- test-only | the pytester plant in test_run_cli.py keeps its own `planted(source)` copy of the module_of shape inside a source string; it cannot import the outer helper without changing what the plant proves
