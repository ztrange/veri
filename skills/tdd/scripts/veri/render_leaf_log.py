"""render-leaf-log.sh's rendering of a leaf's stream-json log, run in-process."""
import json
import sys


def first_line(text):
    return (text.splitlines() or [""])[0]


def truncated(text, limit):
    head = first_line(text)
    cut = len(text.splitlines()) > 1 or len(head) > limit
    return head[:limit] + ("…" if cut else "")


def main(argv):
    out = []
    for line in sys.stdin:
        try:
            obj = json.loads(line)
        except ValueError:
            sys.stderr.write("render-leaf-log.sh: not JSON: %s" % line)
            return 2
        content = (obj.get("message") or {}).get("content") or []
        for block in content:
            kind = block.get("type")
            if kind == "text":
                out.append(block["text"])
            elif kind == "tool_use":
                values = list(block.get("input", {}).values())
                arg = first_line(str(values[0])) if values else ""
                out.append("> %s: %s" % (block["name"], arg))
            elif kind == "tool_result":
                out.append("< " + truncated(str(block.get("content", "")), 80))
    sys.stdout.write("".join(l + "\n" for l in out))
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
