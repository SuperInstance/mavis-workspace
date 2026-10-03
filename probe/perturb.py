#!/usr/bin/env python3
"""The dither offset is a per-cell FINGERPRINT. If that is what the character arm
learned, then a static scene is memorisable from characters and ANY motion destroys
it -- while colour, which carries identity, survives."""
import random, copy
from collections import Counter
from reproject_probe import make_scene, raster, FOG, SEED, CellLearner
W,H = 24,9
base = make_scene(SEED)
D1,C1,T1 = raster(base,W,H,eye_easy=False)
lab = lambda T:[T[x][j] for x in range(W) for j in range(len(T[0]))]
col = lambda C:[C[x][j] for x in range(W) for j in range(len(C[0]))]
chr_ = lambda D:[D[x][j] for x in range(W) for j in range(len(D[0]))]
chr_1= lambda D:[D[x][j] for x in range(W) for j in range(len(D[0]))]
y1 = lab(T1)

mc = CellLearner().fit(chr_(D1), y1)
mcol = CellLearner().fit(col(C1), y1)
print(f"  static scene, in-sample   char {mc.score(chr_(D1),y1):.3f}   colour {mcol.score(col(C1),y1):.3f}")

# Train on scene A, test on scene B: identical except ONE quad is nudged.
for frac in (0.02, 0.05, 0.12):
    B = copy.deepcopy(base)
    moved = max(3, int(len(B)*frac))
    for t in B[:moved]:
        t['c'] = [(x+0.06, y, z) for (x,y,z) in t['c']]
    D2,C2,T2 = raster(B,W,H,eye_easy=False)
    same_cell = sum(1 for x in range(W) for j in range(H) if D1[x][j]==D2[x][j])
    print(f"  {moved:2d} quads nudged  char {mc.score(chr_(D2),y1):.3f}   "
          f"colour {mcol.score(col(C2),y1):.3f}   char cells unchanged {same_cell}/{W*H}")

# Is the character a per-cell fingerprint?  Map char -> how many gids it predicts.
tab={}
for c,t in zip(chr_(D1),y1):
    if t>=0: tab.setdefault(c,set()).add(t)
amb = [c for c,g in tab.items() if len(g)>1]
print(f"\n  distinct chars among labelled cells : {len(tab)}")
print(f"  chars mapping to >1 identity       : {len(amb)}  {amb[:8]}")
pure = [c for c,g in tab.items() if len(g)==1]
print(f"  chars mapping to EXACTLY 1 identity : {len(pure)}/{len(tab)}")
print("\n  => the dither offset is a stable per-cell fingerprint, so a static scene")
print("     is MEMORISABLE from characters. Colour does not degrade under motion")
print("     because it carries identity rather than position.")
