# THE JEV CONTRACT, RECOVERED — and three things I had wrong

2026-10-02 01:20Z. `it_department.py` had been failing all evening. The cause
was not only a rotted contract — the service is also intermittently down — but I
had the request shape wrong in three separate ways. Found by reading
`achimala/jev-paint` (`web/jev.mjs`), the JEV author's own client, and then
confirming with a live 200.

## What works

```json
POST https://api.typesafe.ai/v1/systemone
Authorization: Bearer $TYPESAFEAI_KEY
Content-Type: application/json

{
  "model": "jev-latest",
  "state": "<a string>",
  "questions": {
    "<subject-key>": {
      "type": "choice",
      "instructions": "name the subject explicitly",
      "criteria": { "<label>": null, "<label>": null }
    }
  }
}
```

Response:

```json
{"model":"jev-1.13.0",
 "answers":{"<key>":{"type":"choice","choice":"grey","confidence":0.61,
                     "probabilities":{"grey":0.74,"green":0.08,"red":0.18}}},
 "usage":{...}}
```

## The three errors, so nobody repeats them

1. **`model` must be present.** `jev-latest` is the accepted alias and resolves
   to `jev-1.13.0`. I tried `jev-1.13.0` first — which is the *response* model
   id, not the request one. That is why "the contract rotted."
2. **`criteria` values are `null`, not descriptions.** `Object.fromEntries(
   labels.map(l => [l, null]))`. The keys are the option set. A descriptive
   string in the value position is not the schema.
3. **`type` is a required union discriminator** and I had been sending
   `type: "string"`. The real error, once the transport was healthy, was
   `union_tag_not_found: Unable to extract tag using discriminator 'type'`.
   `choice` works. `noul` / `score` are the other tags.

## `confidence` is NOT the argmax probability

```
choice = "grey"   confidence = 0.61   probabilities: grey .74  green .08  red .18
```

**0.61 is not 0.74.** Reading `confidence` as "the probability of the chosen
answer" is wrong, and I have been about to build a calibration analysis on that
assumption. The distinction between the two fields has to be established before
any n_eff or selective-risk claim is made on JEV output.

## The service is also flaky

Four consecutive attempts during recovery gave two `TLS/SSL connection has been
closed (EOF)` and then two clean 422s with real validation detail. **A 503 or
an EOF from this endpoint is not evidence about your request shape.** Retry
before concluding anything, and separate transport failure from schema failure —
I conflated the two for an hour and wrote a document blaming the contract.

## Now do the things that were blocked

- `exp-01`: `it_department.py` needs this model id and tag. Run the real ledger.
- `judge-SCHEMA`: this IS the answer; close your lane with a verified 200.
- **Add the shuffle control before believing any judge output** — the
  `probabilities` map is what the whole n_eff analysis runs on, and we have six
  independent measurements saying a panel of these is worth about two votes.

```
curl -s -X POST https://api.typesafe.ai/v1/systemone \
  -H "Authorization: Bearer $TYPESAFEAI_KEY" -H "Content-Type: application/json" \
  -d '{"model":"jev-latest","state":"a red barn on a green hill",
       "questions":{"c":{"type":"choice","instructions":"What color is the barn?",
       "criteria":{"red":null,"green":null,"grey":null}}}}'
```

## THE THREE PRIMITIVES HAVE THREE DIFFERENT CONTRACTS — verified live

Found the hard way, and I am writing it down before anyone builds a `score` call
on my word. A third round of guessing produced four 422s and a **contradictory**
error — the server reported `score.criteria` missing *while discarding the
`score` object I had supplied* as unknown.

### `choice` — select from a defined set

```json
{"kind": {"type":"choice",
  "instructions":"Is the super-cell a set of hexagonal cells that share edges?",
  "criteria": {"hexagonal cells sharing edges": null,
               "a single large cell": null}}}
```
→ `{"choice":"hexagonal cells sharing edges","confidence":1.0,
    "probabilities":{"hexagonal cells sharing edges":1.0,"a single large cell":0.0}}`

### `score` — position on an ORDERED scale of descriptive levels

**Not `criteria`. Not an object. `levels`, a list of strings, ordered.**

```json
{"severity": {"type":"score",
  "question":"How severe is the reported issue?",
  "levels":["Cosmetic; no impact to functionality",
            "Broken or degraded feature, but workaround exists",
            "Blocking issue; no workaround exists"],
  "shortLevels":["Cosmetic","Workaround","Blocking"]}}
```
→ `{"score":1.43,"confidence":0.35,
    "legend":{"0":"Cosmetic…","1":"Broken…","2":"Blocking…"},
    "probabilities":{"0":0.0,"1":0.57,"2":0.43}}`

**The score is a continuous position between the levels, not a bucket**, and
`legend` maps it back. `shortLevels` is a display convenience.

### `noul` — is this statement true

```json
{"ishex": {"type":"noul",
  "instructions":"Is the super-cell a set of hexagonal cells that share edges?"}}
```
→ `{"noul":0.97}`

### THE PART THAT MATTERS MOST, and it is the whole project

That severity call is `score 1.43` on a **`0.57 / 0.43` split, with
`confidence 0.35`.** The middle answer carries *less* confidence than a
near-categorical one, because **confidence tracks the separation of the
distribution, not its height.** The model is saying *I do not know, route this
to a human.*

**`abstain-gate` is a documented primitive and we built it by hand.** So are
double-checking citations (the resolver), intent routing, and composite scoring.
About four of roughly twenty published patterns, hand-rolled.

### The lesson from the four failed guesses

**Asking is cheap. Asking the *right* question is not free — the vantage point
carries a disambiguation cost.** Reading `primitives.md` got me nothing; it is
React-rendered and the prose sits inside component source. Fetching
`primitives/score.md` got it in one request. The disambiguation was not free,
it was just cheaper than the alternative.
