# Plan for #656 — unit-tier.test.sh case 5 says it pins four shims but only watches git's and gh's

- [ ] unit-tier.test.sh case 5 fails, naming itself, when tests/unit-guard/python3 is deleted: under `make unit` a fixture suite that runs real python3 must make the run fail with a line naming python3 ⟦criterion 1⟧
- [ ] unit-tier.test.sh case 5 fails, naming itself, when tests/offline/curl is deleted: under `make unit` a fixture suite that runs real curl must make the run fail with a line naming curl ⟦criterion 2⟧
- [ ] the diff to unit-tier.test.sh touches case 5 only — cases 1–4 and 6 keep their names and assertions as on origin/main, checked by reading the PR diff ⟦human-owed⟧ ⟦criterion 3⟧
