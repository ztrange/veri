"""The reader of KEY: value lines off a leaf report."""


def report_read(text, keys, *, optional_space=False):
    fields = {}
    for line in text.replace("\0", "").split("\n"):
        for key in keys:
            if line.startswith(key + ": "):
                fields[key] = line[len(key) + 2:]
                break
            if optional_space and line.startswith(key + ":"):
                fields[key] = line[len(key) + 1:]
                break
    return fields
