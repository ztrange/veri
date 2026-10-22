def _run(line):
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
