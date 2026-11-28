# Plan for #4870 — tests-frozen.sh refuses a describe-nested Vitest red case: recorded id 'file::describe > it' reported as no longer existing

- [x] record --red-case '<file>::<describe> > <it title>' for an it nested in that describe exits 0 and writes the record ⟦criterion 1⟧
- [x] record --red-case resolves two nested describes '<a> > <b> > <it title>' ⟦criterion 2⟧
- [ ] record --red-case resolves an it title holding ' > ' and '::', bare and describe-qualified ⟦criterion 3⟧
- [ ] record --red-case still exits 1 with 'no longer exists' for a describe-qualified id whose it title is absent ⟦criterion 4⟧
