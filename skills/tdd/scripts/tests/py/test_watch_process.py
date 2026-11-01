"""Medium cases for `make watch`: make started for real over a scratch fixture repo, sleep and the nested make stubbed."""
import os
import shutil
import subprocess

import pytest

from conftest import SCRIPTS

ROOT = SCRIPTS.parents[2]
LIB = SCRIPTS / "lib" / "watch.sh"
SLEEP_STOP_AFTER_RECORDING = '#!/bin/sh\nprintf \'%s\\n\' "$1" >> "$SLEEP_LOG"\nkill -TERM "$PPID"\n'
SLEEP_WITH_CHANGES = """#!/bin/sh
n=$(( $(cat "$WATCH_COUNT") + 1 ))
echo "$n" > "$WATCH_COUNT"
case " $WATCH_CHANGE_AT " in
  *" $n "*) printf 'change %s\\n' "$n" > "$WATCH_FIXTURE/tracked.txt"
            touch -t "200${n}01010000" "$WATCH_FIXTURE/tracked.txt" ;;
esac
[ "$n" = "$WATCH_STOP_AT" ] && kill -TERM "$PPID"
exit 0
"""
MAKE_LOGGING_GOALS = '#!/bin/sh\nprintf \'%s %s\\n\' "$(cat "$WATCH_COUNT")" "$*" >> "$MAKE_LOG"\n'


def stub(path, text):
    path.write_text(text)
    path.chmod(0o755)


def git_init_and_add(repo):
    subprocess.run(["git", "-C", str(repo), "init", "-q"], check=True)
    subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)


def fixture_repo(tmp_path):
    fixture = tmp_path / "repo"
    (fixture / "skills" / "tdd" / "scripts" / "lib").mkdir(parents=True)
    shutil.copy(ROOT / "Makefile", fixture / "Makefile")
    shutil.copy(LIB, fixture / "skills" / "tdd" / "scripts" / "lib" / "watch.sh")
    (fixture / "tracked.txt").write_text("original\n")
    git_init_and_add(fixture)
    return fixture


def run_watch(tmp_path, fixture, change_at, stop_at):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    stub(bin_dir / "sleep", SLEEP_WITH_CHANGES)
    stub(bin_dir / "nested-make", MAKE_LOGGING_GOALS)
    (tmp_path / "count").write_text("0\n")
    log = tmp_path / "make.log"
    log.write_text("")
    env = dict(os.environ, PATH="%s%s%s" % (bin_dir, os.pathsep, os.environ["PATH"]), WATCH_COUNT=str(tmp_path / "count"),
               WATCH_FIXTURE=str(fixture), WATCH_CHANGE_AT=change_at, WATCH_STOP_AT=str(stop_at), MAKE_LOG=str(log))
    subprocess.run(["make", "--no-print-directory", "-s", "-C", str(fixture), "MAKE=%s" % (bin_dir / "nested-make"), "watch"],
                   env=env, stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=30)
    return [line.split() for line in log.read_text().splitlines()]


def watch_with_stub_sleep(tmp_path, interval):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    stub(bin_dir / "sleep", SLEEP_STOP_AFTER_RECORDING)
    log = tmp_path / "sleep.log"
    env = {k: v for k, v in os.environ.items() if k != "VERI_WATCH_INTERVAL"}
    env.update(PATH="%s%s%s" % (bin_dir, os.pathsep, os.environ["PATH"]), SLEEP_LOG=str(log))
    if interval is not None:
        env["VERI_WATCH_INTERVAL"] = interval
    ran = subprocess.run(["make", "--no-print-directory", "-s", "-C", str(ROOT), "watch"], env=env,
                         stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=30)
    return ran.returncode, ran.stderr, log.read_text().split() if log.exists() else []


@pytest.mark.process("make -np started over the real Makefile to read its rule database")
def test_make_n_watch_its_own_phony_target_separate_from_test_unit_and_merge_gates():
    ran = subprocess.run(["make", "--no-print-directory", "-np", "-C", str(ROOT), "watch"], stdin=subprocess.DEVNULL,
                         capture_output=True, text=True)
    assert ran.returncode == 0, ran.stderr
    rules = {}
    lines = ran.stdout.splitlines()
    for before, line in zip([""] + lines, lines):
        if line.startswith("#  Phony target") and ":" in before:
            rules[before.split(":")[0]] = before.split(":", 1)[1].split()
    assert "watch" in rules
    assert not {"test", "unit"} & set(rules["watch"])
    assert all("watch" not in rules.get(t, []) for t in ("test", "unit"))


@pytest.mark.process("make watch started over the real Makefile with a stub sleep first on PATH")
def test_veri_watch_interval_malformed_exits_2_naming_the_variable_unset_defaults_to_1(tmp_path):
    for bad in ("abc", "1x"):
        scratch = tmp_path / bad
        scratch.mkdir()
        code, err, _ = watch_with_stub_sleep(scratch, bad)
        assert (code, "VERI_WATCH_INTERVAL" in err) == (2, True), (bad, code, err)
    unset = tmp_path / "unset"
    unset.mkdir()
    assert watch_with_stub_sleep(unset, None)[2][:1] == ["1"]


@pytest.mark.process("make watch started over a scratch git repo with stub sleep and stub nested make")
def test_make_watch_reruns_make_unit_once_per_detected_change_never_between_changes(tmp_path):
    runs = run_watch(tmp_path, fixture_repo(tmp_path), "2 4", 6)
    assert [run[0] for run in runs] == ["2", "4"]


@pytest.mark.process("watch_snapshot sourced under sh over scratch git repos with watch_stat replaced by a recorder")
def test_make_watch_one_poll_pass_calls_its_stat_wrapper_exactly_once_whatever_the_number_of_tracked_files(tmp_path):
    calls = {}
    for n in (1, 40):
        repo = tmp_path / ("repo-%d" % n)
        repo.mkdir()
        for i in range(n):
            (repo / ("f%d.txt" % i)).write_text("%d\n" % i)
        git_init_and_add(repo)
        spy = tmp_path / ("spy-%d.log" % n)
        script = '. "$1"; watch_stat() { echo call >> "$SPY_LOG"; cat > /dev/null; }; watch_snapshot'
        subprocess.run(["sh", "-c", script, "sh", str(LIB)], cwd=repo, env=dict(os.environ, SPY_LOG=str(spy)), capture_output=True, text=True, check=True)
        calls[n] = len(spy.read_text().splitlines())
    assert calls == {1: 1, 40: 1}


@pytest.mark.process("make watch started over a scratch git repo with a nested make that logs its goals")
def test_make_watch_never_runs_any_make_target_besides_unit(tmp_path):
    runs = run_watch(tmp_path, fixture_repo(tmp_path), "2", 4)
    assert runs, "the loop never ran a nested make after a change, so nothing was checked"
    assert [[w for w in run[1:] if not w.startswith("-")] for run in runs] == [["unit"]] * len(runs)


def test_makefile_comment_header_documents_make_watch_as_a_low_priority_developer_convenience_like_profile_and_docs():
    header = []
    on = False
    for line in (ROOT / "Makefile").read_text().splitlines():
        if line.startswith("# `make watch`"):
            on = True
        if on and not line.startswith("#"):
            break
        if on:
            header.append(line[1:].strip())
    text = " ".join(header)
    assert text, "no comment paragraph opening '# `make watch`' in the Makefile"
    lowered = text.lower()
    assert ("developer convenience" in lowered or "low priority" in lowered) and "not part of `test`" in text \
        and "nothing gates on it" in text, text
