### A shell that set an EXIT trap before calling `bg_start` still runs that earlier trap at exit, and still gets the survivor report for a process left running ⟦criterion 1⟧
- extract the shared "start victim in a subshell, wait for the record, check it survived, grep stderr for its pid" setup that case 5 repeats from case 2 in background-kill.test.sh
