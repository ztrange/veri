"""The regular expression that finds a JavaScript test's call (`it(`, `test(`, `.only`, `.skip`, `.each`)."""
CALL = r"\b(?:it|test)(?:\.(?:only|skip))?(?:\.each(?:\([^)]*\)|`[^`]*`))?\(\s*"

