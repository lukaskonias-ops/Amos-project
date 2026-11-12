#!/usr/bin/env python3
"""Gnosis 0.99 - Python port of the Amiga AMOS quiz game by Lukas Konias."""
import json
import os
import random
import re
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

SCREEN_W, SCREEN_H = 640, 256
SCALE = 2
ROUND_LENGTH = 10
STATS_FILE = "gnosis.stat"

QUE_HEADER_MAGIC = b"Questionsv01"
QUE_CATEGORY_OFF = 0x92
QUE_CATEGORY_LEN = 0x3B
QUE_FIRST_RECORD = 0x107
QUE_RECORD_STRIDE = 0x107
QUE_Q_OFF, QUE_Q_LEN = 0x00, 0x58
QUE_A1_OFF, QUE_A1_LEN = 0x58, 0x3A
QUE_A2_OFF, QUE_A2_LEN = 0x92, 0x3A
QUE_A3_OFF, QUE_A3_LEN = 0xCC, 0x3A
QUE_ANSWER_OFF = 0x106

UPPER = "ΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩ"
LOWER = "αάβγδεέζηήθιίϊϋκλμνξοόπρσςτυύϋΰφχψω"
CHARMAP = {}
for _i, _ch in enumerate(UPPER):
    CHARMAP[0xC0 + _i] = _ch
for _i, _ch in enumerate(LOWER):
    CHARMAP[0xD8 + _i] = _ch

ANSWER_LETTERS = ("Α", "Β", "Γ")

UI = {
    "title": "Το Παιχνιδι Των Γνωσεων",
    "subtitle": "Gnosis 0.99 - AMOS 1.35 (1996) - Python port",
    "name_prompt": "Δωσε το ονομα σου",
    "name_hint": "Γραψε το ονομα και πατα Return",
    "start": "Αρχη",
    "stats": "Στατιστικα",
    "about": "About",
    "exit": "Εξοδος",
    "question": "Ερωτηση",
    "score": "Σκορ",
    "correct": "Σωστο!",
    "wrong": "Λαθος!",
    "next": "Επομενο",
    "round_end": "Τελος γυρου",
    "win": "Κερδισες στο Παιχνιδι Των Γνωσεων",
    "again": "Ξανα",
    "menu": "Μεnu",
    "stats_title": "ΣΤΑΤΙΣΤΙΚΑ ΤΟΥ ΠΑΙΚΤΗ",
    "player": "Παιχτης",
    "games": "Επαιξες παιχνιδια",
    "answered": "Ερωτησεις",
    "success": "Ποσοστο επιτυχιας",
    "back": "Πισω",
    "no_questions": "Δεν βρεθηκαν ερωτησεις",
}

ABOUT_LINES = [
    "Κερδισες στο Παιχνιδι Των Γνωσεων",
    "",
    "Δυστυχως λογω ελλειψης χρονου δεν καταφερα να προσθεσω",
    "γραφικα,ηχο και περισσοτερες ερωτησεις σε αυτην την εκ-",
    "δοση του παιχνιδιου.Αν θεις την τελευταια εκδοση μαζι",
    "με εναν Editor Ερωτησεων στειλεια μια αδεια δισκετα στην",
    "παρακατω διευθυνση μαζι με ενα ποσο που να καλυπτει τα",
    "ταχυδρομικα εξοδα.",
    "Οποιοδηποτε σχολιο πανω στο προγραμα ευπροσδεκτο.",
    "Ακομη ενδιαφερομαι να ερθω σε επαφη με ατομα που",
    "μπορουν να με προμηθευσουν με εικονες,μουσικες και",
    "samples η που να προγραμματιζουν σε AMOS.",
    "Το προγραμμα αυτο ειναι Public Domain και μπορει να",
    "αντιγραφει ελευθερα.Οποιεσδηποτε μετατροπες χωρις την",
    "αδεια μου απαγορευονται.",
    "Για την κατασκευη του παιχνιδιου χρησιμοποιηθηκε η",
    "AMOS BASIC 1.35",
    "                                 Ο προγραμματιστής",
    "                                  Λουκας Κονιας",
    "Διευθυνση:Λουκας Κονιας",
    "          Ρετζικι Τ.Τ.57010",
    "          Θεσ/νικη",
    "          Τηλ.(031)673-719",
]


class Question:
    def __init__(self, text, answers, correct):
        self.text = text
        self.answers = answers
        self.correct = correct


def decode_amiga_greek(raw):
    out = []
    for b in raw:
        if b in CHARMAP:
            out.append(CHARMAP[b])
        elif 32 <= b < 127:
            out.append(chr(b))
    return "".join(out)


def _clean(text):
    return re.sub(r" {2,}", " ", text).strip()


def load_que(path):
    data = open(path, "rb").read()
    if not data.startswith(QUE_HEADER_MAGIC[:10]):
        raise ValueError(f"{path}: not a Gnosis question file")
    category = _clean(decode_amiga_greek(
        data[QUE_CATEGORY_OFF:QUE_CATEGORY_OFF + QUE_CATEGORY_LEN]))
    questions = []
    body = data[QUE_FIRST_RECORD:]
    count = len(body) // QUE_RECORD_STRIDE
    for i in range(count):
        rec = body[i * QUE_RECORD_STRIDE:(i + 1) * QUE_RECORD_STRIDE]
        text = _clean(decode_amiga_greek(rec[QUE_Q_OFF:QUE_Q_OFF + QUE_Q_LEN]))
        a1 = _clean(decode_amiga_greek(rec[QUE_A1_OFF:QUE_A1_OFF + QUE_A1_LEN]))
        a2 = _clean(decode_amiga_greek(rec[QUE_A2_OFF:QUE_A2_OFF + QUE_A2_LEN]))
        a3 = _clean(decode_amiga_greek(rec[QUE_A3_OFF:QUE_A3_OFF + QUE_A3_LEN]))
        ans_byte = rec[QUE_ANSWER_OFF]
        if ans_byte < 0xC0 or ans_byte > 0xC2:
            raise ValueError(f"{path}: question {i + 1}: bad answer byte 0x{ans_byte:02x}")
        questions.append(Question(text, [a1, a2, a3], ans_byte - 0xC0))
    return category, questions


def load_all_questions(directory):
    packs = []
    for name in sorted(os.listdir(directory)):
        if name.lower().endswith(".que"):
            packs.append(load_que(os.path.join(directory, name)))
    return packs


def new_stats():
    return {"player": "", "games": 0, "answered": {}, "correct": {}}


def load_stats(path=STATS_FILE):
    if os.path.exists(path):
        try:
            data = json.load(open(path, encoding="utf-8"))
            base = new_stats()
            base.update(data)
            return base
        except (ValueError, OSError):
            pass
    return new_stats()


def save_stats(stats, path=STATS_FILE):
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(stats, fh, ensure_ascii=False, indent=1)


def record_answer(stats, category, was_correct):
    answered = stats["answered"].get(category, 0) + 1
    stats["answered"][category] = answered
    if was_correct:
        stats["correct"][category] = stats["correct"].get(category, 0) + 1


def success_percent(stats, category):
    answered = stats["answered"].get(category, 0)
    if not answered:
        return None
    return round(100.0 * stats["correct"].get(category, 0) / answered)


def wrap_text(text, max_chars):
    words = text.split(" ")
    lines, line = [], ""
    for word in words:
        if line and len(line) + 1 + len(word) > max_chars:
            lines.append(line)
            line = word
        else:
            line = f"{line} {word}".strip()
    if line:
        lines.append(line)
    return lines


class Button:
    def __init__(self, rect, action, label=""):
        self.rect = pygame.Rect(rect)
        self.action = action
        self.label = label


class GnosisApp:
    def __init__(self, questions_dir=None, stats_path=STATS_FILE, scale=SCALE):
        self.scale = scale
        base = os.path.dirname(os.path.abspath(__file__))
        if questions_dir is None:
            questions_dir = os.path.join(base, "questions")
        self.packs = load_all_questions(questions_dir)
        self.stats_path = stats_path
        self.stats = load_stats(stats_path)
        self.screen = pygame.display.set_mode((SCREEN_W * scale, SCREEN_H * scale))
        self.font = pygame.font.Font(None, 22 * scale // 2 + 6)
        self.small = pygame.font.Font(None, 17 * scale // 2 + 4)
        self.title_font = pygame.font.Font(None, 30 * scale // 2 + 8)
        self.buttons = []
        self.state = "name"
        self.player = self.stats.get("player", "")
        self.name_buffer = self.player
        self.category = None
        self.full_questions = []
        self.questions = []
        self.q_index = 0
        self.score = 0
        self.answered_state = None
        self.status = ""
        self._build_name()

    def t(self, key):
        return UI[key]

    def _clear_buttons(self):
        self.buttons = []

    def _add(self, rect, action, label=""):
        self.buttons.append(Button(rect, action, label))

    def _build_name(self):
        self._clear_buttons()
        self._add((250, 200, 140, 30), "start", self.t("start"))

    def _build_menu(self):
        self._clear_buttons()
        y = 78
        for category, questions in self.packs:
            self._add((40, y, 280, 24), ("play", category, questions),
                      f"{category} ({len(questions)})")
            y += 26
        self._add((360, 78, 240, 24), "stats", self.t("stats"))
        self._add((360, 110, 240, 24), "about", self.t("about"))
        self._add((360, 150, 240, 24), "exit", self.t("exit"))

    def _build_quiz(self):
        self._clear_buttons()
        question = self.questions[self.q_index]
        y = 120
        for i in range(3):
            self._add((60, y, 520, 28), ("answer", i))
            y += 34
        if self.answered_state is not None:
            self._add((240, 226, 160, 24), "next", self.t("next"))

    def start_round(self, category, questions):
        self.category = category
        self.full_questions = list(questions)
        pool = list(questions)
        random.shuffle(pool)
        self.questions = pool[:ROUND_LENGTH]
        self.q_index = 0
        self.score = 0
        self.answered_state = None
        self.state = "quiz"
        self._build_quiz()

    def act_start(self):
        if self.name_buffer.strip():
            self.player = self.name_buffer.strip()
            self.stats["player"] = self.player
            self.state = "menu"
            self._build_menu()

    def act_stats(self):
        self.state = "stats"
        self._clear_buttons()
        self._add((260, 226, 120, 24), "back", self.t("back"))

    def act_about(self):
        self.state = "about"
        self._clear_buttons()
        self._add((260, 226, 120, 24), "back", self.t("back"))

    def act_exit(self):
        self.save()
        pygame.event.post(pygame.event.Event(pygame.QUIT))

    def act_back(self):
        self.state = "menu"
        self._build_menu()

    def act_answer(self, index):
        if self.answered_state is not None:
            return
        question = self.questions[self.q_index]
        was_correct = index == question.correct
        if was_correct:
            self.score += 1
        self.answered_state = (index, was_correct)
        record_answer(self.stats, self.category, was_correct)
        self.save()
        self._build_quiz()

    def act_next(self):
        self.q_index += 1
        self.answered_state = None
        if self.q_index >= len(self.questions):
            self.stats["games"] = self.stats.get("games", 0) + 1
            self.save()
            self.state = "round_end"
            self._clear_buttons()
            self._add((200, 210, 110, 26), ("play", self.category, self.full_questions), self.t("again"))
            self._add((330, 210, 110, 26), "back", self.t("menu"))
        else:
            self._build_quiz()


    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.save()
            self.running = False
            return
        if event.type == pygame.KEYDOWN:
            if self.state == "name":
                if event.key == pygame.K_RETURN:
                    self.act_start()
                elif event.key == pygame.K_BACKSPACE:
                    self.name_buffer = self.name_buffer[:-1]
                elif event.unicode and 32 <= ord(event.unicode) < 0x400 and len(self.name_buffer) < 20:
                    self.name_buffer += event.unicode
            elif self.state == "quiz" and event.key in (pygame.K_1, pygame.K_KP_1):
                self._click_action(("answer", 0))
            elif self.state == "quiz" and event.key in (pygame.K_2, pygame.K_KP_2):
                self._click_action(("answer", 1))
            elif self.state == "quiz" and event.key in (pygame.K_3, pygame.K_KP_3):
                self._click_action(("answer", 2))
            elif event.key == pygame.K_SPACE and self.state == "quiz" and self.answered_state is not None:
                self.act_next()
            elif event.key == pygame.K_ESCAPE and self.state in ("quiz", "stats", "about"):
                self.act_back()
            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            for button in self.buttons:
                if button.rect.collidepoint(pos):
                    self._click_action(button.action)
                    return

    def _click_action(self, action):
        if action == "start":
            self.act_start()
        elif action == "stats":
            self.act_stats()
        elif action == "about":
            self.act_about()
        elif action == "exit":
            self.act_exit()
        elif action == "back":
            self.act_back()
        elif action == "next":
            self.act_next()
        elif isinstance(action, tuple) and action[0] == "answer":
            self.act_answer(action[1])
        elif isinstance(action, tuple) and action[0] == "play":
            self.start_round(action[1], action[2])

    def save(self):
        save_stats(self.stats, self.stats_path)

    def run(self, max_frames=None):
        self.running = True
        clock = pygame.time.Clock()
        frames = 0
        while self.running:
            for event in pygame.event.get():
                self.handle_event(event)
            self.draw()
            pygame.display.flip()
            frames += 1
            if max_frames is not None and frames >= max_frames:
                break
            clock.tick(60)
        pygame.quit()

    def draw(self):
        s = self.scale
        surface = pygame.Surface((SCREEN_W, SCREEN_H))
        surface.fill((72, 88, 128))
        pygame.draw.rect(surface, (144, 160, 192), (0, 0, 640, 256), 2)
        if self.state == "name":
            self._draw_name(surface)
        elif self.state == "menu":
            self._draw_menu(surface)
        elif self.state == "quiz":
            self._draw_quiz(surface)
        elif self.state == "round_end":
            self._draw_round_end(surface)
        elif self.state == "stats":
            self._draw_stats(surface)
        elif self.state == "about":
            self._draw_about(surface)
        pygame.transform.scale_by(surface, s, self.screen)

    def _center(self, surface, font, text, y, color=(255, 255, 255)):
        rendered = font.render(text, True, color)
        surface.blit(rendered, (surface.get_width() // 2 - rendered.get_width() // 2, y))
        return rendered

    def _draw_name(self, surface):
        self._center(surface, self.title_font, self.t("title"), 60, (255, 224, 128))
        self._center(surface, self.font, self.t("name_prompt"), 110)
        box = pygame.Rect(200, 140, 240, 28)
        pygame.draw.rect(surface, (32, 40, 64), box)
        pygame.draw.rect(surface, (255, 255, 255), box, 1)
        surface.blit(self.font.render(self.name_buffer + "_", True, (255, 255, 255)),
                     (box.x + 8, box.y + 4))
        self._center(surface, self.small, self.t("name_hint"), 178, (208, 208, 224))
        self._draw_buttons(surface)

    def _draw_menu(self, surface):
        self._center(surface, self.title_font, self.t("title"), 24, (255, 224, 128))
        self._center(surface, self.small, f"{self.t('subtitle')}  |  {self.t('player')}: {self.player}",
                     56, (208, 208, 224))
        self._draw_buttons(surface)

    def _draw_quiz(self, surface):
        question = self.questions[self.q_index]
        header = f"{self.category}  -  {self.t('question')} {self.q_index + 1}/{len(self.questions)}  -  {self.t('score')} {self.score}"
        self._center(surface, self.font, header, 14, (255, 224, 128))
        y = 52
        for line in wrap_text(question.text, 68)[:3]:
            self._center(surface, self.font, line, y)
            y += 20
        for i, button in enumerate(b for b in self.buttons if isinstance(b.action, tuple)):
            letter = ANSWER_LETTERS[i]
            color = (255, 255, 255)
            if self.answered_state is not None:
                chosen, was_correct = self.answered_state
                if i == question.correct:
                    color = (128, 255, 128)
                elif i == chosen:
                    color = (255, 128, 128)
            pygame.draw.rect(surface, (32, 40, 64), button.rect)
            pygame.draw.rect(surface, color, button.rect, 1)
            text = self.font.render(f"{letter}) {question.answers[i]}", True, color)
            surface.blit(text, (button.rect.x + 10, button.rect.y + 5))
        if self.answered_state is not None:
            chosen, was_correct = self.answered_state
            msg = self.t("correct") if was_correct else self.t("wrong")
            color = (128, 255, 128) if was_correct else (255, 128, 128)
            self._center(surface, self.font, msg, 96, color)
        self._draw_buttons(surface)

    def _draw_round_end(self, surface):
        total = len(self.questions)
        self._center(surface, self.title_font, self.t("round_end"), 70, (255, 224, 128))
        self._center(surface, self.font, f"{self.t('score')}: {self.score}/{total}", 110)
        if self.score == total:
            self._center(surface, self.font, self.t("win"), 140, (128, 255, 128))
        self._draw_buttons(surface)

    def _draw_stats(self, surface):
        self._center(surface, self.title_font, self.t("stats_title"), 20, (255, 224, 128))
        self._center(surface, self.font,
                     f"{self.t('player')}: {self.stats.get('player', '-')}   {self.t('games')}: {self.stats.get('games', 0)}",
                     54)
        y = 88
        for category, questions in self.packs:
            answered = self.stats["answered"].get(category, 0)
            percent = success_percent(self.stats, category)
            percent_text = f"{percent}%" if percent is not None else "-"
            line = f"{category}: {self.t('answered')} {answered}  {self.t('success')} {percent_text}"
            surface.blit(self.font.render(line, True, (255, 255, 255)), (60, y))
            y += 20
        self._draw_buttons(surface)

    def _draw_about(self, surface):
        y = 14
        for i, line in enumerate(ABOUT_LINES):
            color = (255, 224, 128) if i == 0 else (255, 255, 255)
            surface.blit(self.small.render(line, True, color), (30, y))
            y += 10
        self._draw_buttons(surface)

    def _draw_buttons(self, surface):
        for button in self.buttons:
            if not button.label:
                continue
            pygame.draw.rect(surface, (144, 160, 192), button.rect)
            pygame.draw.rect(surface, (255, 255, 255), button.rect, 1)
            text = self.font.render(button.label, True, (16, 16, 32))
            surface.blit(text, (button.rect.x + 8,
                                button.rect.y + button.rect.height // 2 - text.get_height() // 2))


def main(argv):
    questions_dir = argv[1] if len(argv) > 1 else None
    pygame.init()
    app = GnosisApp(questions_dir=questions_dir)
    app.run()


if __name__ == "__main__":
    main(sys.argv)
