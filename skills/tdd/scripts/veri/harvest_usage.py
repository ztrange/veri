"""harvest-usage.sh's computations, run in-process."""
import json
import re
import sys
import traceback

import event
import tunables
from leaf_log import result_records

WANT = "develop-*|revise-*|verify-*|conductor-*"
ACTORS = {"develop": "developer", "revise": "developer", "verify": "verifier", "grade": "grader", "conductor": "conductor"}


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


def leaf_role(name):
    """VERI_ACTOR, VERI_PHASE and VERI_ATTEMPT for a leaf name, or None after a diagnostic on stderr."""
    actor_word = name.split("-", 1)[0]
    actor = ACTORS.get(actor_word)
    if actor is None:
        print("leaf-role: leaf name '%s' has an unknown leading word (want %s)" % (name, WANT), file=sys.stderr)
        return None
    phase_attempt = name[len(actor_word) + 1:]
    if not phase_attempt:
        print("leaf-role: leaf name '%s' says no phase (want %s)" % (name, WANT), file=sys.stderr)
        return None
    numbered = re.fullmatch(r"(.*)-([0-9]+)", phase_attempt)
    phase, attempt = numbered.groups() if numbered else (phase_attempt, "1")
    return {"VERI_ACTOR": actor, "VERI_PHASE": phase, "VERI_ATTEMPT": attempt}


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
    role = leaf_role(name)
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
