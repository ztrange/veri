"""The seam contracts of the fused stages (PRD 038.1 SC5): per stage that writes a record, the keys the next stage reads
from it that no committed fact holds, and which record each reading stage reads. One table, the one place a stage
done by hand learns what it owes `seam-settle.sh`."""

# A record-writing stage -> the keys of its record the next stage reads that have no committed source.
CONTRACTS = {"red-half": ("test_path", "target_test"), "green-half": ("test_path",), "refactor-half": ()}

# A reading stage -> the stage whose record it reads.
READS = {"green-half": "red-half", "refactor-half": "green-half", "step-close": "refactor-half"}


def table():
    """The contracts as script-help.sh seam-settle.sh prints them: one `<stage>: <keys>` line per record stage."""
    return "Seam contracts (stage: the keys seam-settle.sh takes for it):\n" + "".join(
        "%s: %s\n" % (stage, " ".join(keys) or "(none)") for stage, keys in CONTRACTS.items())
