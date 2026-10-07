"""The reader of KEY: value lines off a leaf report."""


def report_read(text, keys, *, optional_space=False, terminated_only=False):
    fields = {}
    lines = text.replace("\0", "").split("\n")
    if terminated_only:
        lines.pop()
    for line in lines:
        for key in keys:
            if not line.startswith(key + ":"):
                continue
            value = line[len(key) + 1:]
            if value.startswith(" "):
                fields[key] = value[1:]
                break
            if optional_space:
                fields[key] = value
                break
    return fields
