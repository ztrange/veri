file 37
skills/tdd/scripts/veri/merge_lock.py
old 61
code = subprocess.run(args[args.index("--") + 1:]).returncode
new 73
code = subprocess.run(args[args.index("--") + 1:], cwd="/tmp").returncode
command 80
make test TESTS=skills/tdd/scripts/tests/py/test_merge_lock_gate_push_process.py

