def fenced_lines(text):
    inside = False
    flags = []
    for line in text.splitlines():
        marker = line.startswith(("```", "~~~"))
        flags.append(inside or marker)
        if marker:
            inside = not inside
    return flags
