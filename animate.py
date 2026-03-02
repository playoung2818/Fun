#!/usr/bin/env python3
import curses
import time
import random
import os
import shutil
import subprocess
from wcwidth import wcswidth


TITLE = "HAKUNA MATTATA"
TAGLINE = "It means no worries… for the rest of your day~\nIt's a problem-free… philosophy~\nHappy Tuesday!"


POMPOMPURIN_FRAMES = [
    [
        "⢠⠋⠒⠙⡄⠀⣀⢴⠛⡦⣀⠀⠀⢠⠢⠔⡄",
        "⠀⠑⣀⣊⠤⠯⣥⣄⣀⣠⣬⠵⣀⡈⠢⠔⠁",
        "⣰⠋⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⠓⠦⣄",
        "⣏⠀⢠⠟⠀⠛⠀⢠⣤⠀⠶⠀⠘⣇⠀⠀⣹",
        "⠙⠒⣾⠀⠀⠀⠘⠚⠓⠚⠀⠀⠀⠙⡲⠚⠁",
        "⠀⢀⡾⠀⣀⠔⠒⢞⣫⡷⠖⠢⡀⠀⢧⠀⠀",
        "⠀⣼⠥⡀⢀⡀⣀⡜⠀⢣⣀⣀⠀⡴⠚⢦⠀",
        "⢸⠁⠀⠙⡀⠀⠀⠙⠒⠋⠀⠀⠨⠀⠀⢸⠀",
        "⠀⠳⣄⣠⠴⠤⠤⠤⠤⠤⠤⠤⠦⣤⡤⠋⠀",
    ]
]



CONFETTI_GLYPHS = list("*+o•··•o+*")


def center_x(maxx, text):
    return max(0, (maxx - wcswidth(text)) // 2)


def start_audio():
    """Start background audio with ffplay if available; return Popen or None."""
    repo = os.path.dirname(os.path.abspath(__file__))
    mp3 = os.path.join(repo, "assets", "Hakuna_matata.mp3")
    if not os.path.exists(mp3):
        return None
    # Try ffplay
    try:
        proc = subprocess.Popen(
            ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", mp3],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        return proc
    except FileNotFoundError:
        return None  # no ffplay installed


def stop_audio(proc):
    """Terminate audio process if still running."""
    if proc and proc.poll() is None:
        proc.terminate()
        time.sleep(0.2)
        if proc.poll() is None:
            proc.kill()


def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(60)  # ~16 FPS

    # Enable color if possible
    has_color = curses.has_colors()
    colors = [0]  # fallback
    if has_color:
        curses.start_color()
        try:
            curses.use_default_colors()
            default_bg = -1
        except Exception:
            default_bg = 0

        base_colors = [
            curses.COLOR_RED,
            curses.COLOR_YELLOW,
            curses.COLOR_GREEN,
            curses.COLOR_CYAN,
            curses.COLOR_BLUE,
            curses.COLOR_MAGENTA,
        ]
        max_pairs = max(1, min(len(base_colors), getattr(curses, "COLOR_PAIRS", 8) - 1))
        colors = []
        pair_idx = 1
        for c in base_colors:
            if pair_idx > max_pairs:
                break
            try:
                curses.init_pair(pair_idx, c, default_bg)
                colors.append(pair_idx)
                pair_idx += 1
            except curses.error:
                continue
        if not colors:
            has_color = False

    maxy, maxx = stdscr.getmaxyx()

    # Pompompurin position & velocity
    t = 0
    confetti = []

    # start centered based on frame 0 width
    first_frame = POMPOMPURIN_FRAMES[0]
    ly, lx = maxy // 2, center_x(maxx, first_frame[0])
    vy, vx = 1, 2

    while True:
        t += 1
        stdscr.erase()
        maxy, maxx = stdscr.getmaxyx()

        # Title (rainbow)
        title_x = center_x(maxx, TITLE)
        for i, ch in enumerate(TITLE):
            try:
                if has_color:
                    # cycle color pairs
                    pair = colors[(i + (t // 2)) % len(colors)]
                    stdscr.addstr(2, title_x + i, ch, curses.color_pair(pair) | curses.A_BOLD)
                else:
                    stdscr.addstr(2, title_x + i, ch, curses.A_BOLD)
            except curses.error:
                pass

        # Tagline — center each line separately
        base_y = 4
        for i, line in enumerate(TAGLINE.splitlines()):
            try:
                stdscr.addstr(base_y + i, center_x(maxx, line), line, curses.A_DIM)
            except curses.error:
                pass

        # Select animated frame
        frame_idx = (t // 6) % len(POMPOMPURIN_FRAMES)
        purin = POMPOMPURIN_FRAMES[frame_idx]
        purin_h = len(purin)
        purin_w = max(wcswidth(line) for line in purin)

        # Update bounce position
        ly += vy
        lx += vx

        if ly <= 6 or ly + purin_h >= maxy - 1:
            vy = -vy
            ly += vy
        if lx <= 0 or lx + purin_w >= maxx - 1:
            vx = -vx
            lx += vx

        # Draw Pompompurin
        for i, line in enumerate(purin):
            y = ly + i
            if 0 <= y < maxy:
                try:
                    stdscr.addstr(y, max(0, lx), line[: max(0, maxx - lx)])
                except curses.error:
                    pass

        # Confetti burst
        if t % 6 == 0 and len(confetti) < 120:
            for _ in range(6):
                confetti.append([
                    random.randint(0, maxx - 1),
                    6,
                    random.choice(CONFETTI_GLYPHS),
                    random.choice(colors) if (has_color and colors) else 0
                ])

        # Update confetti (falling)
        new_confetti = []
        for x, y, ch, col in confetti:
            y += 1
            if y < maxy - 1:
                new_confetti.append([x, y, ch, col])
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
        ch = stdscr.getch()
        if ch in (ord('q'), ord('Q')):
            break

        time.sleep(0.06)



if __name__ == "__main__":
    audio_proc = None
    try:
        audio_proc = start_audio()   # start song
        curses.wrapper(main)         # run animation
    except KeyboardInterrupt:
        pass
    finally:
        stop_audio(audio_proc)       # ensure song stops when you quit

