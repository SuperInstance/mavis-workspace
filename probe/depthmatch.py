#!/usr/bin/env python3
"""DECISIVE: two objects at IDENTICAL depth, different identity.
If the character carries identity, they differ. If it carries only depth, they match.
This needs no learner -- the answer is a property of the projection."""
import random
from collections import Counter
from reproject_probe import make_scene, raster, SEED, quad_at, hsv
W,H = 24,9

# 6 objects, ALL at z=0.85 (mid informative band), 6 distinct colours/identities
scene=[]
for k in range(6):
    cx = -0.5 + 1.0*(k%3)/2.0
    cy = -0.15 + 0.3*(k//3)
    scene.append(quad_at(0.85, hsv(k/6.0,0.9,0.95), k, cx, cy, 0.14, 0.11))
D,C,T = raster(scene,W,H,eye_easy=False)

cells=[(x,j) for x in range(W) for j in range(H) if T[x][j]>=0]
by_gid={}
for x,j in cells: by_gid.setdefault(T[x][j],[]).append((D[x][j], C[x][j]))

print("  6 objects, ALL at z=0.85, six distinct identities:\n")
print("   gid  n   distinct CHARS   distinct COLOURS")
for g in sorted(by_gid):
    v=by_gid[g]
    print(f"   {g:3d} {len(v):3d}      {len(set(c for c,_ in v)):2d}              {len(set(k for _,k in v)):2d}")

chars_by_gid={g:set(c for c,_ in v) for g,v in by_gid.items()}
collide=0; tot=0
gs=sorted(by_gid)
for i in range(len(gs)):
    for j in range(i+1,len(gs)):
        tot+=1
        if chars_by_gid[gs[i]] & chars_by_gid[gs[j]]: collide+=1
print(f"\n  identity pairs sharing at least one character : {collide}/{tot}")
print(f"  character channel distinguishes identities      : {tot-collide}/{tot} pairs")
print()
print(f"  all 6 objects are at the SAME depth, so the character channel is")
print(f"  mathematically forced to be near-constant across them. Measured above.")
print(f"\n  glyph histogram across the scene: {dict(Counter(D[x][j] for x,j in cells).most_common())}")
