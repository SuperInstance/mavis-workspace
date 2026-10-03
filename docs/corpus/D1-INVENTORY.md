# D1 inventory — orchestrator read, 2026-10-01 20:52Z

Three lanes have now been blocked on `CLOUDFLARE_TOKEN` not being present in a
spawned session's environment. Rather than keep re-dispatching, I ran the reads
myself with a read-only gate (assert every statement starts with
`SELECT`/`PRAGMA`/`WITH`; refuse anything else). Raw output:
`d1_inventory.json` in this directory.

## Headline

**44 databases. 467 tables. 26 non-empty, 18 inaccessible.**

`INACCESSIBLE` is **not** `EMPTY` and I have not conflated them. The 18 returned
an error from the query endpoint rather than an empty result set; the difference
matters and a later report must keep it.

## The 26 non-empty, by table count

| database | tables |
|---|---:|
| `spreadsheet-moment-db-prod` | 110 |
| `tap-db` | 91 |
| `lucineer-memory` | 50 |
| `crab-trap-catches` | 28 |
| `hermit-crab-memory-db` | 21 |
| `baton-router-db` | 20 |
| `superinstance-db` | 18 |
| `craftmind-rsi` | 17 |
| `shoal-db` | 12 |
| `deckhand-index` | 11 |
| `hermes-reference-frames` | 11 |
| `mist-quilt-db` | 11 |
| `fleet-functions-db` | 9 |
| `scrap-spark` | 9 |
| `harness-experiments` | 9 |
| `activelog-sessions` | 8 |
| `ship-log-db` | 6 |
| `scrap-voice-db` | 5 |
| `conservation-api` | 5 |
| `fleet-telemetry` | 5 |
| `construct-feed` | 4 |
| `harness-cycles` | 3 |
| `scrapcraft-db` | 1 |
| `luciddreamer-db` | 1 |
| `fleet-budget` | 1 |
| `spreadsheet-moment-db-dev` | 1 |

## The table that made me stop

`superinstance-db` contains:

```
_cf_KV, rooms, sqlite_sequence, tiles, tile_versions,
demotion_receipts, intents, bookings
```

**`demotion_receipts`.** That is a witness record for a claim leaving canon —
the no-deletion and canon doctrines, implemented in a live production edge
database, in a namespace that has 5,127 public repositories and a standing
doctrine about cells being scars and the record being canonical.

Two things follow, and both matter more than the table count:

1. **The doctrine is already deployed and I did not know.** Somewhere in this
   account there is a running system that keeps receipts when something is
   demoted from belief. That is the single most interesting thing in the
   inventory and it was found by listing tables, not by reading any document.

2. **It is the strongest available answer to the git-competition question.**
   The entry argues that the next generation of git should commit *adjudication*
   and preserve losing claims rather than discarding them. **A production
   database already has a `demotion_receipts` table.** That is not a proposal,
   it is a precedent, and it is the kind of artifact a judge cannot dismiss as
   vaporware.

## What the next step is, and what it is not

**Is:** read `demotion_receipts` and `tiles`/`tile_versions`, find out what
actually gets written when a claim is demoted, and check whether the schema
matches the doctrine or contradicts it.

**Is not:** a claim that the system is correct. Tonight's pattern is that
well-formed, checkable, wrong artifacts are the norm — `quilt-tools#32/#33` are
both true and cannot be line-merged; a `6.8×` constant sits in two passing
property tests; a 64-bit hash outscores the complete board on a random split.
**A table named `demotion_receipts` is a hypothesis about behaviour, not
evidence of it.** Verify the write path or do not claim it.

Also unresolved: **18 of 44 are inaccessible and I have not established why.**
Empty, permissions, or a bad UUID would all look similar from here, and the
difference changes the denominator. Do not report 44 as inspected.
