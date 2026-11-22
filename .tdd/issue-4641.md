# Plan for #4641 — dispatch.sh skips issues overlapping a parked run's draft PR when only the issue carries parked, and never reports the blocked queue

- [x] dispatch launches an issue whose named path only an unlabelled run draft PR `tdd/<p>-…` changes when issue `<p>` is labelled `parked`, printing no `skip` line for it ⟦criterion 1⟧
- [x] dispatch still skips an issue whose named path an unlabelled run draft PR changes when that PR's issue is not labelled `parked` ⟦criterion 2⟧
- [ ] when every solvable issue is skipped for overlap and no run is live, dispatch prints one `queue-blocked <pr-url>…` line naming each blocking PR, not again while that set is unchanged; documented in SCRIPTS.md and vdev's Watching list ⟦criterion 3⟧
