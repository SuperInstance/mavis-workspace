#!/usr/bin/env python3
"""
CHARACTER SWAP — does the alphabet decide whether identity is recoverable?

The Asciipocalypse ramp is "@&#8x*,:. " mapped by depth. My probe measured
14/15 identity pairs indistinguishable under it. Two proposed fixes:

  ARM A  neutral ramp   — box-drawing / block glyphs, no lexical prior,
                          STILL MAPPED BY DEPTH. Isolates the alphabet.
  ARM B  role palette   — glyphs assigned to semantic ROLES, not to density
                          (the VLA paper's design; arXiv 2606.21470).

Plus a control arm. Ground truth = 6 objects at IDENTICAL depth, distinct colour.
"""
from collections import Counter

# the real ramp, and the three characters that are semantically loaded
DEPTH_RAMP = "@&#8x*,:. "
# ARM A: geometric glyphs only. None of these is a word, a tag, or a numeral.
NEUTRAL_RAMP = "█▓▒░│─┌┐└┘"          # blocks + box drawing
# ARM B: role palette. Position in the ramp is the ROLE, not a density.
ROLE_PALETTE = {0:" ", 1:"○", 2:"△", 3:"□", 4:"◇", 5:"▽", 6:"⬟", 7:"▣"}

def arm_scores(name, ramp_for, n_obj=6, N=24_000, seed=5):
    """6 objects, SAME depth, distinct identity.

    FAITHFUL TO Rasterizer.cs:129 — the glyph is a function of DEPTH, never of
    object identity.  My first version indexed the ramp by object number, which
    handed every object a different glyph and made the test unable to fail.  The
    control arm scored identically to the real arms, which is how I caught it.
    Here z is genuinely identical across objects, as it is in the real renderer.
    """
    z = 0.85                       # all six objects at ONE depth, as before
    objs = [(o, j) for o in range(n_obj) for j in range(4)]
    chars = {o: ramp_for(z, o) for o in range(n_obj)}
    # how many identity pairs share at least one rendered character?
    collide = sum(1 for i in range(n_obj) for j in range(i+1, n_obj)
                  if chars[i] == chars[j])
    pairs = n_obj*(n_obj-1)//2
    distinct = len(set(chars.values()))
    # can a learner recover identity from the character ALONE?
    by_char = {}
    for o, j in objs: by_char.setdefault(chars[o], []).append(o)
    learnable = sum(1 for c, os_ in by_char.items() if len(set(os_)) == 1)
    return dict(arm=name, distinct_glyphs=distinct, of_possible=n_obj,
                colliding_pairs=collide, total_pairs=pairs,
                identifiable_from_char=learnable)

print("  6 objects, IDENTICAL depth, 6 distinct identities.")
print("  Question: can the character channel tell them apart?\n")
rows = [
  # depth arms: glyph = f(z) ONLY. object identity is not an input, by construction.
  arm_scores("CURRENT  depth ramp @&#8x*,:. ", lambda z,o: DEPTH_RAMP[min(int(z**10*10), 9)]),
  arm_scores("ARM A    neutral ramp, still by depth", lambda z,o: NEUTRAL_RAMP[min(int(z**10*10), 9)]),
  # role arm: glyph = f(role). This is the ONLY arm that breaks the depth coupling.
  arm_scores("ARM B    role palette (by role)", lambda z,o: ROLE_PALETTE[o]),
  # CONTROL, corrected. My first control was (o*7+3)%10 -- INJECTIVE for o in 0..5,
  # so it was a role palette in disguise and scored like ARM B. A real control
  # must be NON-injective: many identities forced onto few glyphs.
  arm_scores("CONTROL  non-injective (must be bad)", lambda z,o: DEPTH_RAMP[o % 2]),
]
print(f"   {'arm':38} {'glyphs':>7} {'collide':>9} {'identifiable':>13}")
print("   " + "-"*72)
for r in rows:
    print(f"   {r['arm']:38} {r['distinct_glyphs']:>4}/{r['of_possible']} "
          f"{r['colliding_pairs']:>4}/{r['total_pairs']:>4} {r['identifiable_from_char']:>8}/{r['of_possible']}")
print()
ok = rows[0]
print(f"   CURRENT ramp collapses {ok['colliding_pairs']}/{ok['total_pairs']} identity pairs.")
print(f"   Role palette collapses {rows[2]['colliding_pairs']}/{rows[2]['total_pairs']}.")
print(f"   => NEUTRAL alphabet (ARM A) does NOT help. The glyph is a function of")
print(f"      DEPTH alone, so no alphabet can separate two things at one depth.")
print(f"   => Only breaking the DEPTH COUPLING works. The role palette wins not")
print(f"      because its glyphs are nicer but because they are assigned to")
print(f"      something other than distance. The bug was never the alphabet;")
print(f"      it was the assumption that a character channel should encode depth.")
