"""Cases for the machine-wide run journal under $VERI_HOME."""
import os


def test_hermetic_environment_points_veri_home_at_the_cases_tmp_path(tmp_path):
    assert os.environ.get("VERI_HOME") == str(tmp_path)
