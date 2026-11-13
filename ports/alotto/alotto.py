#!/usr/bin/env python3
"""ALotto 2.06 - Python port of the Amiga BlitzBasic lottery program by Lukas Konias."""
import os
import random
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

MIN_NUM, MAX_NUM = 1, 49
PICKS = 6
DATA_FILE = "default.data"
DATA_MAGIC = b"DAT"

SCREEN_W, SCREEN_H = 640, 256
SCALE = 2

UI = {
    "en": {
        "title": "Lotto Screen.",
        "load": "Load data",
        "save": "Save data",
        "new": "New",
        "random": "Random",
        "calc1": "Calculate 1",
        "calc2": "Calculate 2",
        "calc3": "Calculate 3",
        "graphic": "Graphic",
        "editor": "Editor",
        "about": "About ALotto",
        "exit": "Exit",
        "help_on": "Help: ON",
        "help_off": "Help: OFF",
        "file_not_found": "File not found",
        "wrong_filetype": "Wrong filetype",
        "saved": "Data saved",
        "loaded": "Data loaded",
        "new_data": "New data file created",
        "editor_title": "Draw Editor",
        "add": "Add draw",
        "delete": "Delete",
        "done": "Done",
        "invalid": "Invalid input",
        "graphic_title": "Number frequency",
        "click_number": "Click here to enter a number of your choice.",
        "hold": "Tick this box to hold the number on the right.",
        "load_hint": "Click here to load a data file of your choice.",
        "save_hint": "Click here to save a data file that has been changed.",
        "new_hint": "Click here to create a new data file.",
        "edit_hint": "Click here to edit the data file in memory.",
        "exit_hint": "Click here to exit to Workbench/DOS.",
        "random_hint": "This button produces 1-6 random numbers.",
        "calc1_hint": "This button calculates the numbers using Algorithm 1 (hot numbers).",
        "calc2_hint": "This button calculates the numbers using Algorithm 2 (cold numbers).",
        "calc3_hint": "Uses a random combination and Algorithm 1 to calculate the numbers. Best option.",
        "graphic_hint": "Click here to get a graphical representation.",
        "about_hint": "Click here to learn more about the program.",
        "help_hint": "Click here to turn the Online Help on/off.",
        "lang_hint": "Use this button to change the language. Available: English and German.",
        "about_lines": [
            "This program has been written by Lukas Konias",
            "using Blitz Basic 2.1. It is the follow up",
            "version of ALotto 1.18.",
            "",
            "The program may be copied freely as long as",
            "the following conditions are fullfilled:",
            " 1) All files must remain unmodified",
            " 2) In case this program helps you to win in",
            "    the Lottery, you have to pay 1% of your",
            "    winnings to the author. Please be honest.",
            "    It is just 1%!",
            "",
            "If you have any suggestions, found some bugs",
            "or what ever write to: Lukas Konias",
            "(e-mail: smia1@mlucom2.urz.uni-halle.de)",
            "           TT 57010 Retziki",
            "           Thessaloniki/Greece",
            "",
            "PS. The Algorithms are fairly simple. So do",
            "not rely too much on them.",
        ],
    },
    "de": {
        "title": "Lotto PANTHEON",
        "load": "Laden",
        "save": "Sichern",
        "new": "Neu",
        "random": "Zufall",
        "calc1": "Berechnen 1",
        "calc2": "Berechnen 2",
        "calc3": "Berechnen 3",
        "graphic": "Graphik",
        "editor": "Editor",
        "about": "Über ALotto",
        "exit": "Ende",
        "help_on": "Hilfe: AN",
        "help_off": "Hilfe: AUS",
        "file_not_found": "Datei nicht gefunden",
        "wrong_filetype": "Falscher Dateityp",
        "saved": "Daten gesichert",
        "loaded": "Daten geladen",
        "new_data": "Neue Datei erstellt",
        "editor_title": "Ziehungs-Editor",
        "add": "Ziehung+",
        "delete": "Löschen",
        "done": "Fertig",
        "invalid": "Ungültige Eingabe",
        "graphic_title": "Zahlenhäufigkeit",
        "click_number": "Hier klicken um eine eigene Nummer einzugeben.",
        "hold": "Hier klicken um die Zahl rechts vor Veränderungen zu schützen.",
        "load_hint": "Hier klicken um eine beliebige Datei zu laden.",
        "save_hint": "Hier klicken um eine geänderte Datei zu sichern.",
        "new_hint": "Hier klicken um neu anzufangen.",
        "edit_hint": "Hier klicken um die Datei im Speicher zu ändern.",
        "exit_hint": "Hier klicken um ins Workbench/DOS zu kommen.",
        "random_hint": "Dieser Knopf erzeugt 1-6 zufällige Zahlen.",
        "calc1_hint": "Dieser Knopf benutzt den Algorithmus 1 (häufige Zahlen).",
        "calc2_hint": "Dieser Knopf benutzt den Algorithmus 2 (seltene Zahlen).",
        "calc3_hint": "Errechnet die Zahlen durch eine Kombination von Zufall und Algorithmus 1. Beste Option!",
        "graphic_hint": "Hier klicken um eine graphische Repräsentation zu erhalten.",
        "about_hint": "Hier klicken um mehr über das Programm zu erfahren.",
        "help_hint": "Hier klicken um die Online Hilfe zu aktivieren/deaktivieren.",
        "lang_hint": "Dieser Knopf wechselt die Sprache: English und Deutsch.",
        "about_lines": [
            "Dieses Programm wurde von Lukas Konias",
            "in Blitz Basic 2.1 geschrieben. Es ist die",
            "Nachfolgeversion von ALotto 1.18.",
            "",
            "Das Programm darf frei kopiert werden, solange",
            "folgende Bedingungen erfüllt sind:",
            " 1) Alle Dateien bleiben unverändert",
            " 2) Falls das Programm beim Lotteriesieg hilft,",
            "    gehen 1% des Gewinns an den Autor.",
            "    Bitte ehrlich sein. Es sind nur 1%!",
            "",
            "Bei Vorschlägen oder Fehlern schreibe an:",
            "Lukas Konias",
            "(e-mail: smia1@mlucom2.urz.uni-halle.de)",
            "           TT 57010 Retziki",
            "           Thessaloniki/Griechenland",
            "",
            "PS. Die Algorithmen sind recht einfach. Also",
            "verlasse dich nicht zu sehr darauf.",
        ],
    },
}


def load_data(path):
    with open(path, "rb") as fh:
        raw = fh.read()
    if raw[:3] == DATA_MAGIC:
        body = raw[3:]
        if len(body) % 6 != 0:
            raise ValueError("wrong filetype")
        draws = []
        for i in range(0, len(body), 6):
            draw = tuple(body[i + j] for j in range(6))
            if any(n < MIN_NUM or n > MAX_NUM for n in draw):
                raise ValueError("wrong filetype")
            draws.append(draw)
        return draws
    text = raw.decode("utf-8", "replace")
    draws = []
    for line in text.splitlines():
        nums = [int(t) for t in line.replace(",", " ").split() if t.isdigit()]
        if len(nums) == 6 and all(MIN_NUM <= n <= MAX_NUM for n in nums):
            draws.append(tuple(nums))
    return draws


def save_data(path, draws):
    with open(path, "wb") as fh:
        fh.write(DATA_MAGIC)
        for draw in draws:
            fh.write(bytes(draw))


def algorithm_random(draws, held):
    picked = list(held)
    while len(picked) < PICKS:
        n = random.randint(MIN_NUM, MAX_NUM)
        if n not in picked:
            picked.append(n)
    return picked


def frequencies(draws):
    counts = {n: 0 for n in range(MIN_NUM, MAX_NUM + 1)}
    for draw in draws:
        for n in draw:
            counts[n] += 1
    return counts


def algorithm_calc1(draws, held):
    counts = frequencies(draws)
    pool = [n for n in range(MIN_NUM, MAX_NUM + 1) if n not in held]
    random.shuffle(pool)
    pool.sort(key=lambda n: counts[n], reverse=True)
    return list(held) + pool[: PICKS - len(held)]


def algorithm_calc2(draws, held):
    counts = frequencies(draws)
    pool = [n for n in range(MIN_NUM, MAX_NUM + 1) if n not in held]
    random.shuffle(pool)
    pool.sort(key=lambda n: counts[n])
    return list(held) + pool[: PICKS - len(held)]


def algorithm_calc3(draws, held):
    counts = frequencies(draws)
    pool = [n for n in range(MIN_NUM, MAX_NUM + 1) if n not in held]
    random.shuffle(pool)
    half = (PICKS - len(held)) // 2
    hot = sorted(pool, key=lambda n: counts[n], reverse=True)[:half]
    rest = [n for n in pool if n not in hot]
    picked = list(held) + hot
    while len(picked) < PICKS:
        n = random.choice(rest)
        if n not in picked:
            picked.append(n)
    return picked


class Button:
    def __init__(self, rect, key, action, hint_key=None):
        self.rect = pygame.Rect(rect)
        self.key = key
        self.action = action
        self.hint_key = hint_key or key

    def label(self, lang):
        return UI[lang][self.key]


class ALottoApp:
    BG = (170, 170, 170)
    PANEL = (0, 85, 160)
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    ORANGE = (255, 136, 0)
    BLUE = (0, 0, 136)
    RED = (204, 0, 0)

    def __init__(self, data_path=DATA_FILE, scale=SCALE):
        pygame.init()
        self.scale = scale
        self.screen = pygame.display.set_mode((SCREEN_W * scale, SCREEN_H * scale))
        pygame.display.set_caption("ALotto 2.06 - Lotto Screen")
        self.font = pygame.font.Font(None, 20 * scale // 2 + 6)
        self.small = pygame.font.Font(None, 16 * scale // 2 + 4)
        self.lang = "en"
        self.help_on = True
        self.draws = []
        self.numbers = [0] * PICKS
        self.held = [False] * PICKS
        self.status = ""
        self.status_timer = 0
        self.view = "main"
        self.editor_input = ""
        self.editor_selected = -1
        self.data_path = data_path
        self.view_image = None
        if os.path.exists(data_path):
            try:
                self.draws = load_data(data_path)
            except (ValueError, OSError):
                self.draws = []
        self._build_ui()

    def _build_ui(self):
        s = self.scale
        self.buttons = [
            Button((8 * s, 24 * s, 92 * s, 18 * s), "load", self.act_load),
            Button((8 * s, 46 * s, 92 * s, 18 * s), "save", self.act_save),
            Button((8 * s, 68 * s, 92 * s, 18 * s), "new", self.act_new),
            Button((8 * s, 98 * s, 92 * s, 18 * s), "random", self.act_random),
            Button((8 * s, 120 * s, 92 * s, 18 * s), "calc1", self.act_calc1),
            Button((8 * s, 142 * s, 92 * s, 18 * s), "calc2", self.act_calc2),
            Button((8 * s, 164 * s, 92 * s, 18 * s), "calc3", self.act_calc3),
            Button((8 * s, 194 * s, 92 * s, 18 * s), "graphic", self.act_graphic),
            Button((8 * s, 216 * s, 92 * s, 18 * s), "editor", self.act_editor),
            Button((8 * s, 238 * s, 92 * s, 18 * s), "about", self.act_about),
        ]
        self.lang_btn = Button((520 * s, 4 * s, 70 * s, 16 * s), "lang", self.act_lang, "lang_hint")
        self.help_btn = Button((440 * s, 4 * s, 76 * s, 16 * s), "help", self.act_help, "help_hint")
        self.exit_btn = Button((594 * s, 4 * s, 42 * s, 16 * s), "exit", self.act_exit, "exit_hint")
        self.number_boxes = []
        self.hold_boxes = []
        for i in range(PICKS):
            y = (60 + i * 26) * s
            self.number_boxes.append(pygame.Rect((180 * s, y, 56 * s, 22 * s)))
            self.hold_boxes.append(pygame.Rect((246 * s, y + 4 * s, 14 * s, 14 * s)))
        self.editor_add = Button((300 * s, 60 * s, 120 * s, 20 * s), "add", self.act_editor_add)
        self.editor_delete = Button((300 * s, 86 * s, 120 * s, 20 * s), "delete", self.act_editor_delete)
        self.editor_done = Button((300 * s, 112 * s, 120 * s, 20 * s), "done", self.act_editor_done)

    def t(self, key):
        return UI[self.lang][key]

    def set_status(self, msg):
        self.status = msg
        self.status_timer = 180

    def act_lang(self):
        self.lang = "de" if self.lang == "en" else "en"

    def act_help(self):
        self.help_on = not self.help_on

    def act_exit(self):
        self.running = False

    def act_load(self):
        path = self._ask_file()
        if not path:
            return
        try:
            self.draws = load_data(path)
            self.set_status(f"{self.t('loaded')}: {os.path.basename(path)}")
        except (ValueError, OSError, UnicodeDecodeError):
            self.set_status(self.t("wrong_filetype"))

    def act_save(self):
        path = self._ask_file()
        if not path:
            return
        save_data(path, self.draws)
        self.set_status(f"{self.t('saved')}: {os.path.basename(path)}")

    def act_new(self):
        self.draws = []
        self.numbers = [0] * PICKS
        self.held = [False] * PICKS
        self.set_status(self.t("new_data"))

    def act_random(self):
        self.numbers = algorithm_random(self.draws, self._held_numbers())
        self.view = "main"

    def act_calc1(self):
        self.numbers = algorithm_calc1(self.draws, self._held_numbers())
        self.view = "main"

    def act_calc2(self):
        self.numbers = algorithm_calc2(self.draws, self._held_numbers())
        self.view = "main"

    def act_calc3(self):
        self.numbers = algorithm_calc3(self.draws, self._held_numbers())
        self.view = "main"

    def act_graphic(self):
        self.view = "graphic"

    def act_editor(self):
        self.view = "editor"

    def act_about(self):
        self.view = "about"

    def act_editor_add(self):
        nums = [int(t) for t in self.editor_input.replace(",", " ").split() if t.isdigit()]
        if len(nums) == 6 and all(MIN_NUM <= n <= MAX_NUM for n in nums):
            self.draws.append(tuple(nums))
            self.editor_input = ""
        else:
            self.set_status(self.t("invalid"))

    def act_editor_delete(self):
        if 0 <= self.editor_selected < len(self.draws):
            self.draws.pop(self.editor_selected)
            self.editor_selected = -1

    def act_editor_done(self):
        self.view = "main"

    def _held_numbers(self):
        return [self.numbers[i] for i in range(PICKS) if self.held[i] and self.numbers[i] != 0]

    def _ask_file(self):
        name = self.editor_input.strip() or self.data_path
        return name if os.path.exists(name) or name == self.data_path else None

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
            return
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return
        pos = event.pos
        if self.view == "main":
            for btn in self.buttons + [self.lang_btn, self.help_btn, self.exit_btn]:
                if btn.rect.collidepoint(pos):
                    btn.action()
                    return
            for i, box in enumerate(self.number_boxes):
                if box.collidepoint(pos):
                    self._enter_number(i)
                    return
            for i, box in enumerate(self.hold_boxes):
                if box.collidepoint(pos):
                    self.held[i] = not self.held[i]
                    return
        elif self.view == "editor":
            for btn in (self.editor_add, self.editor_delete, self.editor_done):
                if btn.rect.collidepoint(pos):
                    btn.action()
                    return
            for i in range(len(self.draws)):
                r = pygame.Rect((140 * self.scale, (40 + i * 14) * self.scale, 150 * self.scale, 14 * self.scale))
                if r.collidepoint(pos):
                    self.editor_selected = i
                    return
        elif self.view in ("graphic", "about"):
            self.view = "main"

    def _enter_number(self, idx):
        self.status = "Enter number 1-49, then press Enter"
        self.status_timer = 180
        self.numbers[idx] = 0
        self._pending_number = idx

    def type_digit(self, digit):
        idx = getattr(self, "_pending_number", None)
        if idx is None:
            return
        current = self.numbers[idx]
        new = (current * 10 + digit) if current else digit
        if new > MAX_NUM:
            new = digit
        self.numbers[idx] = new

    def confirm_number(self):
        idx = getattr(self, "_pending_number", None)
        if idx is None:
            return
        n = self.numbers[idx]
        if not (MIN_NUM <= n <= MAX_NUM):
            self.numbers[idx] = 0
        self._pending_number = None

    def _tooltip(self, mouse_pos):
        if not self.help_on:
            return None
        if self.view != "main":
            return None
        for btn in self.buttons + [self.lang_btn, self.help_btn, self.exit_btn]:
            if btn.rect.collidepoint(mouse_pos):
                return self.t(btn.hint_key)
        for i, box in enumerate(self.number_boxes):
            if box.collidepoint(mouse_pos):
                return self.t("click_number")
        for box in self.hold_boxes:
            if box.collidepoint(mouse_pos):
                return self.t("hold")
        return None

    def render(self, mouse_pos=(0, 0)):
        s = self.scale
        surf = self.screen
        surf.fill(self.BG)
        bar = pygame.Rect(0, 0, SCREEN_W * s, 20 * s)
        pygame.draw.rect(surf, self.PANEL, bar)
        title = self.font.render(f"ALotto 2.06  {self.t('title')}", True, self.WHITE)
        surf.blit(title, (8 * s, 3 * s))
        for btn in (self.lang_btn, self.help_btn, self.exit_btn):
            label = {
                "lang": "English|Deutsch" if self.lang == "en" else "Deutsch|English",
                "help": self.t("help_on") if self.help_on else self.t("help_off"),
                "exit": self.t("exit"),
            }[btn.key]
            self._draw_button(btn, label)
        if self.view == "main":
            self._render_main()
        elif self.view == "graphic":
            self._render_graphic()
        elif self.view == "editor":
            self._render_editor()
        elif self.view == "about":
            self._render_about()
        if self.status_timer > 0:
            self.status_timer -= 1
            st = self.small.render(self.status, True, self.BLACK)
            pygame.draw.rect(surf, self.WHITE, (120 * s, 236 * s, 400 * s, 16 * s))
            surf.blit(st, (124 * s, 238 * s))
        self._last_mouse = mouse_pos
        tip = self._tooltip(mouse_pos)
        if tip:
            self._render_tooltip(tip, mouse_pos)
        pygame.display.flip()

    def _draw_button(self, btn, label, active=False):
        s = self.scale
        color = self.ORANGE if active else self.PANEL
        pygame.draw.rect(self.screen, color, btn.rect)
        pygame.draw.rect(self.screen, self.BLACK, btn.rect, 1)
        text = self.small.render(label, True, self.WHITE)
        tw = text.get_width()
        self.screen.blit(text, (btn.rect.x + max(2, (btn.rect.w - tw) // 2), btn.rect.y + 2 * s))

    def _render_main(self):
        s = self.scale
        for btn in self.buttons:
            self._draw_button(btn, btn.label(self.lang))
        for i in range(PICKS):
            box = self.number_boxes[i]
            pygame.draw.rect(self.screen, self.WHITE, box)
            pygame.draw.rect(self.screen, self.BLACK, box, 2)
            n = self.numbers[i]
            if n:
                label = f"{n:02d}"
                color = self.RED if self.held[i] else self.BLUE
                text = self.font.render(label, True, color)
                self.screen.blit(text, (box.x + 14 * s, box.y + 2 * s))
            hb = self.hold_boxes[i]
            pygame.draw.rect(self.screen, self.WHITE, hb)
            pygame.draw.rect(self.screen, self.BLACK, hb, 1)
            if self.held[i]:
                pygame.draw.line(self.screen, self.RED, (hb.x + 2, hb.y + hb.h // 2), (hb.x + hb.w // 2 - 1, hb.bottom - 3), 2)
                pygame.draw.line(self.screen, self.RED, (hb.x + hb.w // 2 - 1, hb.bottom - 3), (hb.right - 2, hb.y + 2), 2)
        info = self.small.render(f"{len(self.draws)} draws in memory", True, self.BLACK)
        self.screen.blit(info, (300 * s, 60 * s))

    def _render_graphic(self):
        s = self.scale
        title = self.font.render(self.t("graphic_title"), True, self.BLACK)
        self.screen.blit(title, (140 * s, 30 * s))
        counts = frequencies(self.draws)
        if counts:
            peak = max(counts.values()) or 1
        else:
            peak = 1
        chart_x, chart_y, chart_h = 140 * s, 50 * s, 150 * s
        bar_w = 9 * s
        for n in range(MIN_NUM, MAX_NUM + 1):
            h = int(counts[n] / peak * chart_h)
            x = chart_x + (n - 1) * bar_w
            pygame.draw.rect(self.screen, self.BLUE, (x, chart_y + chart_h - h, bar_w - s, h))
            pygame.draw.rect(self.screen, self.BLACK, (x, chart_y + chart_h, bar_w - s, 1))
        for n in (1, 10, 20, 30, 40, 49):
            x = chart_x + (n - 1) * bar_w
            lbl = self.small.render(str(n), True, self.BLACK)
            self.screen.blit(lbl, (x, chart_y + chart_h + 2 * s))
        hint = self.small.render(self.t("exit_hint"), True, self.BLACK)
        self.screen.blit(hint, (140 * s, 230 * s))

    def _render_editor(self):
        s = self.scale
        title = self.font.render(self.t("editor_title"), True, self.BLACK)
        self.screen.blit(title, (140 * s, 24 * s))
        for btn in (self.editor_add, self.editor_delete, self.editor_done):
            self._draw_button(btn, btn.label(self.lang))
        entry = pygame.Rect(140 * s, 60 * s, 150 * s, 20 * s)
        pygame.draw.rect(self.screen, self.WHITE, entry)
        pygame.draw.rect(self.screen, self.BLACK, entry, 1)
        cur = self.small.render(self.editor_input, True, self.BLACK)
        self.screen.blit(cur, (entry.x + 4, entry.y + 3))
        for i, draw in enumerate(self.draws[:12]):
            r = pygame.Rect((140 * s, (86 + i * 12) * s, 150 * s, 12 * s))
            color = self.ORANGE if i == self.editor_selected else self.WHITE
            pygame.draw.rect(self.screen, color, r)
            text = self.small.render(" ".join(f"{n:02d}" for n in draw), True, self.BLACK)
            self.screen.blit(text, (r.x + 4, r.y))
        hint = self.small.render("Type: 3 7 12 22 33 41 then Add", True, self.BLACK)
        self.screen.blit(hint, (300 * s, 140 * s))

    def _render_about(self):
        s = self.scale
        y = 24 * s
        for line in self.t("about_lines"):
            text = self.small.render(line, True, self.BLACK)
            self.screen.blit(text, (140 * s, y))
            y += 9 * s
        copy = self.small.render("(c)1997 by Lukas Konias  L-Soft", True, self.BLUE)
        self.screen.blit(copy, (140 * s, y + 6 * s))

    def _render_tooltip(self, tip, mouse_pos):
        s = self.scale
        lines = tip.split(". ")
        width = max(self.small.size(line)[0] for line in lines) + 10
        height = len(lines) * 10 * s + 6
        x = max(0, min(mouse_pos[0], SCREEN_W * s - width))
        y = max(0, min(mouse_pos[1] + 12, SCREEN_H * s - height))
        panel = pygame.Rect(x, y, width, height)
        pygame.draw.rect(self.screen, (255, 255, 210), panel)
        pygame.draw.rect(self.screen, self.BLACK, panel, 1)
        for i, line in enumerate(lines):
            self.screen.blit(self.small.render(line, True, self.BLACK), (x + 5, y + 3 + i * 10 * s))

    def run(self, max_frames=None):
        self.running = True
        clock = pygame.time.Clock()
        frames = 0
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    elif event.unicode.isdigit():
                        self.type_digit(int(event.unicode))
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        self.confirm_number()
                else:
                    self.handle_event(event)
            self._last_mouse = pygame.mouse.get_pos()
            self.render(self._last_mouse)
            frames += 1
            if max_frames is not None and frames >= max_frames:
                break
            clock.tick(60)
        pygame.quit()


def main():
    data_path = sys.argv[1] if len(sys.argv) > 1 else DATA_FILE
    app = ALottoApp(data_path)
    app.run()


if __name__ == "__main__":
    main()
