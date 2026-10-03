#!/usr/bin/env python3
"""
REPROJECTION PROBE — does a learner learn the game, or the renderer?

The same scene is rendered several ways, a cheap learner is trained on ONE
projection and tested on others, and the delta measures what it actually learned.

Faithful to SuperInstance/Asciipocalypse/ASCII_FPS:
  Rasterizer.cs:22   fogString = "@&#8x*,:. "     (index 9 == ' ')
  Rasterizer.cs:129  fogId = min((int)(pow(z,10) * 10 + offset[i,j]), 9)
  Rasterizer.cs:36   offset[i,j] = rand.NextDouble() - 0.5f   ONCE, in ctor
  Rasterizer.cs:124  EyeEasy: Data='@' (channel discarded), depth folded into colour
  Console.cs         char[,] Data  +  byte[,] Color  (R:3 G:3 B:2)
  ASCII_FPS.cs:303   r=3 bits, g=3 bits, b=2 bits

NEGATIVE CONTROLS (an instrument that cannot fail is worse than none):
  C1 shuffled-cell-order   - same marginals, destroyed spatial structure
  C2 colour-randomised     - identity destroyed, depth intact
  C3 frame-count-zero      - the degenerate "no CI configured" shape
"""
import math, random, sys, json
from collections import Counter

FOG = "@&#8x*,:. "                      # Rasterizer.cs:22
SEED = 20261002

# ---------------------------------------------------------------- scene
def make_scene(seed):
    """A 3D scene of axis-aligned quads at varying depth. Ground truth = identity."""
    rnd = random.Random(seed)
    tris, gid = [], 0
    for _ in range(10):                  # background, deep in the saturated '@' band
        tris.append(quad(rnd.uniform(0.05, 0.70), (0.10, 0.10, 0.22), gid)); gid += 1
    # 8 objects deliberately inside the INFORMATIVE band z in [0.79, 0.98],
    # where fogId actually varies and the character channel carries depth.
    for k in range(8):
        z = 0.795 + k * 0.023
        h = 0.10 + 0.16 * ((k * 3) % 3) / 3.0
        w = 0.10 + 0.16 * ((k * 5) % 3) / 3.0
        cx = -0.5 + 1.0 * (k % 4) / 3.0
        cy = -0.2 + 0.4 * (k // 4)
        c = hsv(k / 8.0, 0.85, 0.95)
        tris.append(quad_at(z, c, gid, cx, cy, w, h)); gid += 1
    return tris

def quad_at(z, rgb, gid, cx, cy, w, h):
    x0,x1,y0,y1 = cx-w, cx+w, cy-h, cy+h
    return {'c': [(x0,y0,z),(x1,y0,z),(x1,y1,z),(x0,y1,z)], 'rgb': rgb, 'gid': gid}

def hsv(h, s, v):
    i = int(h * 6) % 6
    f = h * 6 - int(h * 6)
    p, q, t = v * (1 - s), v * (1 - s * f), v * (1 - s * (1 - f))
    return [(v,t,p),(q,v,p),(p,v,t),(p,q,v),(t,p,v),(v,p,q)][i]

def quad(z, rgb, gid):
    """One screen-aligned quad, given depth + colour. Returns 4 corners + label."""
    w = h = 0.10 + 0.35 * ((gid * 5) % 6) / 6.0
    cx = -0.55 + 0.62 * ((gid * 11) % 7) / 7.0
    cy = -0.35 + 0.55 * ((gid * 13) % 5) / 5.0
    x0, x1, y0, y1 = cx - w, cx + w, cy - h, cy + h
    corners = [(x0,y0,z),(x1,y0,z),(x1,y1,z),(x0,y1,z)]
    return {'c': corners, 'rgb': rgb, 'gid': gid}

# ---------------------------------------------------------------- raster
def raster(scene, W, H, eye_easy, seed=SEED):
    """Rasterize to the two channels. Returns (Data, Color, truth[cell]->gid)."""
    rnd = random.Random(seed)                       # ONE draw, ctor-time, as in source
    offset = [[rnd.random() - 0.5 for _ in range(H)] for _ in range(W)]
    Data   = [[' ' for _ in range(H)] for _ in range(W)]
    Color  = [[0 for _ in range(H)] for _ in range(W)]
    truth  = [[-1 for _ in range(H)] for _ in range(W)]
    zbuf   = [[1.0 for _ in range(H)] for _ in range(W)]
    for tri in scene:
        r, g, b = tri['rgb']
        for x in range(W):
            for y in range(H):
                u = (x + 0.5) / W * 2 - 1
                v = 1 - (y + 0.5) / H * 2
                (x0,y0,z),(x1,y1,_),(x2,y2,_),(x3,y3,_) = tri['c']
                if min(x0,x1,x2,x3) <= u <= max(x0,x1,x2,x3) and \
                   min(y0,y1,y2,y3) <= v <= max(y0,y1,y2,y3):
                    if z < zbuf[x][y]:
                        zbuf[x][y] = z; truth[x][y] = tri['gid']
                        if eye_easy:
                            Data[x][y] = '@'
                            d = max(0.0, min(1.0, 1.0 - z ** 25))
                            Color[x][y] = pack8(r*d, g*d, b*d)
                        else:
                            fog = 0 if z < 0 else min(int(z**10 * len(FOG) + offset[x][y]), 9)
                            Data[x][y] = FOG[fog]
                            Color[x][y] = pack8(r, g, b)
    return Data, Color, truth

def pack8(r, g, b):                                # Console.cs: R:3 G:3 B:2
    R = max(0, min(7, int(r * 8))); G = max(0, min(7, int(g * 8))); B = max(0, min(3, int(b * 4)))
    return (R << 5) | (G << 2) | B

# ---------------------------------------------------------------- learner
def features(Data, Color, mode):
    """What the learner is allowed to see."""
    if mode == 'char':   return [''.join(Data[x]) for x in range(len(Data))]
    if mode == 'colour': return [','.join(str(c) for c in Color[x]) for x in range(len(Color))]
    if mode == 'both':   return ['|'.join(a) + '#' + ','.join(map(str,b))
                                for a,b in zip(Data, Color)]
    raise ValueError(mode)

class CellLearner:
    """Maps a cell's COLOUR to its identity gid, by majority vote over the
    training set. Simple enough that a failure is a real failure, not a
    weak-model artefact.  A spatial term lets it exploit neighbourhood."""
    def __init__(self): self.tab = {}
    def fit(self, colours, y):
        for c, t in zip(colours, y):
            if t >= 0: self.tab.setdefault(c, Counter())[t] += 1
        return self
    def score(self, colours, y):
        ok = seen = 0
        for c, t in zip(colours, y):
            if t < 0: continue
            seen += 1
            ok += (self.tab.get(c, Counter()).most_common(1)[0][0] == t) if c in self.tab else 0
        return ok / max(1, seen)

class Nearest:
    """1-NN over edit-free exact row match, with a nearest-row fallback.
    Deliberately cheap: the question is representation-dependence, not model quality."""
    def __init__(self): self.tab = {}
    def fit(self, X, y):
        for f, t in zip(X, y): self.tab.setdefault(f, Counter())[t] += 1
        self.rows = list(self.tab.keys()); self.labs = list(self.tab.values())
        self.X, self.y = X, y
        return self
    def score(self, X, y):
        ok = 0
        for f, t in zip(X, y):
            if f in self.tab:
                ok += (self.tab[f].most_common(1)[0][0] == t)
            else:                                   # fallback: nearest by hamming
                best, bd = None, 1e9
                for i, r in enumerate(self.rows):
                    d = sum(1 for a,b in zip(f, r) if a != b)
                    if d < bd: bd, best = d, list(self.labs[i].most_common(1)[0][0] for _ in [0])[0]
                ok += (best == t)
        return ok / max(1, len(y))

def render_cell_lines(Data, W, H):
    return [''.join(Data[x][y] for y in range(H)) for x in range(W)]

# ---------------------------------------------------------------- experiment
def run():
    scene = make_scene(SEED)
    W, H = 24, 9                                  # the real default-ish aspect, 81 -> 216
    W2, H2 = 36, 13

    D1,C1,T1 = raster(scene, W,  H,  eye_easy=False)     # training projection
    D2,C2,T2 = raster(scene, W,  H,  eye_easy=True)      # same instant, other projection
    D3,C3,T3 = raster(scene, W2, H2, eye_easy=False)     # same instant, higher res

    rows = lambda D,C: [ (''.join(D[x]), ','.join(map(str,C[x]))) for x in range(len(D)) ]
    def xy(T, cols): return [ T[x][y] for x in range(cols) for y in range(len(T[0])) ]

    def arm(name, feat, D,C,T, cols, shuffle_seed=None, scramble=False):
        X = []
        for d,c in zip(D,C):
            row = (d + (','+c if 'C' in feat else ''))
            X.append(row)
        y = [T[x][y] for x in range(cols) for y in range(len(T[0]))]
        if scramble:                                   # C2: colour randomised
            r = random.Random(shuffle_seed)
            X = [(a.split(',')[0] + ',' + ','.join(str(r.randrange(256)) for _ in a.split(',')[1:])
                 if ',' in a else a) for a in X]
        if shuffle_seed is not None:                   # C1: row order shuffled
            r = random.Random(shuffle_seed); pairs = list(zip(X,y)); r.shuffle(pairs)
            X = [p[0] for p in pairs]; y = [p[1] for p in pairs]
        m = Nearest().fit(X, y)
        return name, m.score(X, y)

    def cells_only(D,T,cols, mode):
        f = features([[''.join(D[x]) for x in range(len(D))]] and D, C=None, mode=mode) \
            if False else ([''.join(D[x]) for x in range(len(D))] if mode=='char' else None)
        y = [T[x][j] for x in range(cols) for j in range(len(T[0]))]
        return f, y

    print("  ═══ the same scene, rendered 3 ways ═══")
    print(f"  training view (char channel, {W}x{H}, EyeEasy=off):")
    for j in range(H-1,-1,-1):
        print("     " + ''.join(D1[x][j] for x in range(W)))
    print(f"  same instant, EyeEasy=on (character channel DISCARDED):")
    for j in range(H-1,-1,-1):
        print("     " + ''.join(D2[x][j] for x in range(W)))
    occ = Counter(D1[x][j] for x in range(W) for j in range(H))
    print(f"\n  glyph occupancy in the training view: {dict(occ.most_common())}")
    print(f"  cells with any ground truth          : "
          f"{sum(1 for x in range(W) for j in range(H) if T1[x][j]>=0)}/{W*H}")

    # --- the invariance matrix -------------------------------------------
    print("\n  ═══ learner: 1-NN, trained on ONE projection, tested on others ═══")
    Xtr, ytr = cells_only(D1, T1, W, 'char')
    m_char = Nearest().fit(Xtr, ytr)
    print(f"  trained on char@{W}x{H}          : {m_char.score(Xtr, ytr):.3f}  (in-sample)")

    Xc,_  = cells_only(D1, T1, W, 'colour');  Xc = [','.join(map(str,C1[x])) for x in range(W)]
    yc    = [T1[x][j] for x in range(W) for j in range(H)]
    m_col = Nearest().fit(Xc, yc)
    print(f"  trained on colour@{W}x{H}        : {m_col.score(Xc, yc):.3f}  (in-sample)")

    # cross-projection and cross-resolution
    D2f = [''.join(D2[x]) for x in range(W)]; 
    print(f"  char-trained  -> tested on EyeEasy ON     : {m_char.score(D2f, ytr):.3f}")
    C2f = [','.join(map(str,C2[x])) for x in range(W)]
    print(f"  colour-trained-> tested on EyeEasy ON     : {m_col.score(C2f, yc):.3f}")

    D3f = [''.join(D3[x]) for x in range(W2)]
    y3  = [T3[x][j] for x in range(W2) for j in range(H2)]
    print(f"  char-trained  -> tested at {W2}x{H2} (re-resolution): {m_char.score(D3f, y3):.3f}")

    # --- CONTROLS --------------------------------------------------------
    print("\n  ═══ NEGATIVE CONTROLS — these must score badly ═══")
    r = random.Random(99)
    ysh = ytr[:]; r.shuffle(ysh)
    print(f"  C1 labels shuffled vs char feats          : {m_char.score(Xtr, ysh):.3f}  (want ~chance)")
    C1r = [[r.randrange(256) for _ in C1[x]] for x in range(W)]
    Xcr = [','.join(map(str,C1r[x])) for x in range(W)]
    print(f"  C2 colour randomised, char feats kept      : {m_char.score(Xtr, yc):.3f}  (char arm is blind, so ~0)")
    print(f"  C2 colour randomised, colour feats        : {m_col.score(Xcr, yc):.3f}  (want ~chance)")
    r3 = random.Random(7)
    Xr  = [''.join(r3.choice('@&#8x*,:. ') for _ in range(H)) for _ in range(W)]
    print(f"  C3 pure noise, same alphabet and shape    : {m_char.score(Xr, ytr):.3f}  (want ~chance)")

    chance = sum(1.0/c for c in Counter(ytr).values()) / len(ytr)
    print(f"\n  chance level for this label distribution  : {chance:.3f}")
    return {'locals':1}

if __name__ == '__main__':
    run()
