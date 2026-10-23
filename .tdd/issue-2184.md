# Plan for #2184 — pytest_leg leaks its veri-pytest-* temp folder when the leg is killed by SIGKILL or SIGHUP

- [x] A pytest leg sent SIGHUP while its pytest run is going removes its veri-pytest-* folder and exits as it does on SIGTERM, pinned by a process case that sends SIGHUP to a running leg and finds no folder left ⟦criterion 1⟧
- [x] When a pytest leg's main returns, the SIGHUP handler in force before it started is in force again ⟦criterion 1⟧
- [x] A pytest leg records its own pid in its veri-pytest-* folder when it creates it, readable there while its pytest run is going ⟦criterion 2⟧
- [ ] At start a pytest leg removes a veri-pytest-* folder in the TMPDIR it uses whose recorded pid no longer answers kill -0, deciding by that dead-pid check alone and never by the folder's age ⟦criterion 2⟧
- [ ] At start a pytest leg keeps a veri-pytest-* folder whose recorded pid answers kill -0, whether that pid is another running leg or an unrelated live process that reused it ⟦criterion 2⟧
- [ ] At start a pytest leg keeps a veri-pytest-* folder with no recorded pid, and one whose record cannot be read or parsed as a pid ⟦criterion 3⟧
- [ ] The start-up sweep never touches an entry in the TMPDIR not named veri-pytest-*, even one recording a dead pid, nor anything outside the TMPDIR the leg uses ⟦criterion 3⟧
