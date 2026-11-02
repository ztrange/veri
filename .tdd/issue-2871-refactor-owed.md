### When the merge lock cannot be released during cleanup because merge-lock.sh cannot be started, queued-merge.sh prints its "merged, but cleanup failed: release" line and exits 2 rather than dying on a traceback
- extract the `_cleanup` spare-scripts copy (mkdtemp, RELEASE_FILES copy loop, rmtree) into a helper, so `_cleanup` reads as its steps
- wrap the spare directory's rmtree in try/finally so an exception between mkdtemp and rmtree can't leak it
not-done | no-predicate | extract the `_cleanup` spare-scripts copy (mkdtemp, RELEASE_FILES copy loop, rmtree) into a helper, so `_cleanup` reads as its steps
not-done | no-predicate | wrap the spare directory's rmtree in try/finally so an exception between mkdtemp and rmtree can't leak it
