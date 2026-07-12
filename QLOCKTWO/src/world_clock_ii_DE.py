#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WORLD CLOCK II (DE) — Deutsche Wortuhr für das Terminal (curses / VT100-ANSI).

Layout (11 x 10, QLOCKTWO-Standardfront; ungenutzte Buchstaben sind Füller):

    E S K I S T A F Ü N F
    Z E H N Z W A N Z I G
    D R E I V I E R T E L
    V O R F U N K N A C H
    H A L B A E L F Ü N F
    E I N S X A M Z W E I
    D R E I P M J V I E R
    S E C H S N L A C H T
    S I E B E N Z W Ö L F
    Z E H N E U N K U H R

Die Wörter der aktuellen Zeit (auf 5 Minuten abgerundet) leuchten ROT,
der Rest bleibt dunkelgrau. Beenden mit 'q' oder Strg-C.
"""

import curses
import locale
import time

ROWS = (
    list("ESKISTAFÜNF"),
    list("ZEHNZWANZIG"),
    list("DREIVIERTEL"),
    list("VORFUNKNACH"),
    list("HALBAELFÜNF"),
    list("EINSXAMZWEI"),
    list("DREIPMJVIER"),
    list("SECHSNLACHT"),
    list("SIEBENZWÖLF"),
    list("ZEHNEUNKUHR"),
)

CELL_W = 3

# Wortname -> (Zeile, erste Zelle, Anzahl Zellen)
# FÜNF/ZEHN doppelt: _M = Minuten, _H = Stunde. ELF/FÜNF und ZEHN/NEUN teilen sich Buchstaben.
WORDS = {
    "ES":      (0, 0, 2),
    "IST":     (0, 3, 3),
    "FÜNF_M":  (0, 7, 4),
    "ZEHN_M":  (1, 0, 4),
    "ZWANZIG": (1, 4, 7),
    "VIERTEL": (2, 4, 7),
    "VOR":     (3, 0, 3),
    "NACH":    (3, 7, 4),
    "HALB":    (4, 0, 4),
    "ELF":     (4, 5, 3),
    "FÜNF_H":  (4, 7, 4),
    "EIN":     (5, 0, 3),
    "EINS":    (5, 0, 4),
    "ZWEI":    (5, 7, 4),
    "DREI":    (6, 0, 4),
    "VIER":    (6, 7, 4),
    "SECHS":   (7, 0, 5),
    "ACHT":    (7, 7, 4),
    "SIEBEN":  (8, 0, 6),
    "ZWÖLF":   (8, 6, 5),
    "ZEHN_H":  (9, 0, 4),
    "NEUN":    (9, 3, 4),
    "UHR":     (9, 8, 3),
}

HOURS = {
    1: "EINS", 2: "ZWEI", 3: "DREI", 4: "VIER", 5: "FÜNF_H", 6: "SECHS",
    7: "SIEBEN", 8: "ACHT", 9: "NEUN", 10: "ZEHN_H", 11: "ELF", 12: "ZWÖLF",
}

# 5-Minuten-Block -> Minutenwörter
MINUTE_BLOCK = {
    5:  ("FÜNF_M", "NACH"),
    10: ("ZEHN_M", "NACH"),
    15: ("VIERTEL", "NACH"),
    20: ("ZWANZIG", "NACH"),
    25: ("FÜNF_M", "VOR", "HALB"),
    30: ("HALB",),
    35: ("FÜNF_M", "NACH", "HALB"),
    40: ("ZWANZIG", "VOR"),
    45: ("VIERTEL", "VOR"),
    50: ("ZEHN_M", "VOR"),
    55: ("FÜNF_M", "VOR"),
}


def active_words(hour24, m5):
    """Wortnamen, die für hour24:m5 leuchten sollen."""
    words = ["ES", "IST"]
    hour = hour24
    if m5 >= 25:                        # ab 25 min zählt die nächste Stunde ("fünf vor halb")
        hour += 1
    hour = ((hour - 1) % 12) + 1
    if m5 == 0:
        # "ES IST EIN UHR" (ohne S), sonst volle Stundenwörter
        words += ["EIN" if hour == 1 else HOURS[hour], "UHR"]
    else:
        words += list(MINUTE_BLOCK[m5]) + [HOURS[hour]]
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
    locale.setlocale(locale.LC_ALL, "")  # Umlaute korrekt ausgeben
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        pass
