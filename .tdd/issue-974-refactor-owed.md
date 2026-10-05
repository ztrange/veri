### `build-develop-prompt.sh diff <spec> <step> <test-cmd>` with the fast command left out exits 2 with a diagnostic on stderr and nothing on stdout ⟦criterion 1⟧
- test-only | the `"make unit"` fast-command literal repeated across the three diff cases in build-develop-prompt.test.sh could be one variable shared with `dd_fast`
### `build-develop-prompt.sh revise diff <spec> <step> <test-cmd> <reason-file> <fast-cmd>` prints a prompt that tells the revise leaf to run the given fast command through `{{TIMED_TEST_RUN}} fast` and then the affected suites, and to finish only with both green ⟦criterion 1⟧
- test-only | the #974 revise-diff case and the earlier diff case repeat the same fast/order/both-green check block in `build-develop-prompt.test.sh`; it could be one helper function
### `build-develop-prompt.sh revise diff <spec> <step> <test-cmd> <reason-file>` with the fast command left out exits 2 with a diagnostic on stderr and nothing on stdout ⟦criterion 1⟧
- test-only | build-develop-prompt.test.sh repeats the `"$BUILD" revise diff "$work/spec.md" "$dd_step" "$test_cmd" "$work/reason.md"` invocation across several cases; a small helper could hold it
