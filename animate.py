#!/usr/bin/env python3
import curses
import time
import random
import os

# A simple terminal animation using curses.
# Shows rainbow "HAKUNA MATTATA" text, a bouncing TIMON_PUMBAA face, and confetti.

TITLE = "HAKUNA MATTATA"
TAGLINE = "it means no worries… for the rest of your code"
TIMON_PUMBAA = [
    r"   (\_/)            (\____/)   ",
    r"   ( •_•)           ( •(oo)• ) ",
    r"   /   🍃           (   (  )  )",

]


CONFETTI_GLYPHS = list("*+o•··•o+*")

def center_x(maxx, text):
    return max(0, (maxx - len(text)) // 2)

def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(60)  # ~16 FPS

    # Enable color if possible
    has_color = curses.has_colors()
    colors = [0]  # fallback
    num_pairs = 0

    if has_color:
        curses.start_color()
        # Try to allow default background; harmless if unsupported.
        try:
            curses.use_default_colors()
            default_bg = -1
        except Exception:
            default_bg = 0  # plain black bg

        # Pick a conservative set of foreground colors.
        base_colors = [
            curses.COLOR_RED,
            curses.COLOR_YELLOW,
            curses.COLOR_GREEN,
            curses.COLOR_CYAN,
            curses.COLOR_BLUE,
            curses.COLOR_MAGENTA,
        ]

        # Don’t exceed terminal’s available color pairs.
        max_pairs = max(1, min(len(base_colors), getattr(curses, "COLOR_PAIRS", 8) - 1))

        colors = []
        pair_idx = 1
        for c in base_colors:
            if pair_idx > max_pairs:
                break
            try:
                curses.init_pair(pair_idx, c, default_bg)
                colors.append(pair_idx)  # store the *pair number*, not the color code
                pair_idx += 1
            except curses.error:
                # If a color fails, skip it and continue
                continue

        num_pairs = len(colors)
        if num_pairs == 0:
            has_color = False  # fall back to monochrome


    maxy, maxx = stdscr.getmaxyx()

    # Lion position & velocity
    ly, lx = maxy // 2, center_x(maxx, TIMON_PUMBAA[0])
    vy, vx = 1, 2

    t = 0
    confetti = []

    while True:
        t += 1
        stdscr.erase()
        maxy, maxx = stdscr.getmaxyx()

        # Title (rainbow)
        title_x = center_x(maxx, TITLE)
        for i, ch in enumerate(TITLE):
            if has_color:
                color_idx = (i + t // 2) % min(len(colors), curses.COLOR_WHITE)
                color_pair = curses.color_pair((color_idx % len(colors)) + 1)
                stdscr.addstr(2, title_x + i, ch, color_pair | curses.A_BOLD)
            else:
                stdscr.addstr(2, title_x + i, ch, curses.A_BOLD)

        # Tagline (dim)
        tagline_x = center_x(maxx, TAGLINE)
        try:
            stdscr.addstr(4, tagline_x, TAGLINE, curses.A_DIM)
        except curses.error:
            pass

        # Update & draw bouncing lion
        ly += vy
        lx += vx

        # Bounce
        lion_h = len(TIMON_PUMBAA)
        lion_w = max(len(line) for line in TIMON_PUMBAA)
        if ly <= 6 or ly + lion_h >= maxy - 1:
            vy = -vy
            ly += vy
        if lx <= 0 or lx + lion_w >= maxx - 1:
            vx = -vx
            lx += vx

        for i, line in enumerate(TIMON_PUMBAA):
            y = ly + i
            if 0 <= y < maxy:
                try:
                    stdscr.addstr(y, max(0, lx), line[: maxx - lx])
                except curses.error:
                    pass

        # Confetti burst
        if t % 6 == 0 and len(confetti) < 120:
            # spawn a few confetti pieces at random positions near the top
            for _ in range(6):
                confetti.append([random.randint(0, maxx - 1), 6, random.choice(CONFETTI_GLYPHS),
                                 random.choice(range(1, len(colors) + 1)) if has_color else 0])

        # Update confetti (falling)
        new_confetti = []
        for x, y, ch, col in confetti:
            y += 1
            if y < maxy - 1:
                new_confetti.append([x, y, ch, col])
            # draw
            try:
                if has_color and col:
                    stdscr.addstr(y, x, ch, curses.color_pair(col))
                else:
                    stdscr.addstr(y, x, ch)
            except curses.error:
                pass
        confetti = new_confetti

        # Footer hint
        footer = "Press Q to quit"
        try:
            stdscr.addstr(maxy - 2, center_x(maxx, footer), footer, curses.A_DIM)
        except curses.error:
            pass

        # Handle input
        try:
            ch = stdscr.getch()
        except:
            ch = -1
        if ch in (ord('q'), ord('Q')):
            break

        time.sleep(0.06)

if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        pass
