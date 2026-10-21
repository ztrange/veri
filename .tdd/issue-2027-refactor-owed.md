### `tick-issue-criterion.sh` ticks a box under `## Acceptance criteria` that follows a fenced block holding a line starting `# ` or `## `: a heading-like line inside a fence does not end the section ⟦criterion 3⟧
- share one fence-tracking helper between find_section_start and find_section_end (would change `~~~` and indented-fence handling in the end scan, so it is not behaviour-preserving)
