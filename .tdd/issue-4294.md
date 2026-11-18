# Plan for #4294 — case_reader cuts a JS regex literal holding a paren or quote as a string, so valid test sources exit 2 with UnclosedCase

- [x] `cut_cases` cuts a case holding a regex literal with a paren (`const r = /\(/;`) at its own call's closing paren and returns every case ⟦criterion 1⟧
- [x] `cut_cases` still cuts a case holding a division (`a / b`, `f(x) / 2`, `arr[0] / 2`) and a `//` comment as before ⟦criterion 3⟧
- [ ] `cut_cases` returns every case when one holds a quote-bearing regex (`/'/`) returned by `return`, followed in the same case by a string holding `}` (`'a}'`), while an identifier merely ending in `return` still divides ⟦criterion 2⟧
- [ ] `cut_cases` reads an escaped slash inside a regex literal (`/\/(/`) as part of the regex, not its end
- [ ] `cut_cases` reads a slash inside a regex character class (`/[/(]/`) as part of the regex, not its end
- [ ] `cut_cases` reads a `/` with no closing slash on its own line (`n++ / 2`) as a division, not a regex
