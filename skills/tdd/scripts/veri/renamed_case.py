"""Decides whether a pytest case was renamed: same text, another name on its def line."""
import re

DEF = re.compile(r"^([ \t]*)def[ \t]+(test_\w+)")


def case_texts(source):
    lines = source.splitlines()
    texts = {}
    for start, line in enumerate(lines):
        found = DEF.match(line)
        if not found:
            continue
        end = start + 1
        while end < len(lines) and (not lines[end].strip()
                                    or len(lines[end]) - len(lines[end].lstrip()) > len(found.group(1))):
            end += 1
        first = start
        while first and lines[first - 1].lstrip().startswith("@"):
            first -= 1
        texts[found.group(2)] = (line, "\n".join(lines[first:start] + lines[start + 1:end]).rstrip())
    return texts


def _counterpart(name, old_source, new_source, taken, same_body, record):
    old = case_texts(old_source).get(name)
    if old is None:
        return None
    for other, (head, body) in sorted(case_texts(new_source).items()):
        if other not in taken and (body == old[1]) == same_body \
                and head.replace(other, name, 1) == old[0]:
            if record:
                taken.add(other)
            return other
    return None


def renamed_to(name, old_source, new_source, taken):
    """The case of new_source, not in `taken`, whose text is old_source's `name` case but for its name."""
    return _counterpart(name, old_source, new_source, taken, True, True)


def renamed_and_changed_to(name, old_source, new_source, taken):
    """The case of new_source, not in `taken`, whose def line is old_source's `name` case's but for its name, body differing."""
    return _counterpart(name, old_source, new_source, taken, False, False)
