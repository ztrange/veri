"""The one scan for the result records of a leaf's stream-json log."""
import json


def result_records(lines):
    """Every {"type":"result", ...} record among `lines`, in log order."""
    records = []
    for line in lines:
        s = line.strip()
        if not s.startswith("{"):
            continue
        try:
            obj = json.loads(s)
        except ValueError:
            continue
        if isinstance(obj, dict) and obj.get("type") == "result":
            records.append(obj)
    return records
