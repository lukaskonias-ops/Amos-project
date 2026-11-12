#!/usr/bin/env python3
"""Headless smoke test for the ALotto port; saves screenshots to ./screenshots."""
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import alotto
from alotto import (
    ALottoApp,
    algorithm_calc1,
    algorithm_calc2,
    algorithm_calc3,
    algorithm_random,
    load_data,
    save_data,
)

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "screenshots")
os.makedirs(OUT, exist_ok=True)


def check(cond, msg):
    if not cond:
        raise AssertionError(msg)
    print("OK:", msg)


def main():
    random.seed(42)
    sample = os.path.join(OUT, "sample.data")
    draws = [tuple(sorted(random.sample(range(1, 50), 6))) for _ in range(60)]
    save_data(sample, draws)
    loaded = load_data(sample)
    check(loaded == draws, "save/load roundtrip (DAT format)")
    with open(sample, "rb") as fh:
        check(fh.read(3) == b"DAT", "DAT magic present")

    for name, fn in [("random", algorithm_random), ("calc1", algorithm_calc1),
                     ("calc2", algorithm_calc2), ("calc3", algorithm_calc3)]:
        res = fn(draws, [])
        check(len(res) == 6 and len(set(res)) == 6, f"{name}: 6 unique numbers")
        check(all(1 <= n <= 49 for n in res), f"{name}: range 1-49")
        held = [7]
        res = fn(draws, held)
        check(7 in res and len(set(res)) == 6, f"{name}: held number kept")

    app = ALottoApp(sample)
    check(len(app.draws) == 60, "startup autoload of default.data")

    app.act_random()
    app.render((100, 100))
    pygame = alotto.pygame
    pygame.image.save(app.screen, os.path.join(OUT, "alotto_main.png"))

    app.act_calc3()
    check(all(n != 0 for n in app.numbers), "calc3 produced numbers")

    app.act_lang()
    check(app.lang == "de", "language toggle")
    app.act_random()
    app.render((30, 130))
    pygame.image.save(app.screen, os.path.join(OUT, "alotto_german.png"))

    app.act_graphic()
    app.render((0, 0))
    pygame.image.save(app.screen, os.path.join(OUT, "alotto_graphic.png"))

    app.view = "editor"
    app.editor_input = "4 8 15 16 23 42"
    app.act_editor_add()
    check(tuple([4, 8, 15, 16, 23, 42]) in app.draws, "editor add draw")
    app.render((0, 0))
    pygame.image.save(app.screen, os.path.join(OUT, "alotto_editor.png"))

    app.view = "about"
    app.render((0, 0))
    pygame.image.save(app.screen, os.path.join(OUT, "alotto_about.png"))

    print("All checks passed. Screenshots in", OUT)


if __name__ == "__main__":
    main()
