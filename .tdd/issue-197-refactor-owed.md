### A local branch absent from origin is reported, naming the branch, its tip, how many commits it holds that origin does not, and the worktree holding it when there is one
- cases 4 and 6 of invisible-work.test.sh both build a local branch that origin lacks, one in a worktree and one in the clone's own checkout; the setups differ enough that a shared helper would need a parameter no test yet requires
### The script exits 2 with a diagnostic on stderr and empty stdout when the remote is unreachable or gh cannot be read
- the two `echo … >&2; exit 2` diagnostic blocks in invisible-work.sh could share one `die` function (two 2-line uses; too little to be worth it)
