# vendor/

Third-party source vendored into this repo, for the spike evaluating whether veri's test
suites should move to a framework. Nothing here is veri's own code, and nothing here is
edited: a vendored tree that has been patched is no longer the thing the spike measured.

## shellspec/

| | |
|---|---|
| Version | 0.28.1 |
| Released | 2021-01-11 |
| Source | <https://github.com/shellspec/shellspec/releases/download/0.28.1/shellspec-dist.tar.gz> |
| sha256 | `350d3de04ba61505c54eda31a3c2ee912700f1758b1a80a284bc08fd8b6c5992` |
| Size | 76 KB compressed, 612 KB extracted, 127 files, all text |
| License | MIT (`shellspec/LICENSE`) |
| Vendored | 2026-09-19 |

Vendored rather than installed because CLAUDE.md's testing idiom commits to zero
dependencies: an install step would have to run on the development Mac, on the CI runner
on every job, and on any machine running veri against this repo. The tree is pure POSIX
shell, so vendoring costs nothing but the bytes.

**0.28.1 is the latest release, and it is from January 2021.** The project is not archived
and its default branch still takes commits (most recently 2024-09), but five years without
a release is a fact the adoption decision owes a line to, not a detail. Re-check before
adopting.

To re-fetch and verify:

```sh
curl -sSL -o shellspec-dist.tar.gz \
  https://github.com/shellspec/shellspec/releases/download/0.28.1/shellspec-dist.tar.gz
shasum -a 256 shellspec-dist.tar.gz   # must match the sha256 above
```
