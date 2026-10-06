"""tick-criterion.sh's transform, run in-process."""
import sys

import ledger


def main(argv):
    text = sys.stdin.buffer.read().decode()
    ticked, text = ledger.ledger_tick(text, argv[0] if argv else "")
    sys.stdout.buffer.write(text.encode())
    return 0 if ticked else 3


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
