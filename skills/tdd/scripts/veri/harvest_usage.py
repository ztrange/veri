"""harvest-usage.sh's computations, run in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import json
import sys

import entry
import event
import leaf_role
import tunables
from leaf_log import plain, result_records


def closing_result(path):
    """The last {"type":"result", ...} record in the log at path, or None if it holds none."""
    with open(path) as lines:
        records = result_records(lines)
    return records[-1] if records else None


FIRST_TURN_KEYS = ("cache_creation_input_tokens", "cache_read_input_tokens", "input_tokens")


def first_turn_pairs(path):
    """The usage of the first assistant record carrying one in the log at path, as first_turn_<key>=<value> event
    fields; none when no assistant record carries a usage (a missing figure is unknown, not 0)."""
    with open(path) as lines:
        for line in lines:
            try:
                record = json.loads(line)
            except ValueError:
                continue
            if not isinstance(record, dict) or record.get("type") != "assistant":
                continue
            message = record.get("message")
            usage = message.get("usage") if isinstance(message, dict) else None
            if isinstance(usage, dict) and all(key in usage for key in FIRST_TURN_KEYS):
                return ["first_turn_%s=%s" % (key, usage[key]) for key in FIRST_TURN_KEYS]
    return []


def usage_pairs(record):
    """The eight numbers in one closing result record, as key=value event fields."""
    usage = record["usage"]
    pairs = []
    for key in ("duration_ms", "duration_api_ms", "num_turns"):
        pairs.append("%s=%s" % (key, record[key]))
    pairs.append("total_cost_usd=%s" % plain(record["total_cost_usd"]))
    for key in ("input_tokens", "output_tokens",
                "cache_read_input_tokens", "cache_creation_input_tokens"):
        pairs.append("%s=%s" % (key, usage[key]))
    models = record.get("modelUsage", {})
    pairs.append("model=%s" % ",".join(models))
    if "modelUsage" in record:
        pairs.append("model_usage=%s" % json.dumps(models, sort_keys=True))
    return pairs


def no_usage_event(name, why):
    print("harvest-usage.sh: %s — no usage event appended for %s" % (why, name), file=sys.stderr)


def harvest(name, env):
    """Append the usage event for leaf name, reading the leaf's environment from env; diagnostics go to stderr."""
    log = ".tdd/%s.log" % name
    try:
        record = closing_result(log)
        if record is None:
            no_usage_event(name, "no closing result record in %s" % log)
            return 3
        if "usage" not in record:
            no_usage_event(name, "the closing result record in %s carries no usage" % log)
            return 2
        pairs = usage_pairs(record) + first_turn_pairs(log)
    except UnicodeDecodeError:
        no_usage_event(name, "%s is not valid UTF-8" % log)
        return 2
    except IsADirectoryError:
        no_usage_event(name, "%s is a directory" % log)
        return 2
    except Exception:
        import traceback
        traceback.print_exc()
        return 1
    role = leaf_role.leaf_role(name)
    if role is None:
        return 2
    return entry.to_contract(event.mark("", event.context(dict(env, **role)), "usage", pairs + ["name=" + name]))


USAGE = "usage: harvest-usage.sh <leaf-name>"


def main(argv):
    if not argv or not argv[0]:
        print("usage: harvest-usage.sh <leaf-name>", file=sys.stderr)
        return 2
    return harvest(argv[0], tunables.environment())


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
