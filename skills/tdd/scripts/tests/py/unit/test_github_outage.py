"""Unit cases for veri/github_outage.py: the outage file, the merging list and the one wait, in a tmp_path tree.

The status read, the pid-liveness check, the process starter, the clock and the pause are injected: no process,
no network, no real wait."""
import importlib
import threading

import pytest

outage = importlib.import_module("veri.github_outage")
github_status = importlib.import_module("veri.github_status")

U = "https://github.com/o/r/pull/%d"
INCIDENT = "Incident with Pull Requests\tPull Requests\t2026-11-16 05:59\t42"


class Fake(outage.World):
    def __init__(self, answer=(1, [INCIDENT]), live=()):
        self.answer, self.live, self.starts, self.now, self.next_pid = answer, set(live), [], 0.0, 900

    def status(self):
        if isinstance(self.answer, Exception):
            raise self.answer
        return self.answer

    def alive(self, pid, start):
        return (str(pid), start) in self.live

    def started(self, pid):
        return "start-%s" % pid

    def start(self, argv, out):
        self.next_pid += 1
        self.starts.append(argv)
        self.live.add((str(self.next_pid), "start-%s" % self.next_pid))
        return self.next_pid

    def nonce(self):
        return "nonce-%d" % len(self.starts)

    def clock(self):
        return self.now

    def pause(self, seconds):
        self.now += seconds


def text(root, name=outage.FILE):
    return (root / name).read_text() if (root / name).exists() else None


def entered(root, *done):
    world = Fake()
    assert outage.enter(str(root), U % 1, world)[0] == 0
    for n in done:
        assert outage.hold(str(root), U % n) == (0, ["held"])
    return world


def test_enter_on_a_counting_incident_creates_the_file_with_the_status_lines_the_url_and_the_marker(tmp_path):
    code, lines = outage.enter(str(tmp_path), U % 1, Fake())

    assert (code, lines) == (0, ["entered", INCIDENT])
    assert text(tmp_path) == "%s\n%s\n%s\n" % (INCIDENT, U % 1, outage.MARKER)


def test_enter_with_the_file_present_holds_failed_prs_above_the_marker_in_the_order_they_failed(tmp_path):
    world = entered(tmp_path, 10)

    assert outage.enter(str(tmp_path), U % 2, world) == (0, ["held", INCIDENT])
    assert outage.enter(str(tmp_path), U % 3, world)[0] == 0
    assert outage.held(outage.lines_of(str(tmp_path / outage.FILE))) == [U % 1, U % 2, U % 3, U % 10]


def test_enter_when_github_answered_and_nothing_counts_exits_1_with_the_young_lines_and_writes_nothing(tmp_path):
    code, lines = outage.enter(str(tmp_path), U % 1, Fake(answer=(0, ["young 5 Incident"])))

    assert (code, lines, text(tmp_path)) == (1, ["unexplained", "young 5 Incident"], None)


def test_enter_with_no_answer_exits_2_and_writes_nothing(tmp_path):
    code, lines = outage.enter(str(tmp_path), U % 1, Fake(answer=github_status.NoAnswer("timed out")))

    assert (code, text(tmp_path)) == (2, None)
    assert lines == ["no answer from GitHub's status page: timed out"]


def test_hold_exits_3_when_local_mode_is_off_and_never_creates_the_file(tmp_path):
    assert (outage.hold(str(tmp_path), U % 4), text(tmp_path)) == ((3, []), None)


def test_hold_appends_once_and_refuses_a_line_that_is_not_exactly_a_pr_url(tmp_path):
    entered(tmp_path, 10, 10)

    assert outage.hold(str(tmp_path), "https://status.example/incident")[0] == 2
    assert outage.held(outage.lines_of(str(tmp_path / outage.FILE))) == [U % 1, U % 10]


def test_crlf_lines_a_missing_final_newline_and_status_lines_starting_https_are_read_right(tmp_path):
    (tmp_path / ".tdd").mkdir()
    (tmp_path / outage.FILE).write_bytes(
        b"https://status.example/x\r\nhttps://github.com/o/r/pull/9 is slow\r\n" + (U % 7).encode() + b"\r\n" + outage.MARKER.encode() + b"\r\n"
        + (U % 8).encode())
    world = Fake()

    assert outage.hold(str(tmp_path), U % 8) == (0, ["held"])
    assert outage.enter(str(tmp_path), U % 6, world)[0] == 0
    assert [outage.take(str(tmp_path), 5, world)[1][0] for _ in range(3)] == [U % 7, U % 6, U % 8]
    assert b"\r" not in (tmp_path / outage.FILE).read_bytes()


def test_take_gives_one_url_at_a_time_in_the_files_order(tmp_path):
    world = entered(tmp_path, 10, 11)
    outage.enter(str(tmp_path), U % 2, world)

    taken = [outage.take(str(tmp_path), 5, world) for _ in range(4)]

    assert [t[1] for t in taken] == [[U % 1], [U % 2], [U % 10], [U % 11]]


def test_only_ended_tells_a_raced_take_exits_3_silently_and_the_file_goes_when_the_last_merge_has_finished(tmp_path):
    world = entered(tmp_path)
    assert outage.take(str(tmp_path), 5, world) == (0, [U % 1])

    raced = outage.take(str(tmp_path), 6, world)
    still = text(tmp_path)
    assert outage.settle(str(tmp_path), U % 1, "merged") == (0, ["merged"])
    last = outage.take(str(tmp_path), 5, world)
    after = outage.take(str(tmp_path), 6, world)

    assert (raced, still is not None, last, after, text(tmp_path)) == ((3, []), True, (0, ["ended"]), (3, []), None)


def test_settle_failed_holds_the_url_first_again_and_a_crash_between_its_writes_leaves_it_in_both_lists(tmp_path, monkeypatch):
    world = entered(tmp_path, 10)
    outage.take(str(tmp_path), 5, world)
    real = outage.write_merging

    def crash(root, entries):
        raise OSError("disk full")

    monkeypatch.setattr(outage, "write_merging", crash)
    with pytest.raises(OSError):
        outage.settle(str(tmp_path), U % 1, "failed")
    in_both = (U % 1 in outage.held(outage.lines_of(str(tmp_path / outage.FILE))),
               U % 1 in [e[0] for e in outage.merging_of(str(tmp_path))])
    monkeypatch.setattr(outage, "write_merging", real)

    assert in_both == (True, True)
    assert outage.settle(str(tmp_path), U % 1, "failed") == (0, ["failed"])
    assert outage.held(outage.lines_of(str(tmp_path / outage.FILE))) == [U % 1, U % 10]
    assert outage.merging_of(str(tmp_path)) == []


def test_a_crash_inside_take_leaves_the_url_in_both_lists_never_neither(tmp_path, monkeypatch):
    world = entered(tmp_path)

    def crash(path, lines):
        raise OSError("disk full")

    monkeypatch.setattr(outage, "write", crash)
    monkeypatch.setattr(outage, "write_merging", lambda root, entries: (tmp_path / outage.MERGING).write_text(
        "".join("\t".join(e) + "\n" for e in entries)))
    with pytest.raises(OSError):
        outage.take(str(tmp_path), 5, world)

    assert (U % 1 in text(tmp_path), [e[0] for e in outage.merging_of(str(tmp_path))]) == (True, [U % 1])


def test_a_file_removed_and_recreated_while_a_verb_waits_on_the_lock_is_the_file_it_acts_on(tmp_path, monkeypatch):
    entered(tmp_path)
    real = outage.acquire

    def swapped(handle):
        (tmp_path / outage.FILE).unlink()
        (tmp_path / outage.FILE).write_text("NEW\n%s\n%s\n" % (U % 50, outage.MARKER))
        real(handle)

    monkeypatch.setattr(outage, "acquire", swapped)
    code = outage.hold(str(tmp_path), U % 51)

    assert (code, text(tmp_path)) == ((0, ["held"]), "NEW\n%s\n%s\n%s\n" % (U % 50, outage.MARKER, U % 51))


def test_adopt_reclaims_only_urls_whose_claimer_is_dead_or_is_the_caller_from_before_a_reset(tmp_path):
    (tmp_path / ".tdd").mkdir()
    (tmp_path / outage.MERGING).write_text("%s\t10\tstart-10\n%s\t20\tstart-20\n%s\t30\tstart-30\n" % (U % 1, U % 2, U % 3))
    world = Fake(live={("20", "start-20"), ("30", "start-30")})

    assert outage.adopt(str(tmp_path), 30, world) == (0, [U % 1, U % 3])
    assert outage.merging_of(str(tmp_path)) == [(U % 1, "30", "start-30"), (U % 2, "20", "start-20"),
                                                 (U % 3, "30", "start-30")]
    assert outage.adopt(str(tmp_path), 40, world) == (3, [])


def test_two_wait_starters_start_one_wait(tmp_path):
    world = entered(tmp_path)

    first = outage.wait_start(str(tmp_path), world)
    second = outage.wait_start(str(tmp_path), world)

    assert (first, second, len(world.starts)) == ((0, ["started"]), (3, ["live"]), 1)
    assert world.starts[0][-3:] == [world.starts[0][-3], "wait", "3600"]


def test_a_stale_exit_record_and_a_reused_pid_never_read_as_a_wait_that_ended(tmp_path):
    entered(tmp_path)
    (tmp_path / outage.WAIT).write_text("nonce-old 123 start-123\n")
    (tmp_path / outage.WAIT_EXIT).write_text("nonce-older 0\n")
    reused = Fake(live={("123", "start-of-another-process")})

    assert outage.wait_status(str(tmp_path), reused) == (3, ["none"])
    (tmp_path / outage.WAIT_EXIT).write_text("nonce-old 0\n")
    assert outage.wait_status(str(tmp_path), reused) == (0, ["ended 0"])


def test_wait_start_refuses_when_local_mode_is_off_and_restarts_a_wait_that_ended(tmp_path):
    world = Fake()
    assert outage.wait_start(str(tmp_path), world) == (3, ["off"])
    entered(tmp_path)
    outage.wait_start(str(tmp_path), world)
    (tmp_path / outage.WAIT_EXIT).write_text("nonce-0 3\n")

    assert outage.wait_start(str(tmp_path), world) == (0, ["started"])
    assert len(world.starts) == 2


def test_wait_returns_on_the_end_on_a_dead_wait_and_after_max_seconds(tmp_path):
    world = entered(tmp_path)
    outage.wait_start(str(tmp_path), world)

    assert outage.wait(str(tmp_path), 30, 5, world) == (3, ["live"])
    (tmp_path / outage.WAIT_EXIT).write_text("nonce-0 0\n")
    assert outage.wait(str(tmp_path), 30, 5, world) == (0, ["ended 0"])
    (tmp_path / outage.WAIT).write_text("nonce-9 901 start-of-another\n")
    assert outage.wait(str(tmp_path), 30, 5, world) == (2, ["none"])


def test_status_lists_the_mode_the_held_and_merging_prs_and_the_wait(tmp_path):
    world = entered(tmp_path, 10)
    outage.take(str(tmp_path), 5, world)

    assert outage.status(str(tmp_path), world) == (0, ["mode on", "held " + U % 10, "merging %s orphan" % (U % 1),
                                                       "wait none"])
    assert outage.status(str(tmp_path / "elsewhere"), world) == (3, ["mode off", "wait none"])


def test_fifty_parallel_holds_are_all_kept(tmp_path):
    entered(tmp_path)
    threads = [threading.Thread(target=outage.hold, args=(str(tmp_path), U % n)) for n in range(100, 150)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert sorted(outage.held(outage.lines_of(str(tmp_path / outage.FILE)))) == sorted([U % 1] + [U % n for n in range(100, 150)])


def test_twenty_parallel_takers_of_fifteen_urls_take_each_once_and_one_sees_ended(tmp_path):
    world = entered(tmp_path, *range(100, 114))
    got, lock = [], threading.Lock()

    def taker(pid):
        while True:
            code, lines = outage.take(str(tmp_path), pid, world)
            if code == 3 and not (tmp_path / outage.FILE).exists():
                return
            if code == 0:
                with lock:
                    got.append(lines[0])
                if lines[0] != "ended":
                    outage.settle(str(tmp_path), lines[0], "merged")

    threads = [threading.Thread(target=taker, args=(n,)) for n in range(20)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    urls = [g for g in got if g != "ended"]
    assert (len(urls), len(set(urls)), got.count("ended")) == (15, 15, 1)


def test_run_refuses_a_bad_verb_or_argument(tmp_path):
    world = Fake()
    for argv in ([], ["take"], ["take", "--pid", "x"], ["settle", U % 1, "landed"], ["wait", "-1"], ["status", "x"]):
        assert outage.run(argv, str(tmp_path), world) is None, argv


def test_the_default_status_read_refuses_a_bad_poll_knob_before_any_read_so_enter_never_starts_a_wait_that_dies(tmp_path, monkeypatch):
    monkeypatch.setenv("VERI_GITHUB_STATUS_POLL", "0")
    monkeypatch.setattr(github_status, "read", lambda *a, **k: (1, [INCIDENT]))

    with pytest.raises(github_status.NoAnswer) as refused:
        github_status.default_read()

    assert "VERI_GITHUB_STATUS_POLL" in str(refused.value)


def test_take_drops_a_held_url_already_merging_so_a_crash_left_in_both_lists_is_never_taken_twice(tmp_path):
    world = entered(tmp_path, 10)
    (tmp_path / outage.MERGING).write_text("%s\t5\tstart-5\n" % (U % 1))

    shown = outage.status(str(tmp_path), world)[1]
    taken = outage.take(str(tmp_path), 6, world)

    assert [line for line in shown if line.split()[1:2] == [U % 1]] == ["merging %s orphan" % (U % 1)]
    assert taken == (0, [U % 10])
    assert [e[0] for e in outage.merging_of(str(tmp_path))] == [U % 1, U % 10]
    assert outage.held(outage.lines_of(str(tmp_path / outage.FILE))) == []


def test_write_syncs_the_temporary_file_to_disk_before_renaming_it_over_the_file(tmp_path, monkeypatch):
    seen, real_fsync, real_replace = [], outage.os.fsync, outage.os.replace
    monkeypatch.setattr(outage.os, "fsync", lambda fd: (seen.append("fsync"), real_fsync(fd))[1])
    monkeypatch.setattr(outage.os, "replace", lambda a, b: (seen.append("replace"), real_replace(a, b))[1])

    outage.write(str(tmp_path / "f"), ["one"])

    assert (seen, (tmp_path / "f").read_text()) == (["fsync", "replace"], "one\n")


def test_status_reads_under_the_lock_so_a_change_made_by_the_holder_is_seen_whole(tmp_path, monkeypatch):
    world = entered(tmp_path)
    real = outage.acquire

    def holder_takes_first(handle):
        outage.acquire = real
        outage.take(str(tmp_path), 5, world)
        real(handle)

    monkeypatch.setattr(outage, "acquire", holder_takes_first)
    shown = outage.status(str(tmp_path), world)[1]

    assert shown[:2] == ["mode on", "merging %s orphan" % (U % 1)]


def test_status_with_pid_tells_the_callers_own_claims_from_a_live_other_sessions(tmp_path):
    (tmp_path / ".tdd").mkdir()
    (tmp_path / outage.MERGING).write_text("%s\t30\tstart-30\n%s\t20\tstart-20\n%s\t10\tstart-10\n" % (U % 1, U % 2, U % 3))
    world = Fake(live={("20", "start-20"), ("30", "start-30")})

    code, shown = outage.run(["status", "--pid", "30"], str(tmp_path), world)

    assert (code, shown) == (0, ["mode off", "merging %s mine" % (U % 1), "merging %s live" % (U % 2),
                                 "merging %s orphan" % (U % 3), "wait none"])
