# Plan for #4527 — dispatch.sh ends its watch with exit 0 on an advisory line (queueing, stretched, t-lowered), so a consumer cannot tell advice from a run event

- [x] a poll that prints the `queueing` line keeps watching: `dispatch.main` returns None once the fake world's wait() stops ⟦criterion 1⟧
- [x] a poll that prints a `stretched` line keeps watching: `dispatch.main` returns None once the fake world's wait() stops ⟦criterion 2⟧
- [x] a poll that prints a `t-lowered` line keeps watching: `dispatch.main` returns None once the fake world's wait() stops ⟦criterion 3⟧
- [x] a `queueing` line followed by a run's `### ✅ Done` exit ends on `done <n> <pr-url>`, after the `queueing` line, exit 0 ⟦criterion 4⟧
- [x] a `queueing` line followed by an empty queue ends on `queue-empty`, after the `queueing` line, exit 3 ⟦criterion 4⟧
- [ ] over further polls of an unchanged world, the `queueing`, `stretched` and `t-lowered` lines each appear once ⟦criterion 5⟧
- [ ] `SCRIPTS.md`'s `dispatch.sh` entry and vdev's *Watching* and *Speaking* say advisories are printed while dispatch keeps watching, never as the watch's end, graded ⟦criterion 6⟧
