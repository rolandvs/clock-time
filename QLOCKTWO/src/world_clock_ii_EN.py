#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WORLD CLOCK II (EN) — English word clock for the terminal (curses / VT100-ANSI).

Layout (11 cells x 10 rows, QLOCKTWO-style; unused letters are filler):

    I T L I S A S A M P M
    A C Q U A R T E R D C
    T W E N T Y F I V E X
    H A L F S T E N F T O
    P A S T E R U N I N E
    O N E S I X T H R E E
    F O U R F I V E T W O
    E I G H T E L E V E N
    S E V E N T W E L V E
    T E N S E O' C L O C K

The words forming the current time (snapped down to the last 5-minute
mark) light up RED; everything else stays dark grey. AM/PM lights up
with the half of the day. Quit with 'q' or Ctrl-C.
"""

import curses
import time

# Each row is a list of 11 cells ("O'" counts as one cell, as on the real clock).
ROWS = (
    list("ITLISASAMPM"),
    list("ACQUARTERDC"),
    list("TWENTYFIVEX"),
    list("HALFSTENFTO"),
    list("PASTERUNINE"),
    list("ONESIXTHREE"),
    list("FOURFIVETWO"),
    list("EIGHTELEVEN"),
    list("SEVENTWELVE"),
    ["T", "E", "N", "S", "E", "O'", "C", "L", "O", "C", "K"],
)

CELL_W = 3  # every cell is rendered 3 columns wide: letter (or O') + padding

# word name -> (row, first cell, number of cells)
# FIVE/TEN appear twice: _M = minutes word, _H = hour word.
WORDS = {
    "IT":      (0, 0, 2),
    "IS":      (0, 3, 2),
    "AM":      (0, 7, 2),
    "PM":      (0, 9, 2),
    "A":       (1, 0, 1),
    "QUARTER": (1, 2, 7),
    "TWENTY":  (2, 0, 6),
    "FIVE_M":  (2, 6, 4),
    "HALF":    (3, 0, 4),
    "TEN_M":   (3, 5, 3),
    "TO":      (3, 9, 2),
    "PAST":    (4, 0, 4),
    "NINE":    (4, 7, 4),
    "ONE":     (5, 0, 3),
    "SIX":     (5, 3, 3),
    "THREE":   (5, 6, 5),
    "FOUR":    (6, 0, 4),
    "FIVE_H":  (6, 4, 4),
    "TWO":     (6, 8, 3),
    "EIGHT":   (7, 0, 5),
    "ELEVEN":  (7, 5, 6),
    "SEVEN":   (8, 0, 5),
    "TWELVE":  (8, 5, 6),
    "TEN_H":   (9, 0, 3),
    "OCLOCK":  (9, 5, 6),
}

HOURS = {
    1: "ONE", 2: "TWO", 3: "THREE", 4: "FOUR", 5: "FIVE_H", 6: "SIX",
    7: "SEVEN", 8: "EIGHT", 9: "NINE", 10: "TEN_H", 11: "ELEVEN", 12: "TWELVE",
}

# 5-minute block -> minute words
MINUTE_BLOCK = {
    5:  ("FIVE_M", "PAST"),
    10: ("TEN_M", "PAST"),
    15: ("A", "QUARTER", "PAST"),
    20: ("TWENTY", "PAST"),
    25: ("TWENTY", "FIVE_M", "PAST"),
    30: ("HALF", "PAST"),
    35: ("TWENTY", "FIVE_M", "TO"),
    40: ("TWENTY", "TO"),
    45: ("A", "QUARTER", "TO"),
    50: ("TEN_M", "TO"),
    55: ("FIVE_M", "TO"),
}


def active_words(hour24, m5):
    """Return the set of word names to light up for hour24:m5."""
    words = ["IT", "IS", "AM" if hour24 < 12 else "PM"]
    hour = hour24
    if m5 >= 35:                        # from 35 min we speak towards the next hour
        hour += 1
    hour = ((hour - 1) % 12) + 1        # 24h -> 1..12 (0:xx and 12:xx -> TWELVE)
    if m5 == 0:
        words += [HOURS[hour], "OCLOCK"]
    else:
        words += list(MINUTE_BLOCK[m5]) + [HOURS[hour]]
    return set(words)


def draw(stdscr, active):
    stdscr.erase()
    maxy, maxx = stdscr.getmaxyx()
    width = len(ROWS[0]) * CELL_W - 1
    y0 = max(0, (maxy - len(ROWS)) // 2)
    x0 = max(0, (maxx - width) // 2)

    dark = curses.color_pair(2) | curses.A_BOLD   # "bright black" = dark grey
    red = curses.color_pair(1) | curses.A_BOLD

    # Base grid: everything dark.
    for r, row in enumerate(ROWS):
        if y0 + r >= maxy:
            break
        for c, cell in enumerate(row):
            x = x0 + c * CELL_W
            if x < maxx - len(cell):
                stdscr.addstr(y0 + r, x, cell, dark)

    # Active words in red on top.
    for name in active:
        r, c0, n = WORDS[name]
        if y0 + r >= maxy:
            continue
        for c in range(c0, c0 + n):
            cell = ROWS[r][c]
            x = x0 + c * CELL_W
            if x < maxx - len(cell):
                stdscr.addstr(y0 + r, x, cell, red)
    stdscr.refresh()


def main(stdscr):
    curses.curs_set(0)
    if curses.has_colors():
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_RED, -1)
        curses.init_pair(2, curses.COLOR_BLACK, -1)
    stdscr.timeout(250)  # poll 4x per second; getch() sleeps in between

    while True:
        t = time.localtime()
        # Always show the time in red, snapped down to the last 5-minute mark.
        active = active_words(t.tm_hour, t.tm_min - t.tm_min % 5)
        draw(stdscr, active)

        key = stdscr.getch()
        if key in (ord("q"), ord("Q")):
            break


if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        pass
