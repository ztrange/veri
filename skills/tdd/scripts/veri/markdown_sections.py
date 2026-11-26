"""Which lines of a Markdown text sit in a code fence."""
def _run(line):
    indent = len(line) - len(line.lstrip())
    if indent <= 3:
        line = line[indent:]
    if not line.startswith(("```", "~~~")):
        return None
    return line[0], len(line) - len(line.lstrip(line[0]))


def fenced_lines(text):
    opener = None
    flags = []
    for line in text.splitlines():
        run = _run(line)
        flags.append(opener is not None or run is not None)
        if opener is None:
            opener = run
        elif run is not None and run[0] == opener[0] and run[1] >= opener[1]:
            opener = None
    return flags



def unfenced(text):
    """[(index, line)] for each line of <text> (`str.splitlines`) outside a code fence: the one reading of a heading's
    lines that `record_answer` and `status` share, so a heading quoted in a fence is never one."""
    return [(i, line) for i, (line, fenced) in enumerate(zip(text.splitlines(), fenced_lines(text), strict=True)) if not fenced]
