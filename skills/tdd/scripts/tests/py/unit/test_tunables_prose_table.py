"""veri/README.md's `## tunables` section holds one table row per key of tunables.TUNABLES (PRD 025.18)."""
import importlib
import pathlib
import re

README = pathlib.Path(__file__).resolve().parents[3] / "veri" / "README.md"
ROW = re.compile(r"^\| `([A-Z_0-9]+)` \| ([^|]*) \| ([^|]*) \|$", re.M)


def section(text):
    return text.split("\n## tunables\n", 1)[1].split("\n## ", 1)[0]


def rows(text):
    """{name: (default, refusal)} for each table row of the `## tunables` section of `text`."""
    return {name: (default.strip(), refusal.strip()) for name, default, refusal in ROW.findall(section(text))}


def drift(text, table):
    """[(name, why)] for each key of `table` with no row and each row naming no key."""
    found = rows(text)
    return sorted([(name, "no row") for name in table if name not in found]
                  + [(name, "names no key") for name in found if name not in table])


def test_4053_the_readme_tunables_table_has_one_row_per_key_of_tunables_and_no_other():
    tunables = importlib.import_module("veri.tunables")

    assert drift(README.read_text(), tunables.TUNABLES) == []


def test_4053_a_key_with_no_row_and_a_row_naming_no_key_are_each_named():
    text = "# x\n\n## tunables\n| `VERI_A` | `1` | its readers' own words |\n| `VERI_GONE` | `2` | x |\n\n## next\n"

    assert drift(text, {"VERI_A": None, "VERI_B": None}) == [("VERI_B", "no row"), ("VERI_GONE", "names no key")]
