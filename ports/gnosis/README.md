# Gnosis 0.99 — Python Port

Python/pygame port of **Gnosis 0.99** ("Το Παιχνίδι των Γνώσεων"), the Amiga
quiz board game by Lukas Konias, originally written in AMOS BASIC 1.35
(January 1996). The port runs all **164 original questions** from the six
`.que` files with their original answer keys, renders the Greek text and
recreates the 640×256 Workbench look.

## Run

```bash
pip install pygame-ce   # or pygame
python3 gnosis.py
```

Runs headless too (`SDL_VIDEODRIVER=dummy` is set automatically when no
display is available).

## Features

- **Name entry** — "Δωσε το ονομα σου", as in the original
- **6 categories** — Γεωγραφια (25), Ιστορια (21), Λογοτεχνια (22),
  Ζωα-Φυτα (25), Φυσικες Επιστημες (33), Αθλητικα (38) — all decoded from
  the original `.que` files in `questions/`
- **Quiz rounds** — 10 random questions per round, 3 answers each (Α/Β/Γ),
  original answer key honoured; keys 1/2/3 or mouse
- **Feedback** — green for correct, red for wrong (with the correct answer
  highlighted)
- **Player statistics** — "ΣΤΑΤΙΣΤΙΚΑ ΤΟΥ ΠΑΙΚΤΗ": games played, questions
  answered and success percentage per field, persisted to `gnosis.stat`
- **About screen** — the original About text recovered from the `Qgame`
  binary (Public Domain notice, AMOS BASIC 1.35, author address)

## Reverse-engineered formats

### `.que` question files

- Header: `"Questionsv01"` + padding; category name (Amiga-Greek encoding)
  at offset `0x92`
- Fixed-size records of **0x107 (263) bytes** starting at offset `0x107`:
  - `+0x00` question text (88 bytes, space-padded)
  - `+0x58` answer 1 (58 bytes)
  - `+0x92` answer 2 (58 bytes)
  - `+0xCC` answer 3 (58 bytes)
  - `+0x106` **answer key**: `0xC0`/`0xC1`/`0xC2` = Α/Β/Γ = correct answer
    1/2/3

### Amiga-Greek text encoding

The `.que` files and the `Qgame` binary use a custom single-byte Greek
encoding (uppercase `0xC0–0xD7`, lowercase `0xD8–0xFA` with accented vowels
occupying unused slots). Recovered by frequency analysis and cross-referencing
category names; verified against all 164 questions with zero unmapped bytes.
The author typed without accents and mixed ο/ω in places (he apologises for
the spelling mistakes in `GNOSIS.REA`) — the port keeps the original text
unchanged. Multi-space runs (used for positioning in the original fixed-width
font) are collapsed to single spaces.

### Differences from the original

- The original is a board game with dice ("Μ.ο. ζαριων ανα παιχνιδι" appears
  in its statistics). The board/dice flow of the AMOS binary was not fully
  reverse-engineered; this port implements the quiz core with per-field
  statistics instead.
- Statistics use a JSON file (`gnosis.stat`); the original `.stat` format
  (`QSTATS01` magic) was not decoded.

## Tests

```bash
python3 test_gnosis.py
```

521 headless checks: charset round-trips, all six files parse with the
expected question counts, answer-key bytes valid, spot-checks of decoded
questions, stats round-trip, and a full UI walkthrough (name → menu → quiz →
feedback → round end → stats → about) with screenshots written to
`screenshots/`.
