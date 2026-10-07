"""The reader of KEY: value lines off a leaf report."""


def report_read(text, keys, *, optional_space=False):
    fields = {}
    for line in text.replace("\0", "").split("\n"):
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
