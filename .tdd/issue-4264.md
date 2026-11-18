# Plan for #4264 — The Draft PR step's lint wait has no total bound, so a lint that never exits keeps the conductor waiting for the life of the run

- [x] `detach-command.sh wait <name> --total <seconds>` on a command still running `<seconds>` after its `start` stops the command's process group and exits 2 with one stderr line naming the bound, never 3 ⟦criterion 1⟧
- [x] the `--total` bound counts from the command's `start`, not from the `wait` call: a `wait` called once the bound has already passed exits 2 at once, so repeated calls cannot extend it ⟦criterion 1⟧
- [x] `detach-command.sh wait` refuses a `--total` that is not a whole number with the usage line and exit 2, never a traceback
- [x] the `--total` stop signals no process group when the live pid is not the process the pid file recorded (its start time differs), so a recycled pid is never killed; `wait` exits 2
- [x] `DRAFT-PR.md`'s lint block waits under `VERI_LINT_TIMEOUT` (default 1800 s, counted from the lint's `start`), and on its expiry writes no `lint` event and a `### Lint` section saying the command did not finish within the bound and was stopped, neither bailing nor holding the PR ⟦criterion 3⟧
- [ ] `SCRIPTS.md`'s `detach-command.sh` entry says `wait` takes an optional total bound counted from `start`, past which the command is stopped with its process group and `wait` exits 2 naming the bound, never 3 ⟦criterion 3⟧
