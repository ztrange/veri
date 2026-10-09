# Plan for #1250 — orchestrate.sh crashes with a traceback and exit 1 on a non-numeric VERI_CONDUCTOR_STOP_TIMEOUT, and 0 drains forever

- [x] Through orchestrate.sh, a non-numeric VERI_CONDUCTOR_STOP_TIMEOUT (`abc`) exits 2 before any conductor starts, with one stderr line naming the variable and the value and no traceback ⟦criterion 1⟧
- [x] Through orchestrate.sh, a non-finite VERI_CONDUCTOR_STOP_TIMEOUT (`nan`, `inf`) is refused the same way: exit 2 before any conductor starts, one stderr line naming the variable and the value ⟦added⟧ ⟦criterion 1⟧
- [x] Through orchestrate.sh, a zero or negative VERI_CONDUCTOR_STOP_TIMEOUT (`0`, `-1`) is refused the same way: exit 2 before any conductor starts, one stderr line naming the variable and the value ⟦criterion 1⟧
- [ ] An unset or empty VERI_CONDUCTOR_STOP_TIMEOUT bounds the stopped conductor's drain at 10 s, and a positive value (`0.5`) is used as the bound as given ⟦criterion 2⟧
