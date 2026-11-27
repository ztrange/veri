"""The template mechanics the prompt builders share: reading a template, `{{INCLUDE:x}}` expansion, `{{X}}` filling.

A library module (no shim, no main). Everything is bytes: a template or spec is bytes, a path may be str or bytes.

- `read(path)`: the file's bytes with trailing newlines stripped; raises OSError when it cannot be read.
- `spec_text_of(path)`: `read(path)`, or `b""` when the file cannot be read.
- `has_heading(text, heading)`: bool, whether `## <heading>` (bytes) is a whole line of the bytes `text`.
- `IncludeRefused`: raised by `expand_includes`; `args[0]` is the stderr line, bytes, without its newline.
- `expand_includes(text, prompts, chain=())`: `text` (bytes) with every `{{INCLUDE:x}}` replaced by the expanded
  content of `<prompts>/x` (`prompts` bytes); raises `IncludeRefused` for a missing or unreadable partial and for one
  that includes itself. A partial that is a directory expands to nothing, after `cat: <path>: Is a directory` on stderr.
- `fill(text, pairs)`: `text` with each `{{NAME}}` replaced, pair by pair in order, from `pairs` of `(name bytes,
  value)`; a value is bytes, or a callable returning bytes that is called only when its placeholder is still in
  the text at its turn (and may raise `IncludeRefused`). A later pair therefore sees what an earlier value inserted.

The verifier's blindness checks are not here: they stay in `build_verify_prompt`, which decides what its prompt is built
from.
"""
import os
import re
import sys


def read(path):
    with open(path, "rb") as f:
        return f.read().rstrip(b"\n")


def spec_text_of(path):
    try:
        return read(path)
    except OSError:
        return b""


def has_heading(text, heading):
    return re.search(rb"^## " + heading + rb"[ \t\r\v\f]*$", text, re.M) is not None


class IncludeRefused(Exception):
    pass


def expand_includes(text, prompts, chain=()):
    out = b""
    while (match := re.search(rb"\{\{INCLUDE:([^}]*)\}\}", text)):
        part = prompts + b"/" + match[1]
        out += text[:match.start()]
        text = text[match.end():]
        if not os.access(part, os.R_OK):
            raise IncludeRefused(b"missing partial: " + part)
        if part in chain:
            raise IncludeRefused(b"partial includes itself: " + part)
        try:
            content = read(part)
        except IsADirectoryError:
            sys.stderr.buffer.write(b"cat: " + part + b": Is a directory\n")
            content = b""
        out += expand_includes(content, prompts, chain + (part,))
    return out + text


def fill(text, pairs):
    for name, value in pairs:
        placeholder = b"{{" + name + b"}}"
        if callable(value):
            if placeholder not in text:
                continue
            value = value()
        text = text.replace(placeholder, value)
    return text
