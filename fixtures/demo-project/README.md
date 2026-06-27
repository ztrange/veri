# veri demo project

A minimal, zero-dependency Python project used to demo the veri walking skeleton
(`/solve-issue`). It starts with **no implementation** and a single trivial passing
test, so the baseline suite is green.

- Test command: `python3 -m unittest discover -q` (run from this directory).
- Seeded feature: a `slugify(text)` function (see the seeded fixture issue).

## Demo

This project is meant to be run as its own git repository with a GitHub remote so
veri can read an issue, push a branch, and open a draft PR. See
[`../README.md`](../README.md) for the full procedure.
