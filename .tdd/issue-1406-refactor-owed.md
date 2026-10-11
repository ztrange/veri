### A conductor-run check, given a `⟦replaces-case⟧` step's text, exits 0 when every case the step names is gone from its suite, and exits 1 naming each named case still present ⟦criterion 3⟧
- test-only | the two cases both build the same tmp_path suite file and step prefix; a shared helper could remove that setup
