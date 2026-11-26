### The smell catalogue (`skills/tdd/SMELLS.md`)

The one standard a refactor is held to: the developer tidies to it and the verifier judges by it.
A smell is met only where the code meets its threshold as written; where no smell is met, nothing
is owed. Name a smell and a refactoring exactly as this table spells them.

| Smell | Met when | Refactorings that answer it |
|---|---|---|
| Duplicated Code | the same 3 or more consecutive lines, ignoring whitespace and names, appear in 2 or more places | Extract Function, Slide Statements, Pull Up Method |
| Long Function | a function or method body is longer than 30 lines, blank and comment lines not counted | Extract Function, Decompose Conditional, Replace Temp with Query |
| Deep Nesting | a statement sits more than 3 blocks deep inside a function body | Replace Nested Conditional with Guard Clauses, Extract Function |
| Long Parameter List | a function takes more than 4 parameters | Introduce Parameter Object, Preserve Whole Object |
| Flag Argument | a boolean parameter whose value picks between two paths through the function | Remove Flag Argument |
| Large Module | a source file is longer than 400 lines | Extract Class, Move Function |
| Repeated Switch | the same condition chain on the same value appears in 2 or more places | Replace Conditional with Polymorphism, Extract Function |
| Data Clumps | the same 3 or more parameters or fields travel together in 2 or more signatures | Introduce Parameter Object, Extract Class |
| Magic Literal | the same string or number, other than 0 and 1, is written out in 3 or more places | Replace Magic Literal |
| Message Chain | a chain of more than 3 calls or field reads through other objects, as `a.b().c().d().e()` | Hide Delegate, Extract Function |
| Feature Envy | a function reads 3 or more fields of another module's object and none of its own | Move Function |
| Mysterious Name | a name says something its code does not do | Rename Variable, Change Function Declaration, Rename Field |
| Leaky Scope | a module-level name is used by 1 function only, or a variable lives wider than its uses | Move Statements into Function, Encapsulate Variable |
| Dead Code | a function, branch, parameter or import no code path reaches | Remove Dead Code |
| Speculative Generality | a parameter, option, hook or abstraction no test exercises | Inline Function, Remove Dead Code |
| Sibling Asymmetry | 1 function or stage in a family of 3 or more siblings skips a step all the others take | Extract Function |

Extract Function answers Sibling Asymmetry only where behaviour is unchanged. Otherwise report it
as an `uncovered-spec` flag; no transform ever fixes it.

#### Rules every transform keeps

1. **Search for an existing helper before adding one.** A function that already does the job is
   called, never written a second time beside it.
2. **Do not reverse a refactor made earlier in the same run.** A transform that undoes one the run
   already made (inlines what it extracted, renames back what it renamed) is not applied.
3. **One transform, one named refactoring.** Each transform applies one refactoring of the table
   above, called by its name.

#### Rules for test code

1. **Expected values stay literal.** In a test, an expected value is written out, never computed
   by the code under test.
2. **An assertion is never loosened by a tidy-up.** An assertion line may move into a helper only
   unchanged, modulo whitespace.
