"""When a case in the current tree is "the same case" as one a frozen record names, and the digest of the helpers it calls.

"The same case" is decided by the record's body digest, never by position: a case is the one recorded when
its body (or one of its `parents[N]` root-lookup variants, for a file that moved to another depth) hashes to
a recorded digest. A case missing under its recorded name is the same case when it was only renamed (its
text unchanged but for the name, read off the file's history), and a file missing under its recorded name is
the same file when a visible copy elsewhere in the tree holds the case. The assertions a case leans on in
the helpers it calls are part of its identity: `helper_digest` is the digest of those assertion lines.

Interface (a function says what it touches: text only, the tree's files, or case_history):
  squeezed(text)                          `text` with every run of whitespace dropped. Text only.
  assertion_lines(body)                   the squeezed lines of `body` that start (after indentation) with
                                          assert, expect(, t.Fatal, t.Error, t.Fail or require. Text only.
  bodies_of(text, case)                   every body of the cases named `case` in test source `text`, in file
                                          order; [] when none. Text only; UnclosedCase from case_reader.cut_cases
                                          when a JS call never closes.
  helpers_in(text, body, legacy=False)    the definitions in `text` (python def, Go func, JS function or arrow
                                          const) that `body` calls by name, each from its head to the next
                                          column-0 definition keyword; a python `test*` def and a Go `Test*` func
                                          are never helpers. `legacy` ends a definition only at `func`, the
                                          formula older records were written with. "" when none. Text only.
  helper_digest(text, body, legacy=False) the body digest of the sorted assertion lines of helpers_in. Text only.
  root_variants(body)                     `body`, then `body` with each `parents[N]` rewritten to depth 0..9. Text only.
  as_recorded(body, digests)              the first of root_variants(body) whose digest is in `digests`, else
                                          `body`. Text only.

Error modes: none of these catches anything; they raise only what case_reader raises on an unclosed JS call.
"""
import re

from case_reader import cut_cases
from frozen_record import body_digest


def squeezed(text):
    return re.sub(r"\s+", "", text)


def assertion_lines(body):
    return [squeezed(line) for line in body.splitlines() if line.lstrip().startswith(("assert", "expect(", "t.Fatal", "t.Error", "t.Fail", "require."))]


def bodies_of(text, case):
    return [b for c, b in cut_cases(text) if c == case]


_HELPER_NAME = r"^(?:(?:function|func|def)\s+(\w+)|const\s+(\w+)\s*=\s*(?:async\s*)?(?:\([^)]*\)|\w+)\s*=>)"


def helpers_in(text, body, legacy=False):
    helpers = []
    stop = r"func" if legacy else r"(?:function|func|def|const)"
    rest = re.compile(r"(?:(?!%s\b).*\n?)*" % stop)
    for head in re.finditer(_HELPER_NAME + r"[^\n]*\n", text, re.M):
        definition = head.group() + rest.match(text, head.end()).group()
        name = head.group(1) or head.group(2)
        keyword = definition.split(None, 1)[0]
        collected = (keyword == "def" and name.startswith("test")) or (keyword == "func" and name.startswith("Test"))
        if not collected and re.search(r"\b%s\(" % name, body):
            helpers.append(definition)
    return "\n".join(helpers)


def helper_digest(text, body, legacy=False):
    return body_digest("\n".join(sorted(assertion_lines(helpers_in(text, body, legacy)))))


def root_variants(body):
    yield body
    for k in range(10):
        yield re.sub(r"parents\[\d+\]", "parents[%d]" % k, body)


def as_recorded(body, digests):
    return next((v for v in root_variants(body) if body_digest(v) in digests), body)
