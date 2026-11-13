# ALotto 2.06 — Python Port

Python/pygame port of **ALotto 2.06** ("Lotto PANTHEON"), the Amiga lottery
program by Lukas Konias originally written in Blitz Basic 2.1 (1997).
The port recreates the original 640×256 Workbench look, the English/German
language toggle and the online help.

## Run

```bash
pip install pygame-ce   # or pygame
python3 alotto.py [path/to/default.data]
```

Runs headless too (`SDL_VIDEODRIVER=dummy` is set automatically when no
display is available).

## Features

- 6 number boxes (1–49) with hold checkboxes (a held number survives the
  next calculation, shown in red)
- **Random** — 1–6 unique random numbers
- **Calculate 1 / 2 / 3** — statistics-based number selection
- **Graphic** — frequency bar chart of all numbers from the loaded draws
- **Editor** — add/delete past draws
- **Load/Save/New** — `default.data` is auto-loaded at startup if present
- **Online help** — tooltips on every control, toggleable
- **English | Deutsch** language toggle

## Data format

The original binary checks a `DAT` magic in `default.data`; the port uses
the same convention:

- Binary format: `DAT` followed by one byte per drawn number, 6 bytes per
  draw (e.g. 60 draws = 363 bytes).
- Plain text fallback: one draw per line, six numbers 1–49 separated by
  spaces or commas.

## Algorithm reconstruction

The original is only available as a compiled binary (no source). The m68k
code was disassembled (capstone) to recover the structure:

- **Random** — faithful: loop drawing `Rnd(1..49)` and rejecting duplicates
  until 6 unique numbers remain (matches the routine at `0x2c54`).
- **Calculate 1** — reconstructed as "hot numbers": ranks all 49 numbers by
  draw frequency in the loaded statistics, picks the highest.
- **Calculate 2** — reconstructed as "cold numbers": inverse frequency.
- **Calculate 3** — per the original online help ("uses a random
  combination and Algorithm 1 … best option"): half hot numbers, half
  random fill.

The exact arithmetic of the original compiled routines (fixed-point
weighting around `0x404a`, `divs #49`) was not fully reversed; the
reconstructions follow the documented behaviour. As the author wrote in
the About box: "The Algorithms are fairly simple. So do not rely too much
on them."

## Test

```bash
python3 test_alotto.py
```

Runs logic checks (roundtrip, uniqueness, range, hold behaviour, editor)
headless and writes screenshots to `screenshots/`.
