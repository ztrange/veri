"""A run's conductor never runs under VERI_EVENT_STRICT, so a logging mistake never bails a run (PRD 030.1, ET8)."""
import types

from veri import run_conductor


def test_the_conductors_environment_drops_veri_event_strict_set_by_the_launching_environment(tmp_path, monkeypatch):
    seen = []
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("VERI_EVENT_STRICT", "1")
    monkeypatch.setenv("CLAUDE_BIN", str(tmp_path / "claude"))
    real = run_conductor.subprocess.run

    def run(argv, **kwargs):
        if argv[0] != str(tmp_path / "claude"):
            return real(argv, **kwargs)
        seen.append(kwargs["env"])
        return types.SimpleNamespace(returncode=0)
    monkeypatch.setattr(run_conductor.subprocess, "run", run)
    monkeypatch.setattr(run_conductor, "past_preflight", lambda issue: True)

    run_conductor.conduct("", "8", dict(run_conductor.os.environ))

    assert [env.get("VERI_EVENT_STRICT") for env in seen] == [None]
