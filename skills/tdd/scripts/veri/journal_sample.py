"""The sample journal, fixtures/journal/sample.jsonl: one line per event veri/event_table.py declares, in its order.

Each line carries every key declared for its event, required and optional, built by `event.line`, the journal's own
line builder, from the table alone: every value is invented, fixed per format, so two runs print the same bytes.
Regenerate the file with `python3 skills/tdd/scripts/veri/journal_sample.py > fixtures/journal/sample.jsonl`.

Interface:
  sample()     the sample's bytes
  main(argv)   prints them on stdout; exit 0
"""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import sys

import event
import event_table

TS = 1767225600
AWAKE = b"86400"
VALUES = {"whole": "3", "decimal": "0.25", "url": "https://github.com/acme/widgets/pull/7",
          "sha": "0123456789abcdef0123456789abcdef01234567", "json": '{"claude-sonnet-5-5": {"inputTokens": 3}}',
          "text": "sample text"}


def value(event_name, key):
    form = event_table.format(event_name, key)[0]
    return form[0] if isinstance(form, tuple) else VALUES[form]


def sample():
    context = {key.encode(): value(None, key).encode() for key in event_table.CONTEXT_KEYS if key != "event"}
    return b"".join(event.line([name.encode()]
                               + [f"{key}={value(name, key)}".encode() for key in event_table.keys(name)],
                               context, TS, AWAKE) for name in event_table.EVENTS)


def main(argv):
    sys.stdout.buffer.write(sample())
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
