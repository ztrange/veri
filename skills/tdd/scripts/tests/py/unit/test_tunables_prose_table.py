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
    """[(name, why)] for each key of `table` with no row, each row naming no key and each row whose default differs."""
    found = rows(text)
    stated = {name: "" if default == '""' else default.strip("`") for name, (default, _) in found.items()}
    return sorted([(name, "no row") for name in table if name not in found]
                  + [(name, "names no key") for name in found if name not in table]
                  + [(name, "default %s, not %s" % (stated[name], table[name].default))
                     for name in found if name in table and stated[name] != table[name].default])


def test_4053_the_readme_tunables_table_has_one_row_per_key_of_tunables_and_no_other():
    tunables = importlib.import_module("veri.tunables")

    assert drift(README.read_text(), tunables.TUNABLES) == []


def test_4053_a_key_with_no_row_and_a_row_naming_no_key_are_each_named():
    tunables = importlib.import_module("veri.tunables")
    text = "# x\n\n## tunables\n| `VERI_A` | `1` | its readers' own words |\n| `VERI_GONE` | `2` | x |\n\n## next\n"
    table = {"VERI_A": tunables.Tunable(tunables.text, "1"), "VERI_B": tunables.Tunable(tunables.text, "2")}

    assert drift(text, table) == [("VERI_B", "no row"), ("VERI_GONE", "names no key")]


def test_4053_a_row_whose_default_differs_from_the_tables_default_is_named_and_an_empty_default_reads_as_two_quotes():
    tunables = importlib.import_module("veri.tunables")
    text = "x\n## tunables\n| `VERI_A` | `1` | x |\n| `VERI_B` | \"\" | x |\n| `VERI_C` | `3` | x |\n"
    table = {"VERI_A": tunables.Tunable(tunables.text, "1"), "VERI_B": tunables.Tunable(tunables.text, ""),
             "VERI_C": tunables.Tunable(tunables.text, "30")}

    assert drift(text, table) == [("VERI_C", "default 3, not 30")]


def test_4465_the_dev_reset_tunables_are_gone_from_tunables_and_the_readme_table_and_the_conductor_growth_knob_stays_in_both():
    tunables = importlib.import_module("veri.tunables")
    listed = rows(README.read_text())
    gone = ("VERI_RESET_GROWTH_DEV", "VERI_RESET_ACK_TIMEOUT", "VERI_RESET_MAX_PER_HOUR")

    assert ([n for n in gone if n in tunables.TUNABLES or n in listed],
            "VERI_RESET_GROWTH_CONDUCTOR" in tunables.TUNABLES, "VERI_RESET_GROWTH_CONDUCTOR" in listed) == ([], True, True)
