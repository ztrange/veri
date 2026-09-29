### a fixture suite that prints a non-count last line and exits 3 is reported as nothing to do, not as a suite that never reached its count line, and does not fail the target ⟦criterion 2⟧
- extract the repeated scratch-suite setup (mkdir tests, cp Makefile, write stub, chmod) into one helper in count-line-guard.test.sh
- extract the repeated make-run capture (`env -u VERI_TEST_CMD make -C … test`) into a helper in count-line-guard.test.sh
