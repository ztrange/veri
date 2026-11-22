# Plan for #4627 — A leaf killed-stuck at the hard timeout names no in-flight tool call, so a hung test run bails killed-stuck with no cause

- [x] A leaf killed-stuck while its stream log's last `tool_use` has no `tool_result` gets a kill reason, on `supervise.sh`'s stderr status line and in its `exit` event's `cause`, naming that tool call's command and the seconds it ran ⟦criterion 1⟧
- [ ] A leaf killed-stuck while its stream log's last `tool_use` has its `tool_result` keeps today's kill reason, unchanged ⟦criterion 1⟧
- [ ] The in-flight tool call's command is named by its first line only, cut to a bounded length ⟦criterion 1⟧
