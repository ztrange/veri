def _run(line):
    indent = len(line) - len(line.lstrip(" "))
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


def _level(line):
    hashes = len(line) - len(line.lstrip("#"))
    if hashes and line[hashes:hashes + 1] == " ":
        return hashes
    return 0


def section(text, heading):
    lines = text.splitlines()
    fenced = fenced_lines(text)
    start = next(i for i, line in enumerate(lines) if line == heading and not fenced[i])
    level = _level(heading)
    end = len(lines)
    for i in range(start + 1, len(lines)):
        if not fenced[i] and 0 < _level(lines[i]) <= level:
            end = i
            break
    return lines[start:end]
