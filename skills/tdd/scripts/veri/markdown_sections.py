def fenced_lines(text):
    opener = None
    flags = []
    for line in text.splitlines():
        marker = line[:3] if line.startswith(("```", "~~~")) else None
        flags.append(opener is not None or marker is not None)
        if opener is None:
            opener = marker
        elif marker == opener:
            opener = None
    return flags
