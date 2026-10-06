# Plan for #1014 — Some prompt partials from #703 start or end mid-sentence

- [x] No partial under the prompt templates starts mid-sentence: every `_*.md` partial in `skills/tdd/scripts/prompts/` opens at the start of a sentence, a heading, a list item or a code block, never inside a clause that a template's text before the `{{INCLUDE:…}}` began, and the prompts that include it render the same text ⟦criterion 1⟧ ⟂ refactor pending
- [ ] No partial under the prompt templates ends mid-sentence: every `_*.md` partial in `skills/tdd/scripts/prompts/` closes at the end of a sentence, a heading, a list item or a code block, never inside a clause that a template's text after the `{{INCLUDE:…}}` finishes, and the prompts that include it render the same text ⟦criterion 1⟧
- [ ] Every prompt builder renders the same text as before the branch: byte-identical, or different only in whitespace from rewrapping, across the same builder runs #703 used ⟦diff-checked⟧ ⟦criterion 2⟧
