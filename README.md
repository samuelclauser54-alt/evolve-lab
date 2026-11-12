# Evolve Lab

Watch tiny neural networks learn to fly through gates and drive a track, live in your browser: **https://samuelclauser54-alt.github.io/evolve-lab/**

Each network has fewer than 60 numbers in it. Nobody shows it how to fly or drive. Every generation the networks that got furthest are kept, the rest are replaced by copies with small random changes, and that is the whole method (neuroevolution). You can change the population, the mutation size and the difficulty and see what happens to learning.

- One file, no dependencies, no tracking: `index.html`.
- Companion to the Instagram account [@atc5.builds](https://www.instagram.com/atc5.builds/), which posts a new simulation every day.

## How it works

| Task | Inputs | Hidden | Output |
|---|---|---|---|
| Gates | height of next gap relative to the flyer, vertical speed, distance to gate, the gap after that | 6 tanh | flap or not |
| Drive | 5 distances to the track edge (rays at -60°, -30°, 0°, 30°, 60°) | 6 tanh | steering rate |

Each generation uses a new random course, so the networks cannot memorise one. The top 10% survive unchanged; the rest are mutated copies of survivors.
