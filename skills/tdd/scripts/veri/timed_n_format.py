"""The `<n> until <ISO-8601 datetime>` text a timed-n line carries."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
from datetime import datetime


def parse(text):
    value, _, expiry = text.partition(" until ")
    return int(value), datetime.fromisoformat(expiry).timestamp()
