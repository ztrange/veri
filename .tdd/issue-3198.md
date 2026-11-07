# Plan for #3198 — status.sh --report's zone line drops a half-hour offset: IST prints UTC+5

- [ ] status.sh --report's zone line keeps a non-zero offset's minutes: with TZ=Asia/Kolkata it names UTC+5:30 and with TZ=Asia/Kathmandu UTC+5:45, while a whole-hour zone (TZ=America/Chicago in winter) still names UTC−6 as the existing case pins; a small in-process run_cli case, no real process ⟦criterion 1⟧
