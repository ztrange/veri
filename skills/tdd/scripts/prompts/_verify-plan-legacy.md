This issue is a legacy issue: its spec carries a `## Legacy` section, so each step tagged with a
criterion surrounds one region of untested code with black-box tests driven through a seam, and
lists `⟦phases: seam,surround⟧`. A region is a file and a symbol or line range; a seam is a
command or callable outside the region that drives it without editing it, such as an entry-point
CLI, an exported function or an HTTP handler. Three more checks apply to those steps:

- REJECT a legacy step that names no region: no file with a symbol or line range.
- REJECT a legacy step that names no seam.
- REJECT a legacy step whose seam lies inside its own region: a test driving it would reach in
  rather than wrap the region from outside.
