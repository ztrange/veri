# Plan for #1261 — Cover the behaviour #988 refactors

- [x] A prompt built for the `diff` verify phase (`build-verify-prompt.sh diff <spec> <branch-base-sha> <step-base-sha>`) tells the verifier that the wrapper hands the test command's own exit status straight back, so a red run stays red; changing or dropping that sentence in `prompts/verify-diff.md` alone turns a suite under `make test` red
