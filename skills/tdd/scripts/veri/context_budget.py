"""The conductor context-budget rule, shared by orchestrate.py and parallel_conductors.py."""
import re

CACHE_READ = re.compile(rb'"cache_read_input_tokens":([0-9]+)')
CACHE_CREATION = re.compile(rb'"cache_creation_input_tokens":([0-9]+)')

START = (0, False)


def watch(state, lines, budget):
    """Return (state, readings, exceeded) after lines, stopping at the line that exceeds budget."""
    context, armed = state
    readings = []
    for line in lines:
        if armed and b'"type":"user"' in line:
            armed = False
            if context > budget:
                return (context, armed), readings, True
        if b'"type":"assistant"' not in line:
            continue
        cache_read = CACHE_READ.search(line)
        cache_creation = CACHE_CREATION.search(line) if cache_read else None
        if cache_creation:
            context = int(cache_read.group(1)) + int(cache_creation.group(1))
            readings.append(context)
        if b"event.sh step-done" in line:
            armed = True
    return (context, armed), readings, False
