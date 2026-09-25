// veri — one binary, one subcommand per ported script. The .sh files under scripts/ are
// thin shims that exec `veri <script-name>`, so the CLI contract (name, args, stdout,
// stderr, exit code) is the shim's and stays byte-identical to the bash it replaced.
//
// Usage: veri parse-verdict | push-branch
package main

import (
	"fmt"
	"os"
	"path/filepath"

	"veri/pushbranch"
	"veri/verdict"
)

// scriptsDir is where the sibling scripts a port still calls (event.sh) live: the shim
// says so in VERI_SCRIPTS_DIR; a binary run by hand falls back to go/bin/../.. — the
// scripts directory the binary is built under.
func scriptsDir() string {
	if d, ok := os.LookupEnv("VERI_SCRIPTS_DIR"); ok && d != "" {
		return d
	}
	exe, err := os.Executable()
	if err != nil {
		return "."
	}
	return filepath.Join(filepath.Dir(exe), "..", "..")
}

func main() {
	if len(os.Args) < 2 {
		fmt.Fprintln(os.Stderr, "usage: veri <parse-verdict|push-branch> [args …]")
		os.Exit(2)
	}
	switch os.Args[1] {
	case "parse-verdict":
		os.Exit(verdict.Main(os.Stdin, os.Stdout, os.Stderr))
	case "push-branch":
		os.Exit(pushbranch.Run(pushbranch.ProcessDeps(scriptsDir())))
	default:
		fmt.Fprintf(os.Stderr, "veri: unknown subcommand '%s'\n", os.Args[1])
		os.Exit(2)
	}
}
