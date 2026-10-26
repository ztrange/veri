"""render-leaf-log.sh's rendering of a leaf's stream-json log, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import io
import json
import sys


def first_line(text):
    return (text.splitlines() or [""])[0]


def truncated(text, limit):
    head = first_line(text)
    cut = len(text.splitlines()) > 1 or len(head) > limit
    return head[:limit] + ("…" if cut else "")


def _render(lines):
    out = []
    for line in lines:
        try:
            obj = json.loads(line)
        except ValueError:
            return 2, "", "render-leaf-log.sh: not JSON: %s" % line
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
    return 0, "".join(l + "\n" for l in out), ""


def render_log(text):
    try:
        code, rendering, _ = _render(io.StringIO(text))
    except Exception:
        return 2, ""
    return code, rendering


def main(argv):
    code, rendering, err = _render(sys.stdin)
    sys.stderr.write(err)
    sys.stdout.write(rendering)
    return code


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
