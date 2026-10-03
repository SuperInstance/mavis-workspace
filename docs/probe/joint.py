#!/usr/bin/env python3
"""
JOINT RECOVERY — is the CURRENT renderer actually broken?

Last experiment showed the character channel cannot see identity.  That is true
and it may be irrelevant.  The question nobody asked:

  Does the frame, AS A WHOLE, carry enough to recover (identity, depth)?

  Current (EyeEasy OFF): char = f(depth), color = texture(identity)   -> two
                          channels, two quantities.  Joint should be exact.
  EyeEasy ON            : char = '@' (constant), color = identity*depth -> ONE
                          number for two unknowns.  Joint may be ill-posed.

If current wins on joint recovery, the character channel is not a bug.  It is
carrying its load correctly and I was grading it on the wrong axis.
"""
from fractions import Fraction

# 6 identities x 3 depths, full grid. Colour values are DISTINCT so that
# (identity, depth) is identifiable in principle.
IDS   = ['monster','spinner','bush','shotgun','spooer','collectible']
DEPTHS = [0.82, 0.88, 0.94]
FOG = "@&#8x*,:. "
def fogid(z):  return FOG[min(int(z**10*10), 9)]

# per-identity base colour, 3-bit-ish integers
base = {n: (40+17*i, 90+11*i, 30+7*i) for i,n in enumerate(IDS)}

def current_frame():
    """EyeEasy OFF. Returns {(id,depth): (char, color)}"""
    return {(n,z): (fogid(z), base[n]) for n in IDS for z in DEPTHS}

def eyeeasy_frame():
    """Rasterizer.cs:124. Every cell '@'; colour = texture * d, d from depth."""
    out = {}
    for n in IDS:
     for z in DEPTHS:
        d = max(0.0, min(1.0, 1.0 - z**25))     # the real formula
        r,g,b = base[n]
        out[(n,z)] = ('@', (r*d, g*d, b*d))
    return out

def report(name, frame, separable):
    """Can (identity, depth) be recovered from the rendered cell alone?"""
    # group cells by rendered char; can we read depth from it?
    char_to_depth = {}
    for (n,z),(c,col) in frame.items():
        char_to_depth.setdefault(c, set()).add(z)
    depth_recoverable = all(len(v)==1 for v in char_to_depth.values())
    # group by rendered colour; can we read identity from it?
    col_to_id = {}
    for (n,z),(c,col) in frame.items():
        col_to_id.setdefault(tuple(round(v,6) for v in col), set()).add(n)
    id_recoverable = all(len(v)==1 for v in col_to_id.values())
    # JOINT: given ONLY the rendered cell, is (n,z) determined?
    cellmap = {}
    for (n,z),(c,col) in frame.items():
        cellmap.setdefault((c, tuple(round(v,6) for v in col)), set()).add((n,z))
    joint = all(len(v)==1 for v in cellmap.values())
    print(f"  {name:34} chars={len(char_to_depth):>2}  "
          f"depth-from-char={'YES' if depth_recoverable else 'NO ':>3}  "
          f"identity-from-colour={'YES' if id_recoverable else 'NO ':>3}  "
          f"JOINT={'EXACT' if joint else 'AMBIGUOUS':>9}")
    return joint, depth_recoverable, id_recoverable

print("  6 identities x 3 depths = 18 cells. Can the cell give back both?\n")
j1,d1,i1 = report("CURRENT (EyeEasy OFF)", current_frame(), True)
j2,d2,i2 = report("EyeEasy ON (char='@', col=x d)", eyeeasy_frame(), False)
print()
print(f"  CURRENT: depth {'recoverable' if d1 else 'LOST'}, identity {'recoverable' if i1 else 'LOST'}, joint {'EXACT' if j1 else 'ambiguous'}")
print(f"  EyeEasy: depth {'recoverable' if d2 else 'LOST'}, identity {'recoverable' if i2 else 'LOST'}, joint {'EXACT' if j2 else 'ambiguous'}")
print()
if j1 and not j2:
    print("  => THE CURRENT RENDERER IS CORRECT. The character channel is not a bug;")
    print("     it carries depth, colour carries identity, and together the frame is")
    print("     fully invertible. EyeEasy FUSES two quantities into one number,")
    print("     which is an irreversible projection (L4) even though it looks cleaner.")
    print()
    print("     My previous conclusion was wrong because I graded ONE channel on the")
    print("     job of TWO. The seam is not in the renderer. It is in the observer.")
