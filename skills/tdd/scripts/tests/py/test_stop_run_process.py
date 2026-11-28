"""Process cases for veri/stop_run.py: the ones that start a real process; the small cases are in unit/test_stop_run.py."""
import importlib
import os
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path

import pytest

from repo_builder import new_repo


@pytest.fixture
def stop_run():
    return importlib.import_module("veri.stop_run")


SCRIPTS = Path(__file__).resolve().parents[2]


# Spins while the process that started it lives, so a stub orphaned by a killed run (its parent gone) ends itself.
# /bin/sleep, not PATH's: the suite puts a guard shim named sleep first on PATH that forks a shell and ps per call.
SPINNER = "#!/bin/sh\nwhile kill -0 $PPID 2>/dev/null; do /bin/sleep 0.2; done\n"


@pytest.fixture
def started(request):
    """Processes the case starts, each killed and reaped by the pid recorded at its start."""
    procs = []
    yield procs
    end_all(procs)


def end_all(procs):
    for proc in procs:
        proc.kill()
    for proc in procs:
        proc.wait()


def git(*args, cwd):
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *args], cwd=cwd, check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


class ConductorHolder:
    """A claude -p stand-in run by a run_conductor.py stand-in; pid is the claude's. The launcher leads its own
    process group, so the claude in it ends with it also when its pid was never read."""

    def __init__(self, launcher, pid):
        self.launcher, self.pid = launcher, pid

    def kill(self):
        for target in (self.pid, self.launcher.pid):
            if target <= 1:
                continue  # 0 and -1 name whole groups, 1 is init: never a process this case started
            try:
                os.kill(target, 9)
            except OSError:
                pass
        try:
            os.killpg(self.launcher.pid, 9)
        except OSError:
            pass

    def wait(self):
        self.launcher.wait()
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            try:
                os.killpg(self.launcher.pid, 0)
            except ProcessLookupError:
                return
            except PermissionError:
                pass  # macOS refuses a group whose members are all zombies awaiting their reaper
            time.sleep(0.05)


def live_conductor(run, started):
    holder_dir = run / ".tdd" / "holder"
    holder_dir.mkdir(parents=True, exist_ok=True)
    claude_pid = holder_dir / "claude.pid"
    claude = stub(holder_dir / "claude", '#!/bin/sh\necho $$ > "%s"\n%s' % (claude_pid, SPINNER.split("\n", 1)[1]))
    launcher = stub(holder_dir / "run_conductor.py", '#!/bin/sh\n"%s" -p run\n' % claude)
    proc = subprocess.Popen([str(launcher), run.name], start_new_session=True)
    holder = ConductorHolder(proc, proc.pid)
    started.append(holder)
    for _ in range(500):
        if claude_pid.is_file() and claude_pid.read_text().strip():
            break
        time.sleep(0.05)
    recorded = claude_pid.read_text().strip() if claude_pid.is_file() else ""
    if not recorded:
        raise FileNotFoundError("%s: the stub claude recorded no pid within 25 s" % claude_pid)
    holder.pid = int(recorded)
    (run / ".tdd" / "conductor.pid").write_text("%d\n" % holder.pid)
    return holder


def stub(path, text=SPINNER):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    path.chmod(0o755)
    return path


def live_supervisor(run, name, started, stub_path):
    proc = subprocess.Popen([str(stub_path), name, run.name])
    started.append(proc)
    (run / ".tdd" / (name + ".pid")).write_text(recorded(proc.pid))
    return proc


def start_time_of(pid):
    """The start time as veri's writers record it (pid_file.ps_field: ps under LC_ALL=C and TZ=UTC)."""
    return importlib.import_module("veri.pid_file").ps_field("lstart", pid)


def recorded(pid):
    """A pid file's text: the pid, then its start time, as supervise.sh and detach-command.sh write it."""
    return "%d\n%s\n" % (pid, start_time_of(pid))


def reaped_pid():
    proc = subprocess.Popen(["sleep", "0"])
    proc.wait()
    return proc.pid


def gone(proc):
    for _ in range(40):
        if proc.poll() is not None:
            return True
        time.sleep(0.05)
    return False


def stop_text(run):
    path = run / ".tdd" / "stop"
    return path.read_text() if path.is_file() else None


def mutant_of(source, before, inserted, destination):
    """A copy of stop-run.sh with <inserted> on a line of its own before the first line starting <before>."""
    (destination / "veri").parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["cp", "-R", str(SCRIPTS / "veri"), str(destination / "veri")], check=True)
    if (SCRIPTS / "lib" / "shim-python.sh").is_file():
        (destination / "lib").mkdir(exist_ok=True)
        shutil.copy(SCRIPTS / "lib" / "shim-python.sh", destination / "lib" / "shim-python.sh")
        shutil.copy(SCRIPTS / "lib" / "venv-python.sh", destination / "lib" / "venv-python.sh")
    lines = (SCRIPTS / "stop-run.sh").read_text().splitlines()
    at = next(i for i, line in enumerate(lines) if line.startswith(before))
    stub(destination / "stop-run.sh", "\n".join(lines[:at] + [inserted] + lines[at:]) + "\n")
    return destination / "stop-run.sh"


def run_script(script, cwd, *argv):
    done = subprocess.run([str(script), *argv], cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return done.returncode, done.stdout, done.stderr


@pytest.mark.process("real supervisor processes seen by ps and sent a real TERM")
def test_stop_run_cli_mode_now_terms_the_pid_in_the_run_s_pid_file_whose_process_runs_supervise_sh_of_its_name_and_no_pid_whose_process_is_gone_or_runs_something_else(
        tmp_path, run_cli, stop_run, started):
    repo = new_repo(tmp_path.resolve() / "repo")
    run = repo / ".tdd" / "wt" / "5"
    live_conductor(run, started)
    supervisor = stub(tmp_path / "stubbin" / "supervise.sh")
    green = live_supervisor(run, "develop-green", started, supervisor)
    impostor = subprocess.Popen(["sleep", "60"])
    started.append(impostor)
    (run / ".tdd" / "verify-green.pid").write_text(recorded(impostor.pid))
    (run / ".tdd" / "verify-refactor.pid").write_text("%d\n" % reaped_pid())

    code, out, err = run_cli(stop_run, ["--mode", "now", "5"], cwd=repo)

    assert (code, out, err) == (0, str(run) + "\n", "")
    assert gone(green), "the develop-green supervisor %d was not signalled" % green.pid
    assert impostor.poll() is None


@pytest.mark.process("a real supervisor process whose ps line spells veri/supervise.py, sent a real TERM")
def test_stop_run_cli_mode_now_terms_the_pid_in_the_run_s_pid_file_whose_process_runs_veri_supervise_py_of_its_name(
        tmp_path, run_cli, stop_run, started):
    repo = new_repo(tmp_path.resolve() / "repo")
    run = repo / ".tdd" / "wt" / "5"
    live_conductor(run, started)
    supervisor = stub(tmp_path / "pybin" / "veri" / "supervise.py")
    refactor = live_supervisor(run, "develop-refactor", started, supervisor)

    code, out, err = run_cli(stop_run, ["--mode", "now", "5"], cwd=repo)

    assert (code, out, err) == (0, str(run) + "\n", "")
    assert gone(refactor), "the develop-refactor supervisor %d, spelled veri/supervise.py, was not signalled" % refactor.pid


@pytest.mark.process("the shim run through a symlink to the skill's scripts directory from a subdirectory of another repository")
def test_stop_run_sh_run_through_a_symlink_to_the_skill_s_scripts_directory_from_a_subdirectory_of_another_repository_stops_that_repository_s_run_and_writes_nothing_under_the_skill_s_own(
        tmp_path, started):
    skill_main = new_repo(tmp_path.resolve() / "skill-main")
    skill_scripts = skill_main / "skills" / "tdd" / "scripts"
    skill_scripts.mkdir(parents=True)
    subprocess.run(["cp", "-R", str(SCRIPTS / "stop-run.sh"), str(SCRIPTS / "veri"), str(skill_scripts)], check=True)
    (skill_scripts / "lib").mkdir()
    shutil.copy(SCRIPTS / "lib" / "shim-python.sh", skill_scripts / "lib" / "shim-python.sh")
    shutil.copy(SCRIPTS / "lib" / "venv-python.sh", skill_scripts / "lib" / "venv-python.sh")
    git("add", "-A", cwd=skill_main)
    git("commit", "-q", "-m", "skill", cwd=skill_main)
    skill_worktree = tmp_path.resolve() / "skill-worktree"
    git("worktree", "add", "-q", str(skill_worktree), "-b", "linked", cwd=skill_main)
    linked = tmp_path / "linked-scripts"
    linked.symlink_to(skill_worktree / "skills" / "tdd" / "scripts")
    listed = subprocess.run(["git", "worktree", "list", "--porcelain"], cwd=linked, check=True,
                            stdout=subprocess.PIPE, text=True).stdout
    assert listed.split("\n", 1)[0] == "worktree %s" % skill_main
    elsewhere = new_repo(tmp_path.resolve() / "elsewhere")
    far_run = elsewhere / ".tdd" / "wt" / "31337"
    live_conductor(far_run, started)
    deep = elsewhere / "some" / "sub" / "dir"
    deep.mkdir(parents=True)
    code, out, err = run_script(linked / "stop-run.sh", deep, "31337")

    assert (code, err, stop_text(far_run)) == (0, "", "at-ledger\n")
    assert "\n" not in out.rstrip("\n") and os.path.samefile(out.rstrip("\n"), far_run)
    assert not (skill_main / ".tdd" / "wt" / "31337").exists()


def planted_run(path, started, supervisor):
    run = path / ".tdd" / "wt" / "5"
    live_conductor(run, started)
    return run, live_supervisor(run, "develop-red", started, supervisor)


def assert_planted_cd_contained(tmp_path, started, decoy_name, before, answers_live_run):
    """The mutant, typed from a scratch repository with a live run, stops that run alone when <answers_live_run>, else refuses."""
    scratch = new_repo(tmp_path.resolve() / "repo")
    decoy = new_repo(tmp_path.resolve() / decoy_name)
    supervisor = stub(tmp_path / "stubbin" / "supervise.sh")
    scratch_run, _ = planted_run(scratch, started, supervisor)
    decoy_run, decoy_sup = planted_run(decoy, started, supervisor)
    mutant = mutant_of(SCRIPTS, before, 'cd "$(dirname "$0")"', decoy / "skills" / "tdd" / "scripts")

    code, out, err = run_script(mutant, scratch, "--mode", "now", "--all")

    assert stop_text(decoy_run) is None
    assert decoy_sup.poll() is None
    assert (code, out) == ((0, str(scratch_run) + "\n") if answers_live_run else (2, "")), err


@pytest.mark.process("the shim, with a cd to its own directory planted before the exec, run for real in another repository")
def test_1158_a_stop_run_sh_that_resolves_its_main_tree_from_its_own_directory_not_the_suite_s_scratch_repository_writes_no_stop_file_and_signals_no_supervisor_outside_that_repository(
        tmp_path, started):
    assert_planted_cd_contained(tmp_path, started, "decoy", ("exec python3", '. "$(dirname "$0")/lib/shim-python.sh"', 'exec "$py"'), answers_live_run=True)


@pytest.mark.process("the shim, with a cd to its own directory planted before it records its caller, run for real in another repository")
def test_1158_a_stop_run_sh_that_moves_to_its_own_directory_before_it_records_where_it_was_called_from_writes_no_stop_file_and_signals_no_supervisor_outside_the_suite_s_scratch_repository(
        tmp_path, started):
    assert_planted_cd_contained(tmp_path, started, "early-decoy", "export VERI_CALLER_DIR", answers_live_run=False)


@pytest.mark.process("the shim copied under the scratch directory, with a cd two levels up planted before it records its caller, run for real")
def test_1158_the_suite_runs_a_scratch_copy_of_stop_run_sh_and_a_cd_dirname_0_up_two_planted_into_it_writes_no_stop_file_and_signals_no_supervisor_outside_the_scratch_repository(
        tmp_path, started):
    work = tmp_path.resolve()
    scratch = new_repo(work / "repo")
    supervisor = stub(work / "stubbin" / "supervise.sh")
    subject = mutant_of(SCRIPTS, "export VERI_CALLER_DIR", 'cd "$(dirname "$0")/../.."', work / "skill" / "scripts")
    landing = Path(os.path.realpath(subject.parent / ".." / ".."))
    assert landing == work and scratch not in landing.parents
    landing_run, landing_sup = planted_run(landing, started, supervisor)

    run_script(subject, scratch, "--mode", "now", "--all")

    assert stop_text(landing_run) is None
    assert landing_sup.poll() is None


@pytest.mark.process("a real linked worktree outside the primary clone, resolved by real git")
def test_1158_stop_run_sh_typed_from_a_linked_worktree_outside_the_primary_clone_exits_0_and_writes_at_ledger_into_the_run_s_stop_file(
        tmp_path, run_cli, stop_run, started):
    primary = new_repo(tmp_path.resolve() / "primary")
    git("commit", "-q", "--allow-empty", "-m", "init", cwd=primary)
    outside = tmp_path.resolve() / "outside-linked"
    git("worktree", "add", "-q", str(outside), "-b", "linked", cwd=primary)
    primary_run = primary / ".tdd" / "wt" / "7"
    live_conductor(primary_run, started)

    code, out, err = run_cli(stop_run, ["7"], cwd=outside)

    assert (code, err, stop_text(primary_run)) == (0, "", "at-ledger\n")


@pytest.mark.process("a real detached group leader with a descendant and a member of the test's own in its group, sent a real TERM")
def test_3375_stop_run_cli_mode_now_terms_the_whole_process_group_of_the_detached_command_in_fulltier_pid(
        tmp_path, run_cli, stop_run, started):
    repo = new_repo(tmp_path.resolve() / "repo")
    run = repo / ".tdd" / "wt" / "5"
    live_conductor(run, started)
    child_file = tmp_path / "child.pid"
    command = subprocess.Popen(["sh", "-c", 'sleep 60 & echo $! > "$0"; wait', str(child_file)],
                               process_group=0)
    started.append(command)
    member = subprocess.Popen(["sleep", "60"], process_group=command.pid)
    started.append(member)
    (run / ".tdd" / "fulltier.pid").write_text(recorded(command.pid))
    for _ in range(200):
        if child_file.is_file() and child_file.read_text().strip():
            break
        time.sleep(0.05)
    child = int(child_file.read_text())

    try:
        code, out, err = run_cli(stop_run, ["--mode", "now", "5"], cwd=repo,
                                 env={"VERI_STOP_KILL_GRACE": "0.2"})

        assert (code, out, err) == (0, str(run) + "\n", "")
        assert gone(command), "the detached command %d was not signalled" % command.pid
        ended = member.wait(timeout=5)
        assert ended == -signal.SIGTERM, "the group member ended by signal %d, not TERM (%d)" % (-ended, signal.SIGTERM)
        for _ in range(40):
            try:
                os.kill(child, 0)
            except ProcessLookupError:
                break
            time.sleep(0.05)
        else:
            pytest.fail("the detached command's descendant %d was not signalled" % child)
    finally:
        try:
            os.kill(child, 9)
        except OSError:
            pass


@pytest.mark.process("a real session leader that is not the command detach-command.sh starts, holding the pid fulltier.pid records, with a descendant in its group")
def test_3375_stop_run_cli_mode_now_signals_no_group_of_an_unrelated_process_now_holding_the_pid_in_fulltier_pid(
        tmp_path, run_cli, stop_run, started):
    repo = new_repo(tmp_path.resolve() / "repo")
    run = repo / ".tdd" / "wt" / "5"
    live_conductor(run, started)
    child_file = tmp_path / "child.pid"
    unrelated = subprocess.Popen(
        [sys.executable, "-c",
         "import subprocess, sys\n"
         "child = subprocess.Popen(['sleep', '60'])\n"
         "open(sys.argv[1], 'w').write(str(child.pid))\n"
         "child.wait()\n",
         str(child_file)],
        start_new_session=True)
    started.append(unrelated)
    (run / ".tdd" / "fulltier.pid").write_text(recorded(unrelated.pid))
    for _ in range(200):
        if child_file.is_file() and child_file.read_text().strip():
            break
        time.sleep(0.05)
    child = int(child_file.read_text())

    try:
        code, out, err = run_cli(stop_run, ["--mode", "now", "5"], cwd=repo)

        assert (code, out, err) == (0, str(run) + "\n", "")
        assert not gone(unrelated), "the unrelated process %d now holding the recorded pid was signalled" % unrelated.pid
        os.kill(child, 0)
    finally:
        try:
            os.kill(child, 9)
        except OSError:
            pass


@pytest.mark.process("a real detached session leader and a descendant that both ignore TERM, sent a real TERM and then KILL")
def test_3375_stop_run_cli_mode_now_kills_the_members_of_the_detached_command_s_group_that_survive_the_term(
        tmp_path, run_cli, stop_run, started):
    repo = new_repo(tmp_path.resolve() / "repo")
    run = repo / ".tdd" / "wt" / "5"
    live_conductor(run, started)
    child_file = tmp_path / "child.pid"
    command = subprocess.Popen(["sh", "-c", 'trap "" TERM; sleep 60 & echo $! > "$0"; wait', str(child_file)],
                               start_new_session=True)
    started.append(command)
    (run / ".tdd" / "fulltier.pid").write_text(recorded(command.pid))
    for _ in range(200):
        if child_file.is_file() and child_file.read_text().strip():
            break
        time.sleep(0.05)
    child = int(child_file.read_text())

    try:
        code, out, err = run_cli(stop_run, ["--mode", "now", "5"], cwd=repo,
                                 env={"VERI_STOP_KILL_GRACE": "0.2"})

        assert (code, out, err) == (0, str(run) + "\n", "")
        assert gone(command), "the TERM-ignoring detached command %d was not killed" % command.pid
        for _ in range(40):
            try:
                os.kill(child, 0)
            except ProcessLookupError:
                break
            time.sleep(0.05)
        else:
            pytest.fail("the TERM-ignoring descendant %d of the detached command was not killed" % child)
    finally:
        try:
            os.kill(child, 9)
        except OSError:
            pass


@pytest.mark.process("two real sh -c session leaders, one veri's recorded command and one unrelated holding a recorded pid, sent real signals")
def test_3375_stop_run_cli_mode_now_signals_a_detached_sh_c_only_when_its_recorded_start_time_still_matches_and_never_an_unrelated_sh_c_holding_the_pid(
        tmp_path, run_cli, stop_run, started):
    repo = new_repo(tmp_path.resolve() / "repo")
    run = repo / ".tdd" / "wt" / "5"
    live_conductor(run, started)
    own = subprocess.Popen(["sh", "-c", 'trap "" TERM; sleep 60 & wait'], start_new_session=True)
    unrelated = subprocess.Popen(["sh", "-c", "sleep 60 & wait"], start_new_session=True)
    started.extend([own, unrelated])
    own_started = start_time_of(own.pid)
    (run / ".tdd" / "fulltier.pid").write_text("%d\n%s\n" % (own.pid, own_started))
    (run / ".tdd" / "fasttier.pid").write_text("%d\nThu Jan  1 00:00:00 1970\n" % unrelated.pid)
    time.sleep(0.3)

    try:
        code, out, err = run_cli(stop_run, ["--mode", "now", "5"], cwd=repo,
                                 env={"VERI_STOP_KILL_GRACE": "0.2"})

        assert (code, out, err) == (0, str(run) + "\n", "")
        assert gone(own), "veri's own detached command %d was not sent TERM then KILL" % own.pid
        assert not gone(unrelated), "the unrelated sh -c %d holding the recorded pid was signalled" % unrelated.pid
    finally:
        for proc in (own, unrelated):
            try:
                os.killpg(proc.pid, 9)
            except OSError:
                pass


@pytest.mark.process("a real detached group killed by stop-run.sh")
def test_3375_stop_run_cli_mode_now_exits_0_when_the_detached_group_leader_sent_kill_is_an_unreaped_zombie_and_2_when_a_live_member_survives_kill(
        monkeypatch, tmp_path, run_cli, stop_run, started):
    import signal
    repo = new_repo(tmp_path.resolve() / "repo")
    run = repo / ".tdd" / "wt" / "5"
    live_conductor(run, started)
    env = {"VERI_STOP_KILL_GRACE": "0.2"}
    real_killpg = os.killpg

    stubborn = subprocess.Popen(["sh", "-c", 'trap "" TERM; sleep 60 & wait'], start_new_session=True)
    started.append(stubborn)
    (run / ".tdd" / "fulltier.pid").write_text(recorded(stubborn.pid))
    time.sleep(0.3)
    monkeypatch.setattr(os, "killpg", lambda group, sig: None if sig == signal.SIGKILL else real_killpg(group, sig))
    try:
        code, out, err = run_cli(stop_run, ["--mode", "now", "5"], cwd=repo, env=env)
        assert code == 2 and str(stubborn.pid) in err and str(run) in err
    finally:
        monkeypatch.setattr(os, "killpg", real_killpg)
        os.killpg(stubborn.pid, 9)
        stubborn.wait()

    leader = subprocess.Popen(["sh", "-c", "sleep 60 & wait"], start_new_session=True)
    started.append(leader)
    (run / ".tdd" / "fulltier.pid").write_text(recorded(leader.pid))
    time.sleep(0.3)
    try:
        code, out, err = run_cli(stop_run, ["--mode", "now", "5"], cwd=repo, env=env)
        state = subprocess.run(["ps", "-o", "stat=", "-p", str(leader.pid)],
                               stdout=subprocess.PIPE, text=True).stdout.strip()
        assert state.startswith("Z"), "the killed leader %d should be an unreaped zombie, ps says %r" % (leader.pid, state)
        assert (code, out, err) == (0, str(run) + "\n", "")
    finally:
        try:
            os.killpg(leader.pid, 9)
        except OSError:
            pass
        leader.wait()


@pytest.mark.process("python3 on veri/stop_run.py as a script, with VERI_CALLER_DIR set but empty")
def test_stop_run_run_as_a_script_with_an_empty_veri_caller_dir_stays_in_its_directory(tmp_path):
    ran = subprocess.run([sys.executable, str(SCRIPTS / "veri" / "stop_run.py"), "--help"], cwd=tmp_path,
                         env={**os.environ, "VERI_CALLER_DIR": ""}, capture_output=True, text=True, stdin=subprocess.DEVNULL)

    assert (ran.returncode, ran.stdout.startswith("usage: stop-run.sh")) == (0, True)


def alive(pid):
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    return True


@pytest.mark.process("the stub claude live_conductor starts, torn down by the started fixture's teardown")
def test_4131_the_started_teardown_ends_the_stub_claude_live_conductor_starts_also_when_its_claude_pid_was_never_read(tmp_path):
    run = tmp_path / ".tdd" / "wt" / "5"
    claude_pid = run / ".tdd" / "holder" / "claude.pid"
    procs = []
    try:
        live_conductor(run, procs)
    except FileNotFoundError:
        pass
    procs[0].pid = procs[0].launcher.pid
    end_all(procs)
    deadline = time.monotonic() + 10
    while not (claude_pid.is_file() and claude_pid.read_text().strip()) and time.monotonic() < deadline:
        time.sleep(0.05)
    claude = int(claude_pid.read_text()) if claude_pid.is_file() and claude_pid.read_text().strip() else None
    try:
        assert claude is None or not alive(claude), "the stub claude %d outlived the teardown" % claude
    finally:
        if claude is not None and claude > 1:
            try:
                os.kill(claude, 9)
            except OSError:
                pass


@pytest.mark.process("the stub claude live_conductor starts, left behind by a launcher killed alone")
def test_4131_the_stub_claude_ends_itself_once_its_launcher_is_gone(tmp_path, started):
    holder = live_conductor(tmp_path / ".tdd" / "wt" / "5", started)

    os.kill(holder.launcher.pid, 9)
    holder.launcher.wait()

    deadline = time.monotonic() + 20
    while alive(holder.pid) and time.monotonic() < deadline:
        time.sleep(0.05)
    assert not alive(holder.pid), "the stub claude %d outlived its launcher" % holder.pid
