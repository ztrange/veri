"""The reader of KEY: value lines off a leaf report."""


def report_read(text, keys):
    fields = {}
    for line in text.split("\n"):
        for key in keys:
            if line.startswith(key + ": "):
                fields[key] = line[len(key) + 2:]
                break
    return fields
