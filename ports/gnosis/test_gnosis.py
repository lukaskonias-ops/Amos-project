#!/usr/bin/env python3
"""Headless smoke test for the Gnosis port; saves screenshots to ./screenshots."""
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pygame
from gnosis import (
    GnosisApp,
    QUE_ANSWER_OFF,
    QUE_RECORD_STRIDE,
    decode_amiga_greek,
    load_all_questions,
    load_que,
    new_stats,
    record_answer,
    save_stats,
    success_percent,
    wrap_text,
)

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "screenshots")
os.makedirs(OUT, exist_ok=True)

EXPECTED_COUNTS = {
    "Γεωγραφια": 25,
    "Ιστορια": 21,
    "Λογοτεχνια": 22,
    "Ζωα-Φυτα": 25,
    "Φυσικες Επιστημες": 33,
    "Αθλητικα": 38,
}


def check(cond, msg):
    if not cond:
        raise AssertionError(msg)
    print("OK:", msg)


def main():
    random.seed(42)
    base = os.path.dirname(os.path.abspath(__file__))
    qdir = os.path.join(base, "questions")

    check(decode_amiga_greek(bytes([0xC2, 0xDD, 0xFA, 0xDB, 0xEF, 0xD8, 0xF7, 0xE3, 0xD8]))
          == "Γεωγραφια", "greek charset: Γεωγραφια")
    check(decode_amiga_greek(bytes([0xF8, 0xFA, 0xEF, 0xD8]))
          == "χωρα", "greek charset: χωρα (0xF8=χ, 0xFA=ω)")

    packs = load_all_questions(qdir)
    check(len(packs) == 6, f"6 question packs loaded (got {len(packs)})")
    for category, questions in packs:
        check(category in EXPECTED_COUNTS, f"category '{category}' decoded")
        check(len(questions) == EXPECTED_COUNTS[category],
              f"{category}: {EXPECTED_COUNTS[category]} questions")
        for q in questions:
            check(q.correct in (0, 1, 2), f"{category}: answer index valid")
            check(len(q.answers) == 3 and all(q.answers), f"{category}: 3 non-empty answers")
            check(len(q.text) > 5, f"{category}: question text non-empty")

    _, geography = load_que(os.path.join(qdir, "geography.que"))
    q1 = geography[0]
    check("νομοι" in q1.text and "Ελλαδας" in q1.text,
          f"geography q1 reads as greek: {q1.text!r}")
    check(q1.answers[q1.correct] == "Επτα.", "geography q1 correct answer is Επτα.")
    q2 = geography[1]
    check(q2.answers[q2.correct] == "Λαμια.", "geography q2 correct answer is Λαμια (Λαμία)")

    raw = open(os.path.join(qdir, "geography.que"), "rb").read()
    check(raw[0x107 + QUE_ANSWER_OFF] in (0xC0, 0xC1, 0xC2),
          "answer key byte at record offset 0x106")
    check(len(raw) == 0x107 + EXPECTED_COUNTS["Γεωγραφια"] * QUE_RECORD_STRIDE,
          "file size = header + n * 0x107")

    check(wrap_text("α β γ δ ε", 3) == ["α β", "γ δ", "ε"], "wrap_text")

    stats = new_stats()
    record_answer(stats, "Γεωγραφια", True)
    record_answer(stats, "Γεωγραφια", False)
    check(success_percent(stats, "Γεωγραφια") == 50, "success_percent 50%")
    check(success_percent(stats, "Ιστορια") is None, "success_percent None for new category")
    stat_path = "/tmp/gnosis_test.stat"
    save_stats(stats, stat_path)
    from gnosis import load_stats
    check(load_stats(stat_path)["answered"]["Γεωγραφια"] == 2, "stats roundtrip")

    pygame.init()
    app = GnosisApp(questions_dir=qdir, stats_path="/tmp/gnosis_app.stat")
    app.stats = new_stats()
    app.stats["player"] = "Lukas"

    app.name_buffer = "Lukas"
    app.act_start()
    check(app.state == "menu", "name entry -> menu")

    def snap(name):
        app.draw()
        pygame.image.save(app.screen, os.path.join(OUT, name))

    snap("01_name.png")
    app.state = "name"
    app.draw()
    snap("01_name.png")
    app.act_start()
    snap("02_menu.png")

    category, questions = packs[0]
    app.start_round(category, questions)
    check(app.state == "quiz" and len(app.questions) == min(10, len(questions)),
          "round starts with up to 10 questions")
    app.draw()
    snap("03_quiz.png")

    question = app.questions[0]
    app.act_answer(question.correct)
    check(app.score == 1 and app.answered_state[1], "correct answer scores")
    app.draw()
    snap("04_feedback_correct.png")
    app.act_next()
    question = app.questions[1]
    wrong = (question.correct + 1) % 3
    app.act_answer(wrong)
    check(app.score == 1 and not app.answered_state[1], "wrong answer does not score")
    app.draw()
    snap("05_feedback_wrong.png")

    app.q_index = len(app.questions) - 1
    app.act_next()
    check(app.state == "round_end", "round ends after last question")
    app.draw()
    snap("06_round_end.png")

    app.act_stats()
    app.draw()
    snap("07_stats.png")
    app.act_back()
    app.act_about()
    app.draw()
    snap("08_about.png")
    pygame.quit()
    print("ALL GNOSIS CHECKS PASSED")


if __name__ == "__main__":
    main()
