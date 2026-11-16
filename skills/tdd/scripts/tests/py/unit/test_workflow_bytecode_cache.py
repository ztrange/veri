"""ci.yml's gates job restores the bytecode cache the last push to main saved, read as text the way Actions reads it."""
import re

from conftest import ROOT

CI_YML = ROOT / ".github/workflows/ci.yml"


def gates():
    """The gates job's lines, from `  gates:` to the next job or the end."""
    lines, inside = [], False
    for line in CI_YML.read_text().split("\n"):
        if not inside:
            inside = line == "  gates:"
        elif re.match(r"  [^ ]", line):
            break
        else:
            lines.append(line)
    return lines


def unquoted(value):
    return value[1:-1] if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"" else value


def steps(job):
    """Each step of <job> as {key: value} for its top-level keys and its `with:` keys, comments dropped."""
    found, current = [], None
    for line in job:
        text = line.split(" #", 1)[0].rstrip() if not line.lstrip().startswith("#") else ""
        item = re.match(r"      - (\S[^:]*):\s*(.*)$", text)
        if item:
            current = {item.group(1): unquoted(item.group(2))}
            found.append(current)
            continue
        field = re.match(r"        (?:  )?([A-Za-z_-]+):\s*(.*)$", text)
        if current is not None and field:
            current[field.group(1)] = unquoted(field.group(2))
    return found


def job_env(job):
    env, inside = {}, False
    for line in job:
        if line == "    env:":
            inside = True
        elif inside and re.match(r"      ([A-Z_]+):\s*(.*)$", line):
            name, value = re.match(r"      ([A-Z_]+):\s*(.*)$", line).groups()
            env[name] = unquoted(value.split(" #", 1)[0].strip())
        elif inside:
            inside = False
    return env


def where(found, test):
    return next((i for i, step in enumerate(found) if test(step)), None)


def test_the_gates_job_stamps_mtimes_restores_a_fixed_pycache_before_make_test_and_saves_it_only_on_a_push_to_main_3922():
    job = gates()
    found = steps(job)
    pycache = job_env(job).get("VERI_PYCACHE", "")
    checkout = where(found, lambda s: s.get("uses", "").startswith("actions/checkout@"))
    stamp = where(found, lambda s: "skills/tdd/scripts/veri/content_mtimes.py" in s.get("run", ""))
    make_test = where(found, lambda s: s.get("run") == "make test")
    restore = where(found, lambda s: s.get("uses", "").startswith("actions/cache/restore@"))
    save = where(found, lambda s: s.get("uses", "").startswith("actions/cache/save@"))
    restored, saved = (found[restore] if restore is not None else {}), (found[save] if save is not None else {})
    key, fallback = restored.get("key", ""), restored.get("restore-keys", "")

    assert {
        "stamped after checkout, before make test": None not in (checkout, stamp, make_test) and checkout < stamp < make_test,
        "VERI_PYCACHE one fixed absolute path": pycache.startswith("/") and "${{" not in pycache,
        "restored before make test": None not in (restore, make_test) and restore < make_test,
        "restore and save name that path": restored.get("path") == saved.get("path") == pycache,
        "key names the runner OS and the Python version": "runner.os" in key and "python-version" in key,
        "falls back to the newest under that prefix": bool(fallback) and key.startswith(fallback) and fallback != key,
        "saved after make test under the same key": None not in (save, make_test) and save > make_test and saved.get("key") == key,
        "saved only on a push to main": re.fullmatch(
            r"github\.event_name == 'push' && github\.ref == 'refs/heads/main'", saved.get("if", "")) is not None,
        "no step both restores and saves": not any(s.get("uses", "").startswith("actions/cache@") for s in found),
    } == dict.fromkeys([
        "stamped after checkout, before make test", "VERI_PYCACHE one fixed absolute path", "restored before make test",
        "restore and save name that path", "key names the runner OS and the Python version",
        "falls back to the newest under that prefix", "saved after make test under the same key", "saved only on a push to main",
        "no step both restores and saves"], True)
