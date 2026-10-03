#!/usr/bin/env python3
"""The invariance test. Learns identity from ONE projection, tested on others."""
import random, math
from collections import Counter
from reproject_probe import make_scene, raster, FOG, SEED, CellLearner

W,H,W2,H2 = 24,9,36,13
scene = make_scene(SEED)
D1,C1,T1 = raster(scene,W ,H ,eye_easy=False)
D2,C2,T2 = raster(scene,W ,H ,eye_easy=True )
D3,C3,T3 = raster(scene,W2,H2,eye_easy=False)

lab = lambda T,cols:[T[x][j] for x in range(cols) for j in range(len(T[0]))]
col = lambda C,cols:[C[x][j] for x in range(cols) for j in range(len(C[0]))]
chr_ = lambda D,cols:[D[x][j] for x in range(cols) for j in range(len(D[0]))]

print("  ═══ the SAME scene, three renderings ═══")
occ1=Counter(chr_(D1,W)); occ3=Counter(chr_(D3,W2))
print(f"  glyph occupancy {W}x{H}   : {dict(occ1.most_common())}")
print(f"  glyph occupancy {W2}x{H2} : {dict(occ3.most_common())}")
print(f"  glyphs used: {len(occ1)} of 10 at {W}x{H}, {len(occ3)} of 10 at {W2}x{H2}")
same = sum(1 for x in range(W) for j in range(H) if D1[x][j]==D2[x][j])
print(f"  EyeEasy OFF vs ON: {same}/{W*H} character cells identical ({same/(W*H)*100:.0f}%)")

y1 = lab(T1,W)
m  = CellLearner().fit(col(C1,W), y1)

print("\n  ═══ learner: colour-cell -> identity, trained on ONE rendering ═══")
print(f"  in-sample, EyeEasy OFF  {W}x{H} : {m.score(col(C1,W), y1):.3f}")
print(f"  same scene, EyeEasy ON  {W}x{H} : {m.score(col(C2,W), y1):.3f}   <- re-projection")
print(f"  same scene, EyeEasy OFF {W2}x{H2}: {m.score(col(C3,W2), lab(T3,W2)):.3f}   <- re-resolution")

print("\n  ═══ the CHARACTER arm, same train/test discipline ═══")
mc = CellLearner().fit(chr_(D1,W), y1)
print(f"  char-cell -> identity, in-sample      : {mc.score(chr_(D1,W), y1):.3f}   <- expect ~0: char carries NO identity")
print(f"  char-cell -> identity, EyeEasy ON     : {mc.score(chr_(D2,W), y1):.3f}")

print("\n  ═══ NEGATIVE CONTROLS — must score badly, and must NOT match the real arm ═══")
r=random.Random(5)
print(f"  C1 colour randomised, same labels     : {m.score([r.randrange(256) for _ in col(C1,W)], y1):.3f}")
print(f"  C2 char noise, same alphabet          : {mc.score([r.choice(list(FOG)) for _ in chr_(D1,W)], y1):.3f}")
print(f"  C3 identity labels shuffled           : {m.score(col(C1,W), r.sample(y1,len(y1))):.3f}")
chance = sum(1.0/c for c in Counter([t for t in y1 if t>=0]).values())/max(1,len([t for t in y1 if t>=0]))
print(f"\n  chance for this label distribution    : {chance:.3f}")
print(f"  labelled cells                        : {sum(1 for t in y1 if t>=0)}/{len(y1)}")
