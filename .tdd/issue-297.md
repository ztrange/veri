# Plan for #297 — skill-leaf-env.test.sh passes when a launch's leaf name is wrong: it waits out VERI_TIMEOUT instead of failing

- [x] A launch that writes no completion file under the leaf name the probe derived is reported as a failing launch line, naming that line, instead of being read back from the stub's file and passed ⟦criterion 1⟧
- [ ] The probe stops waiting on a launch once that launch's supervisor is no longer running, rather than waiting out its whole fixed wait budget, so a derived name no launch writes is answered promptly ⟦criterion 2⟧
