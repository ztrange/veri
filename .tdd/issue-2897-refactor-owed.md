### The diff verifier's deleted-case guard refuses a step that deletes an `it("x", …)` case in a `.test.js` file which an earlier step of the branch added, with the existing refusal text unchanged ⟦criterion 2⟧
- replace the nested ternary and `go`/`js` flags in `pytest_cases` with a suffix-to-pattern table
applied | 3d805dec80a19bd42a9faf0bba6e4703ec59edd1 | replace the nested ternary and `go`/`js` flags in `pytest_cases` with a suffix-to-pattern table	refactor: pytest_cases picks its pattern from a suffix table (#2897)
