#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

WORLD CLOCK II (FR) — Horloge à mots française pour le terminal (curses / VT100-ANSI).

Grille (11 x 10, façade QLOCKTWO standard ; les lettres inutilisées sont du remplissage) :

    I L N E S T O D E U X
    Q U A T R E T R O I S
    N E U F U N E S E P T
    H U I T S I X C I N Q
    M I D I X M I N U I T
    O N Z E R H E U R E S
    M O I N S O L E D I X
    E T R Q U A R T P M D
    V I N G T - C I N Q U
    E T S D E M I E P A M

Les mots de l'heure courante (arrondie aux 5 minutes inférieures) s'allument
en ROUGE, le reste reste gris foncé. Quitter avec 'q' ou Ctrl-C.
"""

import curses
import locale
import time

ROWS = (
    list("ILNESTODEUX"),
    list("QUATRETROIS"),
    list("NEUFUNESEPT"),
    list("HUITSIXCINQ"),
    list("MIDIXMINUIT"),
    list("ONZERHEURES"),
    list("MOINSOLEDIX"),
    list("ETRQUARTPMD"),
    list("VINGT-CINQU"),
    list("ETSDEMIEPAM"),
)

CELL_W = 3

# mot -> (ligne, première cellule, nombre de cellules)
# CINQ/DIX en double : _M = minutes, _H = heure. MIDI et DIX_H partagent des lettres.
WORDS = {
    "IL":      (0, 0, 2),
    "EST":     (0, 3, 3),
    "DEUX":    (0, 7, 4),
    "QUATRE":  (1, 0, 6),
    "TROIS":   (1, 6, 5),
    "NEUF":    (2, 0, 4),
    "UNE":     (2, 4, 3),
    "SEPT":    (2, 7, 4),
    "HUIT":    (3, 0, 4),
    "SIX":     (3, 4, 3),
    "CINQ_H":  (3, 7, 4),
    "MIDI":    (4, 0, 4),
    "DIX_H":   (4, 2, 3),
    "MINUIT":  (4, 5, 6),
    "ONZE":    (5, 0, 4),
    "HEURE":   (5, 5, 5),
    "HEURES":  (5, 5, 6),
    "MOINS":   (6, 0, 5),
    "LE":      (6, 6, 2),
    "DIX_M":   (6, 8, 3),
    "ET_Q":    (7, 0, 2),
    "QUART":   (7, 3, 5),
    "VINGT":   (8, 0, 5),
    "TRAIT":   (8, 5, 1),   # le trait d'union de VINGT-CINQ
    "CINQ_M":  (8, 6, 4),
    "ET_D":    (9, 0, 2),
    "DEMI":    (9, 3, 4),
    "DEMIE":   (9, 3, 5),
}

HOURS = {
    1: "UNE", 2: "DEUX", 3: "TROIS", 4: "QUATRE", 5: "CINQ_H", 6: "SIX",
    7: "SEPT", 8: "HUIT", 9: "NEUF", 10: "DIX_H", 11: "ONZE",
}

# bloc de 5 minutes -> mots des minutes (hors gestion demi/demie)
MINUTE_BLOCK = {
    5:  ("CINQ_M",),
    10: ("DIX_M",),
    15: ("ET_Q", "QUART"),
    20: ("VINGT",),
    25: ("VINGT", "TRAIT", "CINQ_M"),
    35: ("MOINS", "VINGT", "TRAIT", "CINQ_M"),
    40: ("MOINS", "VINGT"),
    45: ("MOINS", "LE", "QUART"),
    50: ("MOINS", "DIX_M"),
    55: ("MOINS", "CINQ_M"),
}


def active_words(hour24, m5):
    """Mots à allumer pour hour24:m5."""
    words = ["IL", "EST"]
    hour = hour24
    if m5 >= 35:                        # à partir de 35 min : "moins ..." vers l'heure suivante
        hour += 1
    hour %= 24

    if hour == 0:
        hour_words, special = ["MINUIT"], True
    elif hour == 12:
        hour_words, special = ["MIDI"], True
    else:
        h12 = ((hour - 1) % 12) + 1     # 1..11 (13h -> UNE, 23h -> ONZE)
        hour_words = [HOURS[h12], "HEURE" if h12 == 1 else "HEURES"]
        special = False

    words += hour_words
    if m5 == 30:
        # midi/minuit ET DEMI (masculin), sinon ET DEMIE
        words += ["ET_D", "DEMI" if special else "DEMIE"]
    elif m5 != 0:
        words += list(MINUTE_BLOCK[m5])
    return set(words)


def draw(stdscr, active):
    stdscr.erase()
    maxy, maxx = stdscr.getmaxyx()
    width = len(ROWS[0]) * CELL_W - 1
    y0 = max(0, (maxy - len(ROWS)) // 2)
    x0 = max(0, (maxx - width) // 2)

    dark = curses.color_pair(2) | curses.A_BOLD
    red = curses.color_pair(1) | curses.A_BOLD

    for r, row in enumerate(ROWS):
        if y0 + r >= maxy:
            break
        for c, cell in enumerate(row):
            x = x0 + c * CELL_W
            if x < maxx - 2:
                stdscr.addstr(y0 + r, x, cell, dark)

    for name in active:
        r, c0, n = WORDS[name]
        if y0 + r >= maxy:
            continue
        for c in range(c0, c0 + n):
            x = x0 + c * CELL_W
            if x < maxx - 2:
                stdscr.addstr(y0 + r, x, ROWS[r][c], red)
    stdscr.refresh()


def main(stdscr):
    curses.curs_set(0)
    if curses.has_colors():
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_RED, -1)
        curses.init_pair(2, curses.COLOR_BLACK, -1)
    stdscr.timeout(250)

    while True:
        t = time.localtime()
        active = active_words(t.tm_hour, t.tm_min - t.tm_min % 5)
        draw(stdscr, active)
        key = stdscr.getch()
        if key in (ord("q"), ord("Q")):
            break


if __name__ == "__main__":
    locale.setlocale(locale.LC_ALL, "")
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        pass
