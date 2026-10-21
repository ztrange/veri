"""harvest-usage.sh's computations, run in-process."""
import json
import sys
import traceback

import event
import tunables
import leaf_role
from leaf_log import result_records


def closing_result(path):
    """The last {"type":"result", ...} record in the log at path, or None if it holds none."""
    with open(path) as lines:
        records = result_records(lines)
    return records[-1] if records else None


def usage_pairs(record):
    """The eight numbers in one closing result record, as key=value event fields."""
    usage = record["usage"]
    pairs = []
    for key in ("duration_ms", "duration_api_ms", "num_turns", "total_cost_usd"):
        pairs.append("%s=%s" % (key, record[key]))
    for key in ("input_tokens", "output_tokens",
                "cache_read_input_tokens", "cache_creation_input_tokens"):
        pairs.append("%s=%s" % (key, usage[key]))
    models = record.get("modelUsage", {})
    pairs.append("model=%s" % ",".join(models))
    if "modelUsage" in record:
        pairs.append("model_usage=%s" % json.dumps(models, sort_keys=True))
    return pairs


def to_contract(code):
    return code if code in (0, 1, 2, 3) else 2


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
        pairs = usage_pairs(record)
    except UnicodeDecodeError:
        no_usage_event(name, "%s is not valid UTF-8" % log)
        return 2
    except IsADirectoryError:
        no_usage_event(name, "%s is a directory" % log)
        return 2
    except Exception:
        traceback.print_exc()
        return 1
    role = leaf_role.leaf_role(name)
    if role is None:
        return 2
    return to_contract(event.mark("", event.context(dict(env, **role)), "usage", pairs))


def main(argv):
    if not argv or not argv[0]:
        print("usage: harvest-usage.sh <leaf-name>", file=sys.stderr)
        return 2
    return harvest(argv[0], tunables.environment())


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
