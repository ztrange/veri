"""The one scan for the result records of a leaf's stream-json log, and the text its dollar figures are written in."""
import decimal
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


def result_text(line):
    """The result string of the result record on one log line (str or bytes), else None."""
    try:
        obj = json.loads(line)
    except ValueError:
        return None
    if isinstance(obj, dict) and obj.get("type") == "result" and isinstance(obj.get("result"), str):
        return obj["result"]
    return None


def result_texts(lines):
    """The result string of every result record among `lines` that has one, in log order."""
    texts = (result_text(line) for line in lines)
    return [text for text in texts if text is not None]


def last_result_text(lines):
    """The final result string among `lines`, None when no result record has one."""
    texts = result_texts(lines)
    return texts[-1] if texts else None


def cost(lines):
    """Dollars: total_cost_usd summed over the result records among `lines` that carry a result field."""
    return sum(float(r.get("total_cost_usd") or 0) for r in result_records(lines) if "result" in r)


def plain(number):
    """The number as Python prints it, unless that is in exponent form (1e-05): then as a plain decimal (0.00001)."""
    text = str(number)
    return format(decimal.Decimal(text), "f") if isinstance(number, float) and "e" in text else text
