"""A spinning ASCII Christmas tree. Every character is a point in 3D.
Run it in a terminal:  python tree.py"""
import numpy as np

rng = np.random.default_rng(2026)
COLS, ROWS = 78, 38
RAMP = ".*+x%#"                                   # light -> dense


def needles(n=6000):
    """A cone of branches in 9 whorls. Tips are light, the inside is dense."""
    h = rng.uniform(0, 1, n) ** 0.75              # 0 = bottom, 1 = top
    whorl = (h * 9) % 1                           # position inside a whorl
    depth = 0.25 + 0.75 * rng.uniform(0, 1, n) ** 0.5
    r = 0.50 * (1 - h) * (1.0 - 0.3 * whorl) * depth
    a = rng.uniform(0, 2 * np.pi, n)
    dense = ((1 - depth) * 7).astype(int).clip(0, 5)
    green = np.c_[25 + 22 * dense, 190 - 22 * dense, 70 - 6 * dense]
    char = np.array(list(RAMP))[dense + (dense < 5)]
    return r * np.cos(a), 0.10 + 0.80 * h, r * np.sin(a), char, green


def trunk(n=200):
    y = rng.uniform(0.02, 0.12, n)
    a = rng.uniform(0, 2 * np.pi, n)
    brown = np.tile([130, 82, 45], (n, 1))
    return 0.03 * np.cos(a), y, 0.03 * np.sin(a), np.full(n, "#"), brown


def tinsel(n=500):
    """A helix that winds four times round the cone."""
    s = np.linspace(0, 1, n)
    r, a = 0.51 * (1 - s) + 0.005, 8 * np.pi * s
    gold = np.tile([255, 205, 70], (n, 1))
    return r * np.cos(a), 0.10 + 0.80 * s, r * np.sin(a), np.full(n, "~"), gold


def lights(n=110):
    """Fairy lights on the branch tips. Each one blinks on its own clock."""
    h = rng.uniform(0.02, 0.95, n) ** 0.8
    a = rng.uniform(0, 2 * np.pi, n)
    r = 0.50 * (1 - h)
    palette = np.array([[255, 60, 60], [255, 210, 60], [90, 170, 255], [255, 255, 255]])
    colour = palette[rng.integers(0, 4, n)]
    return r * np.cos(a), 0.10 + 0.80 * h, r * np.sin(a), np.full(n, "o"), colour


def presents(k=6):
    """Boxes on a golden-angle spiral round the trunk, each with a ribbon."""
    out = []
    for i in range(k):
        a, d = i * 2.39996, 0.26 + 0.30 * (i / k) ** 0.5
        s = rng.uniform(0.028, 0.045)                       # half the box size
        p = rng.uniform(-s, s, (160, 3))
        face = rng.integers(0, 3, 160)                      # push each point onto a face
        p[np.arange(160), face] = s * rng.choice([-1, 1], 160)
        ribbon = (abs(p[:, 0]) < s / 4) | (abs(p[:, 2]) < s / 4)
        box = np.array([[225, 55, 65], [70, 130, 240], [200, 90, 220]])[i % 3]
        col = np.where(ribbon[:, None], [255, 215, 90], box)
        x, z = p[:, 0] + d * np.cos(a), p[:, 2] + d * np.sin(a)
        out.append((x, p[:, 1] + s, z, np.where(ribbon, "+", "#"), col))
    return [np.concatenate(v) for v in zip(*out)]


def frame(parts, angle, t):
    """Rotate every point, project it onto the grid, keep the nearest per cell."""
    x, y, z, ch, col = (np.concatenate(v) for v in zip(*parts))
    xr = x * np.cos(angle) + z * np.sin(angle)
    zr = z * np.cos(angle) - x * np.sin(angle)
    c = (COLS / 2 + xr * 62).astype(int)                  # characters are tall and thin
    r = (ROWS - 2 - y * 34).astype(int)
    shade = 0.55 + 0.45 * (zr / 0.5 + 1) / 2              # the far side is darker
    blink = np.where(ch == "o", 0.3 + 0.7 * (np.sin(t * 5 + x * 90) > 0), 1)
    grid = np.full((ROWS, COLS), " ")
    rgb = np.zeros((ROWS, COLS, 3))
    o = np.argsort(zr)                                    # far first: near points overwrite
    o = o[(c[o] >= 0) & (c[o] < COLS) & (r[o] >= 0) & (r[o] < ROWS)]
    grid[r[o], c[o]] = ch[o]
    rgb[r[o], c[o]] = col[o] * (shade[o] * blink[o])[:, None]
    return grid, rgb


def star(grid, rgb, t):
    r, c, glow = 2, COLS // 2, 0.7 + 0.3 * np.sin(t * 6)
    rays = [(0, 0, "*"), (-1, 0, "|"), (1, 0, "|"), (0, -2, "-"), (0, 2, "-"),
            (-1, -2, "\\"), (-1, 2, "/"), (1, -2, "/"), (1, 2, "\\")]
    for dr, dc, s in rays:
        grid[r + dr, c + dc], rgb[r + dr, c + dc] = s, np.array([255, 235, 120]) * glow


if __name__ == "__main__":
    import time
    parts = [needles(), trunk(), tinsel(), lights(), presents()]
    t = 0.0
    while True:
        grid, rgb = frame(parts, 0.6 * t, t)
        star(grid, rgb, t)
        ink = lambda q: f"\x1b[38;2;{int(q[0])};{int(q[1])};{int(q[2])}m"
        rows = ["".join(ink(q) + s for s, q in zip(g, p)) for g, p in zip(grid, rgb)]
        print("\x1b[H\x1b[2J" + "\n".join(rows) + "\x1b[0m")
        print("MERRY CHRISTMAS 2026".center(COLS))
        time.sleep(1 / 30)
        t += 1 / 30
