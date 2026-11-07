### A `structural-pass` event with no `transforms` field (the `stopped=nothing-structural` mark the Draft PR step writes) counts in the Running block's refactor figures as one pass with 0 transforms, which landed nothing, and the report does not fail on it
- test-only | extract the repeated journal and report setup in test_status_report_running_refactor.py into one helper
