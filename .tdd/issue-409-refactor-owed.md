### preserve-attempt.sh commits the worktree as it stands to a ref under refs/veri/attempts/ named by issue, step, phase and attempt, and git show reads that commit's tree back
- extract the throwaway-index snapshot (`GIT_INDEX_FILE` + `git add -A` + one git command) duplicated between `preserve-attempt.sh:32-35` and `verify.sh:143-149`'s `in_temp_index` into `lib/` — not applied here because the two error contracts differ (verify.sh fails open and prints nothing; preserve-attempt must fail loudly under `set -e`), so today it would need a policy parameter no test demands
### preserve-attempt.sh also copies the leaf's progress log and its final-output file to preserved names carrying the step, phase, attempt and the mark that triggered the preservation
- the `$([[ -e … ]] && echo yes || echo no)` existence readback is written twice (cases 4 and 6) and could be one `exists` helper
- the six `preserve "$repo" 409 3 develop-green 1 …` calls repeat the coordinates `REF` now states once; a wrapper taking only the repo and the optional mark would tie them together
### a REJECT or a malformed verdict makes verify.sh preserve that attempt, and the preserved names pair with the verdict event
- verify.sh:353-366 — fold the outer `if [[ "$word" != PASS ]]` and the inner four-condition guard into one condition, so `$trouble` and `$attempt` are derived only where they are read
### a killed-stuck leaf makes supervise.sh preserve that attempt, both on a retry and on the final killed-stuck exit
- fold supervise.test.sh case 35's two `printf '%s\n' "$X" | grep -c . || true` counts into one named helper
- fold case 35's two `while read … done <<< … | sort | xargs` extraction loops into one helper taking the per-line reader
