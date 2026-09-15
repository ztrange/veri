# A preamble token is priced per night, at a counted request volume

A file that is auto-loaded is not read once — it is re-sent, and re-billed at cache-read
rates, on **every request of every session that loads it**. So the unit that matters when
someone is about to add a page of prose to `CLAUDE.md` or `skills/tdd/SKILL.md` is not the
file's size and not the share of a bill some past cut once saved. It is a rate:

> **One preamble token resident in every request costs ~$0.0019 per night — about $1.90
> per thousand tokens — at 1,285 requests a night.** A token resident only in a
> conductor's requests costs ~$0.00062 a night, ~$0.62 per thousand, at 410 of them.

Measured on the overnight run of **2026-09-14 22:00 → 2026-09-15 06:08**, and quoted with
that date because a price per night is meaningless without the night it was counted on: a
later run at a different volume supersedes this figure rather than proving it wrong.

## Context

That night ran **1,285 deduplicated requests** across 94 sessions for **$313**, of which
**410 requests were conductors**. The rate is arithmetic on those counts and the
cache-read price of $1.50 per million tokens: a token in every request is read 1,285
times, 1,285 × $1.50/MTok = $0.0019; a token only a conductor loads is read 410 times,
$0.00062.

Applied to the two files that were the subject of issue #202 it reproduces what that issue
measured, which is the check that the rate is the right unit:

| resident in | tokens | × rate | per night |
|---|---|---|---|
| `skills/tdd/SKILL.md` — every conductor request | 19,449 | $0.00062 | ~$12 |
| `CLAUDE.md` — every request made in this repo | 3,607 | $0.0019 | ~$7 |
| #202's scope-loop cut, out of `SKILL.md` | −1,676 | $0.00062 | −$1.03 |

Stating it as ~6% of a night instead was the framing that made the decision hard. A
percentage prices only the cut that was already made; it cannot price the paragraph in
front of you. A reader who knows the rate can multiply before writing.

Rejected: **a maximum size, asserted by a test**, on either file. The counter-argument is
real and #161 recorded it — a byte that stops one bad leaf pays for itself many times over,
and four suites pin `CLAUDE.md`'s content for exactly that reason. A cap would make the
cheap file the good one, which is the wrong objective; the price is an input to a judgement,
not the judgement. Also rejected: **a figure recomputed by a script at build time**, because
the run it would read is a different run every night and the point of a record is that it
holds still and can be seen to be out of date.

## Consequences

Prose added to an auto-loaded file can be priced before it is written: tokens × the rate
above. Prose that only one phase needs can be moved behind a `Read` and drops to zero,
which is what #202 did with the scope loop — at the cost, weighed there and declined for
the bail and revise paths, that a conductor which must read a file before it can act might
fail to read it.

The figure goes stale by design. It rests on one night's volume and on a cache-read price
neither veri nor this repo sets, so a later measurement replaces it by superseding this
ADR, with its own date and its own counts.
