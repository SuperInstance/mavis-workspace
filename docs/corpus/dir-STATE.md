# dir-STATE — state, data, and time (RESEARCH LANE, in progress)

**Status: STUB as of 2026-10-02T02:30Z. One measured fact, per instruction.**

## Fact 1 (measured, this session): the 18 "inaccessible" databases are
## not recorded as inaccessible. They are recorded with a *transport* error.

`d1_inventory.json` labels 18 of 44 databases `INACCESSIBLE` and stores, for
every one of them, the same 68-character string:

```
upstream connect error or disconnect/reset before headers. retried and the lates
```

Three measured things about that string, none of them "inaccessible":

1. **It is the wrong error class.** I probed
   `GET /accounts/049ff5e84ecf636b53b162cbb580aae6/d1/database` unauthenticated
   just now: **HTTP 401** in **115 ms**, with a structured body
   `{"success":false,"errors":[{"code":10000,"message":"Authentication error"}]}`.
   The API is up, reachable, and answering in ~0.1 s. A real permission problem
   in this fleet looks like a `success:false` JSON body, not a socket error.
   **No 401/403/`code:10000` appears anywhere in the 18.**
2. **It is identical for all 18.** A per-database property — permission, a bad
   UUID, an empty database — does not produce one identical string 18 times.
   A property of the *observer* does.
3. **It is truncated mid-word** at `lates`. The receipt stored 68 characters and
   cut the sentence that would have said what actually happened on the retry.

So the 18 are **UNVERIFIABLE**, not inaccessible, and the fleet's own
denominator (26 of 44) rests on a cause that has never been established.
`quilt-canon` is in that 18 — see §2 below when it lands.

**Rule this suggests:** a status column must record the *class* of failure
(transport / auth / not-found / empty) separately from the observation, or the
observer's own behaviour becomes the system's recorded history. That is a
time-and-state bug wearing a permissions costume.

---
*Stub. Full lane report follows in this file.*
