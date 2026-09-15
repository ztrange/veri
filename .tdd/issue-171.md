# Plan for #171 — Each leaf role's model is a tunable, so a run can put developer leaves on Sonnet

- [x] leaf-model.sh prints VERI_MODEL for a leaf of either role, and nothing when no variable is set
- [x] A role variable beats VERI_MODEL for that role's leaves only — VERI_MODEL_DEVELOPER for develop-* and revise-*, VERI_MODEL_VERIFIER for verify-*
- [x] leaf-model.sh exits 2 with a diagnostic on a value containing whitespace and on a leaf name leaf-role.sh refuses, while opus[1m] is accepted
- [x] supervise.sh resolves the model once beside the role, and its launch event carries model= — the resolved value, or "" when none
- [x] A supervised leaf's claude argv carries --model only when the resolved model is non-empty, byte-identical to today when unset
- [x] SKILL.md preflight runs leaf-model.sh for a developer and a verifier name, so a bad value stops the run before any branch or leaf
- [x] An ambient VERI_MODEL in the calling shell does not change any suite's result, pinned by hermetic-suites.test.sh
- [ ] VERIFY_LEAF_ARGS carrying its own --model alongside a role variable is resolved by a stated rule, not by flag order
- [ ] SKILL.md's supervise.sh bullet and CLAUDE.md name the three tunables and why developer and verifier are separate knobs, with CLAUDE.md's script and suite counts moved
