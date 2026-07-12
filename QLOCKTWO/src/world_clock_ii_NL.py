#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WORLD CLOCK II — Nederlandse woordklok voor de terminal (curses / VT100-ANSI).

Werking:
  * De volledige tekst staat altijd op het scherm, in vaste volgorde,
    zeven regels, vast-breed font (dat regelt de terminal zelf).
  * Elke 5 minuten (mm % 5 == 0) kleuren de woorden die de tijd vormen
    1 minuut lang ROOD; daarna is alles weer zwart.
  * Zwart wordt getoond als "helder zwart" (donkergrijs), anders is de
    tekst op een zwarte terminalachtergrond onzichtbaar.

Stoppen: toets 'q' of Ctrl-C.
"""

import curses
import time

REGELS = (
    "HET IS KWART TIEN",
    "VIJF MINUTEN OVER",
    "VOOR HALF ZEVEN",
    "VIER ACHT TWAALF",
    "EEN ZES TIEN DRIE",
    "TWEE NEGEN",
    "VIJF ELF UUR",
)

# woordnaam -> (regel, kolom, lengte)
# VIJF en TIEN staan er twee keer in: _M = minuten-woord, _U = uur-woord.
WOORDEN = {
    "HET":     (0,  0, 3),
    "IS":      (0,  4, 2),
    "KWART":   (0,  7, 5),
    "TIEN_M":  (0, 13, 4),
    "VIJF_M":  (1,  0, 4),
    "MINUTEN": (1,  5, 7),
    "OVER":    (1, 13, 4),
    "VOOR":    (2,  0, 4),
    "HALF":    (2,  5, 4),
    "ZEVEN":   (2, 10, 5),
    "VIER":    (3,  0, 4),
    "ACHT":    (3,  5, 4),
    "TWAALF":  (3, 10, 6),
    "EEN":     (4,  0, 3),
    "ZES":     (4,  4, 3),
    "TIEN_U":  (4,  8, 4),
    "DRIE":    (4, 13, 4),
    "TWEE":    (5,  0, 4),
    "NEGEN":   (5,  5, 5),
    "VIJF_U":  (6,  0, 4),
    "ELF":     (6,  5, 3),
    "UUR":     (6,  9, 3),
}

UREN = {
    1: "EEN", 2: "TWEE", 3: "DRIE", 4: "VIER", 5: "VIJF_U", 6: "ZES",
    7: "ZEVEN", 8: "ACHT", 9: "NEGEN", 10: "TIEN_U", 11: "ELF", 12: "TWAALF",
}

# Minutenblok -> woorden vóór het uur-woord.
MINUTENBLOK = {
    5:  ("VIJF_M", "MINUTEN", "OVER"),
    10: ("TIEN_M", "MINUTEN", "OVER"),
    15: ("KWART", "OVER"),
    20: ("TIEN_M", "MINUTEN", "VOOR", "HALF"),
    25: ("VIJF_M", "MINUTEN", "VOOR", "HALF"),
    30: ("HALF",),
    35: ("VIJF_M", "MINUTEN", "OVER", "HALF"),
    40: ("TIEN_M", "MINUTEN", "OVER", "HALF"),
    45: ("KWART", "VOOR"),
    50: ("TIEN_M", "MINUTEN", "VOOR"),
    55: ("VIJF_M", "MINUTEN", "VOOR"),
}


def actieve_woorden(uur24, m5):
    """Geef de set woordnamen die rood moeten kleuren voor uur24:m5."""
    woorden = ["HET", "IS"]
    uur = uur24
    if m5 >= 20:                       # vanaf 20 min praten we naar het volgende uur toe
        uur += 1
    uur = ((uur - 1) % 12) + 1         # 24u -> 1..12 (0:xx en 12:xx -> TWAALF)
    if m5 == 0:
        woorden += [UREN[uur], "UUR"]  # "HET IS <uur> UUR"
    else:
        woorden += list(MINUTENBLOK[m5]) + [UREN[uur]]
    return set(woorden)


def teken(stdscr, actief):
    stdscr.erase()
    maxy, maxx = stdscr.getmaxyx()
    breedte = max(len(r) for r in REGELS)
    y0 = max(0, (maxy - len(REGELS)) // 2)
    x0 = max(0, (maxx - breedte) // 2)

    zwart = curses.color_pair(2) | curses.A_BOLD   # "helder zwart" = donkergrijs
    rood = curses.color_pair(1) | curses.A_BOLD

    # Basistekst: alles zwart.
    for i, regel in enumerate(REGELS):
        if y0 + i < maxy:
            stdscr.addnstr(y0 + i, x0, regel, max(0, maxx - x0 - 1), zwart)

    # Actieve woorden rood eroverheen.
    for naam in actief:
        rij, kol, lengte = WOORDEN[naam]
        if y0 + rij < maxy:
            tekst = REGELS[rij][kol:kol + lengte]
            stdscr.addnstr(y0 + rij, x0 + kol, tekst,
                           max(0, maxx - (x0 + kol) - 1), rood)
    stdscr.refresh()


def main(stdscr):
    curses.curs_set(0)
    if curses.has_colors():
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_RED, -1)
        curses.init_pair(2, curses.COLOR_BLACK, -1)
    stdscr.timeout(250)  # 4x per seconde controleren; getch() slaapt intussen

    while True:
        t = time.localtime()
        # Tijd altijd rood tonen, afgekapt op het laatste 5-minutenblok.
        actief = actieve_woorden(t.tm_hour, t.tm_min - t.tm_min % 5)
        teken(stdscr, actief)

        toets = stdscr.getch()
        if toets in (ord("q"), ord("Q")):
            break
        # curses.KEY_RESIZE wordt vanzelf opgevangen doordat elke cyclus
        # opnieuw wordt getekend met de actuele schermafmetingen.


if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        pass
