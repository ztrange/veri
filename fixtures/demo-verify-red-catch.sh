#!/usr/bin/env bash
# demo-verify-red-catch.sh — show the blind verifier catching a deliberately weak test.
#
# This is the slice-3 demo (issue #3, "Demoable: a deliberately weak/wrong test is caught
# by verify-red"). It does NOT need GitHub: it stands up a throwaway copy of the demo
# project, drops in a test that *pretends* to pin the slugify criterion but is trivial
# (it asserts a constant and never calls slugify), then runs the real blind verifier
# against it. A correct verifier REJECTs it.
#
# It makes a real `claude -p` model call (the verifier leaf), so it needs an authenticated
# `claude`. Override the binary with CLAUDE_BIN for a dry run.
#
# Usage:  fixtures/demo-verify-red-catch.sh
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$HERE/.." && pwd)"
S="$REPO/skills/tdd/scripts"

work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
cp -r "$REPO/fixtures/demo-project/." "$work/"

# The behavior spec the blind verifier is allowed to see (mirrors the seeded issue).
cat > "$work/spec.md" <<'SPEC'
## What to build

Add a `slugify(text)` function to the `slugify` package that turns an arbitrary string
into a URL-friendly slug: lowercase the text, replace any run of non-alphanumeric
characters with a single hyphen, and strip leading/trailing hyphens.

## Acceptance criteria

- [ ] `slugify("Hello, World!")` returns `"hello-world"`
SPEC

# A deliberately WEAK "Red" test: it claims to test slugify but asserts a constant and
# never imports or calls the function. It cannot fail for the right reason — verify-red
# should REJECT it (trivial / does not pin the behavior / does not even fail).
cat > "$work/tests/test_slugify_weak.py" <<'WEAK'
import unittest


class SlugifyTest(unittest.TestCase):
    def test_slugify_hello_world(self):
        # Looks like it pins the criterion, but it asserts a constant and never
        # calls slugify(...). A genuine Red test must fail because the behavior is
        # missing; this one passes vacuously.
        self.assertEqual("hello-world", "hello-world")


if __name__ == "__main__":
    unittest.main()
WEAK

echo ">> Running blind verify-red against the weak test (real claude -p leaf)..."
echo

set +e
( cd "$work" && "$S/verify.sh" red "$work/spec.md" tests/test_slugify_weak.py test_slugify_hello_world )
code=$?
set -e

echo
case "$code" in
  1) echo "✅ REJECT (exit 1) — the blind verifier caught the weak test, as designed." ;;
  0) echo "❌ PASS (exit 0) — the verifier failed to catch a weak test. Investigate." ;;
  2) echo "⚠️  malformed (exit 2) — the verifier leaf produced no parseable verdict." ;;
  *) echo "⚠️  unexpected exit $code." ;;
esac
exit "$code"
