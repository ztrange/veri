"""refresh-spec.sh's re-capture, built in-process."""
if __name__ == "__main__": __import__("runpy").run_path(__import__("sys").path[0] + "/pycache_prefix.py")
import sys

try:
    from capture_spec import capture
except ImportError:
    from .capture_spec import capture


def main(argv):
    live = capture(argv[0])
    with open(argv[1], "w") as f:
        f.write(live)
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
