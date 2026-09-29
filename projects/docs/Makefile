# Docs project targets. Run from the repo root with `make -C projects/docs <target>`.
COUNT_LINE := ^[0-9]+ passed, [0-9]+ failed$$
COUNTLESS := %s: never reached its count line\n

DEV_RUN_GUARD := case "$${VERI_TEST_CMD:-}" in \
	  ''|'make docs'*) ;; \
	  *) printf 'refusing: VERI_TEST_CMD=%s is set, so this is a development run, and a development run never owes a page build.\n' "$${VERI_TEST_CMD}" >&2; \
	     exit 2 ;; \
	esac

DOCS_TESTS := $(sort $(wildcard tests/*.test.sh))

.PHONY: docs test fresh check
docs:
	@$(DEV_RUN_GUARD)
	@python3 build-walkthrough.py

test:
	@$(DEV_RUN_GUARD)
	@fail=0; suite_out="$$(mktemp)"; suite_status="$$(mktemp)"; \
	trap 'rm -f "$$suite_out" "$$suite_status"' EXIT; \
	for t in $(DOCS_TESTS); do \
	  suite_name="$$(basename "$$t")"; \
	  printf '== %s\n' "$$suite_name"; \
	  { "$$t" < /dev/null; echo $$? > "$$suite_status"; } | tee "$$suite_out"; \
	  [ "$$(cat "$$suite_status")" -eq 0 ] || fail=1; \
	  last_line="$$(tail -n 1 "$$suite_out")"; \
	  printf '%s\n' "$$last_line" | grep -E '$(COUNT_LINE)' > /dev/null || { \
	    printf '$(COUNTLESS)' "$$suite_name"; fail=1; \
	  }; \
	done; \
	echo "----"; \
	if [ $$fail -eq 0 ]; then echo "all suites green"; else echo "SUITES FAILED"; exit 1; fi

fresh:
	@$(DEV_RUN_GUARD)
	@python3 check-walkthrough.py

check: test fresh
