# Plan for #1738 — The conductor inherits FORCE_PROMPT_CACHING_5M from the operator's shell and loses the 1-hour cache TTL

- [x] With FORCE_PROMPT_CACHING_5M set in the parent environment, the conductor run-conductor.sh launches does not see the variable, while a leaf launched under that same parent environment still gets FORCE_PROMPT_CACHING_5M=1 — pinned by a small pytest case that sets the variable in the parent environment rather than deleting it ⟦criterion 1⟧
