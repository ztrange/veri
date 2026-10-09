**Signal only processes you started**, by the pid you recorded when you started them —
never by name or pattern (`pkill`, `killall`, `kill $(pgrep …)`). A pattern matches every
process on the machine, so it reaches another live run's supervisor and leaves. Name an
experiment's processes and leaves with the `exp-` prefix, which no live run uses.
