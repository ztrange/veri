### Given a base sha, the production-frozen check exits 1 and names each path changed in `<base>..HEAD` that is not a test file by `transform-touches-tests.sh`'s rule ⟦criterion 1⟧
- production_frozen.py's inline usage print duplicates transform_touches_tests.refuse(); share it once a later step adds the unresolved-base refusal, which will duplicate the rev-parse check as well
