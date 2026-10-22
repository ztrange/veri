"""The shapes of environment read that direct_reads() must name."""
from test_tunable_reads import direct_reads


def test_1997_the_guard_names_the_line_of_a_planted_environ_copy_read_by_a_veri_name(tmp_path):
    planted = tmp_path / "planted.py"
    planted.write_text('import os\ne = os.environ.copy()\nvalue = e.get("VERI_X")\n')

    assert direct_reads(planted) == ["%s:2" % planted]


def test_1997_the_guard_names_the_line_of_a_planted_aliased_environ_read_by_a_veri_name(tmp_path):
    planted = tmp_path / "planted.py"
    planted.write_text('import os as o\ne = o.environ\nvalue = e.get("VERI_X")\n')

    assert direct_reads(planted) == ["%s:2" % planted]


def test_1997_the_guard_names_the_line_of_a_planted_environ_spread_read_by_a_veri_name(tmp_path):
    planted = tmp_path / "planted.py"
    planted.write_text('import os\ne = {**os.environ}\nvalue = e.get("VERI_X")\n')

    assert direct_reads(planted) == ["%s:2" % planted]


def test_1997_the_guard_names_the_line_of_a_planted_dict_copy_read_by_a_veri_name_held_in_a_variable(tmp_path):
    planted = tmp_path / "planted.py"
    planted.write_text('import os\ne = dict(os.environ)\nname = "VERI_X"\nvalue = e.get(name)\n')

    assert direct_reads(planted) == ["%s:2" % planted]


def test_1997_the_guard_names_the_line_of_a_planted_star_import_environ_read_by_a_veri_name(tmp_path):
    planted = tmp_path / "planted.py"
    planted.write_text('from os import *\nvalue = environ.get("VERI_X")\n')

    assert direct_reads(planted) == ["%s:2" % planted]


def test_1997_the_guard_names_the_line_of_a_planted_tunables_environment_read_by_a_veri_name(tmp_path):
    planted = tmp_path / "planted.py"
    planted.write_text('from veri import tunables\ne = tunables.environment()\nvalue = e.get("VERI_X")\n')

    assert direct_reads(planted) == ["%s:2" % planted]
