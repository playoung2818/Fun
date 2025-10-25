#!/usr/bin/env python3
import sys, time, random, json, os
from pathlib import Path
from typing import List, Dict, Any

import pygame
from PIL import Image, ImageSequence

# ========== CONFIG ==========
RESOURCES_DIR_NAME = "resources"
STATE_FILENAME = "state.json"
STATIC_DISPLAY_MS = 1500
FLASH_COUNT = 3
SHAKE_DURATION = 0.8
SHAKE_MAG = 18
AUTO_CLOSE_AFTER = 1.2
FIT_MODE = "contain"   # or "cover"
# ============================

def exe_folder() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).parent

def discover_assets(res_dir: Path) -> List[Path]:
    desired_order = ["1.gif", "2.gif", "3.gif", "4.png"]
    assets = []
    for name in desired_order:
        p = res_dir / name
        if p.exists():
            assets.append(p)
    return assets

def read_state(state_path: Path) -> Dict[str, Any]:
    if not state_path.exists():
        return {"last_index": -1}
    try:
        return json.loads(state_path.read_text(encoding="utf8"))
    except Exception:
        return {"last_index": -1}

def write_state(state_path: Path, state: Dict[str, Any]):
    try:
        state_path.write_text(json.dumps(state), encoding="utf8")
    except Exception:
        pass

# ---------- GIF loader ----------
def load_gif_frames(path: Path, target_size: tuple):
    im = Image.open(path)
    frames = []
    for frame in ImageSequence.Iterator(im):
        fr = frame.convert("RGBA")
        fw, fh = fr.size
        tw, th = target_size
        if FIT_MODE == "contain":
            scale = min(tw / fw, th / fh)
        else:
            scale = max(tw / fw, th / fh)
        new_size = (max(1, int(fw * scale)), max(1, int(fh * scale)))
        # Pillow 10+
        fr = fr.resize(new_size, Image.Resampling.LANCZOS)
        data = fr.tobytes()
        surf = pygame.image.fromstring(data, fr.size, "RGBA").convert_alpha()
        dur = frame.info.get("duration", 100) if hasattr(frame, "info") else 100
        if dur <= 0:
            dur = 100
        frames.append({"surf": surf, "duration_ms": int(dur)})
    return frames

def wait_for_escape_or_timeout(timeout):
    end = time.time() + timeout
    while time.time() < end:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return True
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                return True
            if ev.type == pygame.MOUSEBUTTONDOWN:
                return True
        pygame.time.wait(20)
    return False

# ---------- Main ----------
def main():
    base = exe_folder()
    res_dir = base / RESOURCES_DIR_NAME
    if not res_dir.exists():
        print(f"[ERROR] resources folder not found: {res_dir}")
        sys.exit(1)

    assets = discover_assets(res_dir)
    if not assets:
        print("[ERROR] No supported images/gifs found in resources/")
        sys.exit(1)

    # rotation state
    state_path = base / STATE_FILENAME
    st = read_state(state_path)
    last = int(st.get("last_index", -1))
    idx = (last + 1) % len(assets)
    chosen = assets[idx]
    st["last_index"] = idx
    write_state(state_path, st)

    # --- pygame window (smaller, centered) ---
    os.environ["SDL_VIDEO_CENTERED"] = "1"  # must be set before set_mode
    pygame.init()
    pygame.display.set_caption("Surprise")

    info = pygame.display.Info()
    screen_w = int(info.current_w * 0.6)
    screen_h = int(info.current_h * 0.6)
    flags = 0  # windowed
    screen = pygame.display.set_mode((screen_w, screen_h), flags)

    screen.fill((0, 0, 0))
    pygame.display.flip()

    # small random delay with cancel
    if wait_for_escape_or_timeout(random.uniform(0.5, 2.5)):
        pygame.quit()
        return

    clock = pygame.time.Clock()
    t0 = time.time()
    shake_end = t0 + SHAKE_DURATION
    running = True

    suffix = chosen.suffix.lower()
    if suffix == ".gif":
        # Pre-scaled frames to window size
        frames = load_gif_frames(chosen, (screen_w, screen_h))
        if not frames:
            print("[ERROR] failed to load gif frames")
            pygame.quit()
            return

        frame_idx = 0
        frame_acc = 0
        total_duration = sum(f["duration_ms"] for f in frames) / 1000.0
        play_start = time.time()

        while running:
            dt = clock.tick(60)
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    running = False
                if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                    running = False
                if ev.type == pygame.MOUSEBUTTONDOWN:
                    running = False

            now = time.time()
            screen.fill((0, 0, 0))

            # draw current frame centered (shake briefly)
            surf = frames[frame_idx]["surf"]
            fw, fh = surf.get_size()
            x = (screen_w - fw) // 2
            y = (screen_h - fh) // 2

            if now < shake_end:
                progress = (shake_end - now) / max(0.001, SHAKE_DURATION)
                mag = int(SHAKE_MAG * progress)
                screen.blit(surf, (x + random.randint(-mag, mag),
                                   y + random.randint(-mag, mag)))
            else:
                screen.blit(surf, (x, y))

            pygame.display.flip()

            # advance frame by duration
            frame_acc += dt
            dur = frames[frame_idx]["duration_ms"]
            if frame_acc >= dur:
                frame_acc -= dur
                frame_idx += 1
                if frame_idx >= len(frames):
                    # finished gif; hold last frame briefly then exit
                    if now > (play_start + total_duration + AUTO_CLOSE_AFTER):
                        running = False
                    else:
                        frame_idx = len(frames) - 1

    else:
        # Static image (PNG/JPG) — no shake, stays until manually closed
        try:
            img = pygame.image.load(str(chosen)).convert_alpha()
        except Exception as e:
            print("[ERROR] failed to load image:", e)
            pygame.quit()
            return

        # Scale to window
        iw, ih = img.get_size()
        if FIT_MODE == "contain":
            scale = min(screen_w / iw, screen_h / ih)
        else:
            scale = max(screen_w / iw, screen_h / ih)
        new_size = (max(1, int(iw * scale)), max(1, int(ih * scale)))
        img = pygame.transform.smoothscale(img, new_size)

        # Optional: set to 0 to remove the white flash entirely
        flash_frames = FLASH_COUNT

        running = True
        clock = pygame.time.Clock()

        while running:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    running = False
                if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                    running = False
                if ev.type == pygame.MOUSEBUTTONDOWN:
                    running = False

            screen.fill((0, 0, 0))

            if flash_frames > 0:
                alpha = int(255 * (flash_frames / max(1, FLASH_COUNT)))
                flash = pygame.Surface((screen_w, screen_h))
                flash.fill((255, 255, 255))
                flash.set_alpha(alpha)
                screen.blit(flash, (0, 0))
                flash_frames -= 1
            else:
                # Centered draw, no shake
                x = (screen_w - img.get_width()) // 2
                y = (screen_h - img.get_height()) // 2
                screen.blit(img, (x, y))

            pygame.display.flip()
            clock.tick(60)

    wait_for_escape_or_timeout(0.6)
    pygame.quit()

if __name__ == "__main__":
    try:
        main()
    except Exception:
        pygame.quit()
        raise