"""A fire made of text. Every cell copies the heat of a cell just below it,
a little cooler and a little to one side. That is the whole simulation.
Run it in a terminal:  python fire.py"""
import numpy as np

rng = np.random.default_rng(7)
COLS, ROWS = 78, 38
RAMP = " .:;+*oxO#@"                                # cold -> hot
EMBER = np.array([[0, 0, 0], [170, 25, 0], [250, 90, 0], [255, 175, 30], [255, 238, 120], [255, 255, 240]])


def step(heat, wind=0.0, t=0.0):
    """One tick: heat rises one row, drifts sideways and cools at random."""
    drift = rng.choice([-1, 0, 0, 0, 1], (ROWS - 1, COLS)) + int(round(wind))
    source = (np.arange(COLS) + drift) % COLS       # which column each cell copies from
    cool = rng.uniform(0.0, 0.062, (ROWS - 1, COLS))
    below = heat[1:]                                # the row underneath each cell
    heat[:-1] = np.clip(np.take_along_axis(below, source, axis=1) - cool, 0, 1)
    c = np.arange(COLS)
    spots = np.sin(c / 4.5 + 0.8 * np.sin(0.7 * t)) ** 2           # hot spots that sway
    flicker = 0.65 + 0.35 * np.sin(2.3 * t + c // 9 * 2.1)        # each group burns up and down
    heat[-1] = np.clip(1.3 * spots * flicker + rng.uniform(-0.1, 0.1, COLS), 0, 1)   # the fuel
    return heat


def paint(heat):
    """Heat -> a character (denser = hotter) and a colour (black, red, orange, yellow, white)."""
    grid = np.array(list(RAMP))[(heat * 10.999).astype(int)]
    f = heat * 4.999
    i = f.astype(int)
    w = (f - i)[..., None]
    return grid, EMBER[i] * (1 - w) + EMBER[i + 1] * w


if __name__ == "__main__":
    import time
    heat = np.zeros((ROWS, COLS))
    t = 0.0
    while True:
        heat = step(heat, wind=1.2 * np.sin(t / 2), t=t)
        grid, rgb = paint(heat)
        ink = lambda q: f"\x1b[38;2;{int(q[0])};{int(q[1])};{int(q[2])}m"
        rows = ["".join(ink(q) + s for s, q in zip(g, c)) for g, c in zip(grid, rgb)]
        print("\x1b[H\x1b[2J" + "\n".join(rows) + "\x1b[0m")
        time.sleep(1 / 30)
        t += 1 / 30
