# #4278 plan

- [x] 1. After KILL, end_workers waits (bounded by GRACE) until every worker is gone, reaping it; both the idle and the TERM/HUP end go through it
