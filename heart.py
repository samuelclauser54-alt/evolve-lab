"""A beating 3D heart made of text. One equation decides which points are inside.
Run it in a terminal:  python heart.py"""
import numpy as np

rng = np.random.default_rng(14)
COLS, ROWS = 78, 38
RAMP = ".:-=+*#%@"                                 # far -> near


def heart(n=200000):
    """Throw random points into a box and keep the ones inside the heart surface
    (x^2 + 9/4 y^2 + z^2 - 1)^3 - x^2 z^3 - 9/80 y^2 z^3 = 0."""
    p = rng.uniform(-1.4, 1.4, (n, 3))
    x, y, z = p.T
    q = x * x + 2.25 * y * y + z * z - 1
    f = q ** 3 - x * x * z ** 3 - 0.1125 * y * y * z ** 3
    return p[f < 0]


def beat(t, bpm=72):
    """Two quick bumps per beat: lub-dub."""
    u = (t * bpm / 60) % 1
    lub = 0.10 * np.exp(-((u - 0.08) / 0.05) ** 2)
    dub = 0.06 * np.exp(-((u - 0.30) / 0.06) ** 2)
    return 1 + lub + dub


def frame(p, angle, t):
    """Scale by the beat, spin, project onto the grid, nearest point wins."""
    x, y, z = (p * beat(t)).T
    xr = x * np.cos(angle) + y * np.sin(angle)
    yr = y * np.cos(angle) - x * np.sin(angle)
    c = (COLS / 2 + xr * 29).astype(int)
    r = (ROWS / 2 - z * 15).astype(int)
    near = np.clip(0.5 + yr / 1.5, 0, 0.999)        # 0 = back of the heart, 1 = front
    ch = np.array(list(RAMP))[(near ** 1.6 * 9).astype(int)]
    red = np.c_[90 + 165 * near, 20 + 70 * near ** 3, 40 + 90 * near ** 2]
    grid = np.full((ROWS, COLS), " ")
    rgb = np.zeros((ROWS, COLS, 3))
    o = np.argsort(yr)                              # far first: near points overwrite
    o = o[(c[o] >= 0) & (c[o] < COLS) & (r[o] >= 0) & (r[o] < ROWS)]
    grid[r[o], c[o]] = ch[o]
    rgb[r[o], c[o]] = red[o]
    return grid, rgb


def ecg(grid, rgb, t, bpm=72):
    """A heart-monitor trace along the bottom row, in step with the beat."""
    for c in range(COLS):
        u = ((t - (COLS - c) / 30) * bpm / 60) % 1          # the trace scrolls left
        spike = "/" if u < 0.06 else "\\" if u < 0.12 else "^" if 0.28 < u < 0.33 else "_"
        grid[ROWS - 1, c] = spike
        rgb[ROWS - 1, c] = np.array([90, 255, 150]) * (0.35 + 0.65 * c / COLS)


if __name__ == "__main__":
    import time
    p = heart()
    t = 0.0
    while True:
        grid, rgb = frame(p, 0.7 * np.sin(0.9 * t), t)      # rock from side to side
        ecg(grid, rgb, t)
        ink = lambda q: f"\x1b[38;2;{int(q[0])};{int(q[1])};{int(q[2])}m"
        rows = ["".join(ink(q) + s for s, q in zip(g, c)) for g, c in zip(grid, rgb)]
        print("\x1b[H\x1b[2J" + "\n".join(rows) + "\x1b[0m")
        time.sleep(1 / 30)
        t += 1 / 30
