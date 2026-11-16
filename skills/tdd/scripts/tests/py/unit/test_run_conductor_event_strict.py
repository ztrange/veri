"""A run's conductor never runs under VERI_EVENT_STRICT, so a logging mistake never bails a run (PRD 030.1, ET8)."""
from veri import run_conductor


def test_the_conductors_environment_drops_veri_event_strict_set_by_the_launching_environment(
        tmp_path, monkeypatch, fake_processes):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("VERI_EVENT_STRICT", "1")
    monkeypatch.setenv("CLAUDE_BIN", str(tmp_path / "claude"))
    monkeypatch.setattr(run_conductor, "past_preflight", lambda issue: True)
    fake = fake_processes.answers({"claude": (0, "", "")})

    run_conductor.conduct("", "8", dict(run_conductor.os.environ))

    assert [kwargs["env"].get("VERI_EVENT_STRICT") for _, kwargs in fake.seen] == [None]
