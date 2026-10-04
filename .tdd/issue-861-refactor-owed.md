### `make test TESTS=<one shell suite>` runs that shell suite and no pytest case, so a red pytest case elsewhere under tests/py does not change its outcome ⟦criterion 1⟧
- test-only | make-test-env.test.sh sets the global `make_args` around one case and resets it by hand afterwards; passing it as an argument to `recipe` would remove the need for the reset
