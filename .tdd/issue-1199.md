# Plan for #1199 — supervise.sh leaves a TERM-ignoring leaf running after killing it

- [x] When supervise.sh kills a leaf for being stuck (heartbeat silence), no process of that leaf's process group is left running afterwards, even when the group leader dies on SIGTERM and another member of the group ignores SIGTERM: the group gets SIGKILL once the grace period ends, judged by the group, not by the group leader alone ⟦criterion 1⟧
- [x] When supervise.sh kills a leaf for running past its hard timeout, no process of that leaf's process group is left running afterwards, even when the group leader dies on SIGTERM and another member of the group ignores SIGTERM ⟦criterion 1⟧
