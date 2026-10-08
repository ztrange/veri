# Plan for #1126 — orchestrate.sh starts each conductor with SIGPIPE and SIGXFSZ ignored

- [ ] a conductor started by orchestrate.sh has SIGPIPE at its default disposition: a writer to a closed pipe inside it dies of SIGPIPE (status 141 in a bash pipeline), not of EPIPE ⟦criterion 1⟧
- [ ] a conductor started by orchestrate.sh has SIGXFSZ at its default disposition ⟦criterion 2⟧
- [ ] the conductor started by orchestrate.sh is still the leader of a new session whose pid orchestrate records, with stdin /dev/null and orchestrate's stderr, and SIGINT and SIGQUIT still ignored ⟦criterion 3⟧
- [ ] a conductor orchestrate.sh stops is stopped by SIGTERM to its process group, never by its writes failing ⟦criterion 4⟧
