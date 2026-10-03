# Asciipocalypse as a JEV substrate — what the code says

2026-10-02. Read before building. **One correction to the design, and one
prediction that is already testable from a measurement I took three hours ago.**

---

## The substrate is better than the design assumed

`ASCII_FPS/Console.cs:1-55` is 55 lines and it is the entire observation surface:

```csharp
public char[,] Data  { get; set; }   // width × height
public byte[,] Color { get; set; }   // packed: R=3 bits, G=3 bits, B=2 bits
```

`ASCII_FPS.cs:303` is the whole render:

```csharp
int r = ((color & 0b111)           * 0b1001001) >> 1;   // 3 bits → 0..7
int g = (((color >> 3) & 0b111)   * 0b1001001) >> 1;   // 3 bits → 0..7
int b = ((color >> 6) & 0b11)     * 0b1010101;         // 2 bits → 0..3
spriteBatch.DrawString(Assets.font, console.Data[i,j].ToString(),
                       new Vector2(i,j) * Console.FONT_SIZE, ...);
```

**So a cell is a four-field fixed-width record: `(char, R:3, G:3, B:2, x, y)`.**

That is the PLATO tabulation shape and the `plato-tile-encoder` 384-byte record
lineage, and **it is already native here** — the game was written as a DOS-style
8-bit colour console. **The record discipline is not something to add.**

**And the text frame is a first-class object in the game's own architecture**, not
something reverse-engineered from pixels. The README says it outright: *"Everything
shown on the screen is first passed to a simple 8-bit color console simulation,
whose content is drawn to the screen every frame."*

**Casey's instinct is exactly right and the code confirms it: a text-only model
and a vision model can both work with this game, because the text *is* the
representation and the screen is its projection.**

---

## THE CORRECTION: a vision arm is NOT an independent instrument

The design pairs a text-only model with a vision model and treats them as two
readers. **They are the same call path.**

`console.Data[x,y]` → `DrawString` through `Assets.font` at `FONT_SIZE = 12` →
scaled to the window → screenshot → vision model.

**A vision model is reading the character buffer, re-rasterized and lossy-encoded.
It is downstream of the text arm in exactly the way that makes it useless as a
control**, and the account's own doctrine already says it:

> **A control using the same call path as the audited implementation cannot
> detect a fault in that path.**

Ensembling the two would manufacture the *appearance* of corroboration for free.
**This is the `n_eff ≈ 2` disease wearing a different hat** — and worse, because
here the `n_eff` is exactly 1 and it would still look like 2.

### What they ARE independent for — and it is more valuable

| question | better instrument | why |
|---|---|---|
| *where is the enemy* | **text / `Data`** | it reads the buffer, not a photograph of it |
| *can a player actually read this frame* | **vision** | only it sees the font raster, the 12px cell, the contrast |

> **These are not two opinions. They are two projections of one cell, discarding
> different information.** The useful question is not "do they agree" — they will,
> because they share a path — it is:

> **Does the ASCII rendering lose information that the text arm can read and a
> human cannot?**

**That is a legibility audit, and it is the question that decides whether this
substrate works at all.** Ensemble it as corroboration and you get nothing; audit
it for legibility and you get the real finding.

There is a **third arm** available that is *also* downstream of the same path but
discards a different field: read `Color[x,y]` alone, with no characters at all.

---

## A prediction that is already testable, from a measurement I took tonight

I measured a projection ladder three hours ago. Median recovery:

| level | projection | median |
|---|---|---|
| L0 | lossless | 0.8831 |
| L1 | colour-collapsed | **0.8947** |
| L3 | coarse | 0.6839 |
| L4 | hash64 | 0.5103 |
| L5 | stone count | 0.5000 |

> **Prediction: for this game, the char arm and the colour arm should be nearly
> equally informative, and collapsing to char-only should lose little.**

**If it holds, colour is decorative for strategy purposes and the text arm is
sufficient — which makes the cheapest possible agent viable.**
**If L1 drops sharply here, colour is carrying the enemy-detection load, the
text arm is blind to something a player can see, and the design is wrong.**

Either way it is a number, decided in an afternoon. **This is the first
prediction in `PREDICTIONS.md` that a lane can settle, and I am scoring it.**

---

## Why "tile makers and movers" is the right abstraction — and the trap in it

The enemy roster is finite and enumerable from source: `PoisonMonster`,
`BushMonster`, `SpinnyBoi`, `ShotgunDude`, `IceShotgunDude`, `Spooper`, `LavaPool`,
`Collectible`, plus the player. **That is eight tile kinds. A mover is a policy
over transitions between them.** That is the whole abstraction, and it is what
`plato-tile-encoder` and `patchwork`'s *"composition must be explicit"* are for.

**The trap, and it is specific to this game:**

> The README states the **z-buffer is also used to select which character is
> written to the console** — *"individualy selected per image pixel to add a
> greater sense of depth."*

**So the same 3D enemy renders as a DIFFERENT character at a different distance.**

**A mover scripted as "walk toward `@`" is chasing a depth-dependent glyph.** Any
autoplayer written against raw characters will thrash, and it will thrash in a way
that looks like bad policy rather than bad abstraction. **This is very likely why
naive player-bots fail on ASCII games generally, and it is the single thing to get
right before any JEV is introduced.**

**The tile must therefore be a function of (glyph, colour, neighbourhood), not
glyph alone.** A lone `x` is a wall; an `x` at the edge of a `|` corridor is a
doorway at a distance. **The tile is the glyph plus its context, and the context
is where the depth-encoding is decoded.**

---

## The pulse structure, and why ASCII earns it

| pulse | what runs | why it belongs there |
|---|---|---|
| **fast** | JEV over the enumerated move set | a cell record is 16 bytes; the enumeration is free |
| **fast** | the mover policy — local, no model | `r1-NOENGINE`; the bot plays with no model at all |
| **slow** | a system-two model redesigning the **tile taxonomy and the mover scripts** | the thing a fast loop cannot do: change what counts as a tile |

**This is `r1-SYNCOPATION` with the seam at the right place.** The slow layer does
not retune weights — it **renames the tiles and rewrites the movers**, which is a
different kind of change and exactly the kind a fast loop cannot make.

**The slow layer needs something the fast loop cannot give it: the archived
strategy with comments, and the index of what those comments were doing.** That
is `PIXELS-ARCHITECTURE.md`, and the ASCII substrate makes it cheap — **a frame
is `Data` and `Color` serialised, so the whole history is small enough to actually
keep, which is the one thing that was never true for the pixel version.**

---

## What would make me wrong

- If the font at `FONT_SIZE = 12` makes the screen genuinely illegible, the vision
  arm is the *only* useful reader and the text arm is reading a buffer no human
  can see — which would be a fascinating finding and would invert the design.
- If depth-encoding makes the glyph alphabet too unstable to build a taxonomy
  from, "tile makers" is the wrong abstraction and the tiles have to come from the
  3D scene graph instead — **which is available**, since the game is open source
  and the scene is right there. **That is the fallback, and it is a good one,
  because it is ground truth rather than a projection of it.**
- If the enemy roster is not the nine kinds I read from filenames, the taxonomy
  has to be derived by execution instead of by reading.
