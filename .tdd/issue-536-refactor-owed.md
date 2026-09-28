### A shell that set an EXIT trap before calling `bg_start` still runs that earlier trap at exit, and still gets the survivor report for a process left running ⟦criterion 1⟧
- extract the shared "start victim in a subshell, wait for the record, check it survived, grep stderr for its pid" setup that case 5 repeats from case 2 in background-kill.test.sh
### A shell that set an EXIT trap and then calls `bg_start` more than once, with the same record and with a second record, reports each survivor exactly once and runs its own earlier trap exactly once ⟦criterion 2⟧
- case 6 loops over the same three pids twice (checks, then `end_victim`); the `end_victim` call could fold into the first loop
