### affected_suites.py: a fence closes only at a line of the same fence character at least as long as its opener, so an edit below a ```` fence holding a ``` line and a `## x` line is attributed to the real enclosing section, not to `## x` ⟦criterion 1⟧
- out-of-scope | share one fence-tracking helper between skill_sections.py and affected_suites.py, which carry near-identical fence logic (a helper that tests can't be edited by Green, and #1021 owns it)
### affected_suites.py: a ``` or ~~~ line indented four or more spaces neither opens nor closes a fence, so a heading after such a line is still read as a heading ⟦criterion 2⟧
- out-of-scope | `skill_sections.py` fence logic duplicates `affected_suites.unfenced`, so the two could share one helper (cross-module, owned by #1021)
