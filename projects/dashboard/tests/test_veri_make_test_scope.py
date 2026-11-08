import pathlib
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[3]


def test_veri_make_test_collects_nothing_under_projects_dashboard():
    plan = subprocess.run(["make", "-n", "test"], cwd=ROOT, capture_output=True, text=True)

    assert (plan.returncode, "projects/dashboard" in plan.stdout) == (0, False)
