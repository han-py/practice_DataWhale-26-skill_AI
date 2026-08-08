# -*- coding: utf-8 -*-
import math
import random
import threading
import time
import wave
import struct
from pathlib import Path
import tkinter as tk

try:
    import winsound
except ImportError:  # pragma: no cover
    winsound = None

SCRIPT_DIR = Path(__file__).resolve().parent
MUSIC_FILE = SCRIPT_DIR / "happy_music.wav"

WIDTH = 0
HEIGHT = 0
COLORS = ["#ff6b6b", "#ffd166", "#06d6a0", "#4cc9f0", "#ff9f1c", "#f72585", "#ff7ad9", "#9b5de5"]

root = None
canvas = None
stars = []
clouds = []
rockets = []
particles = []
flash_particles = []
launch_timer = 0
intro_time = 0.0
music_started = False


def generate_music_file(path, duration_sec=24, sample_rate=22050):
    if path.exists():
        return path

    amplitude = 30000
    frames = []
    bpm = 96
    beat_samples = int(sample_rate * 60 / bpm)
    melody = [523.25, 659.25, 783.99, 659.25, 587.33, 523.25, 392.00, 440.00]
    chords = [261.63, 329.63, 392.00]
    note_len = beat_samples * 2
    total_samples = int(sample_rate * duration_sec)
    t = 0

    while t < total_samples:
        note_idx = (t // note_len) % len(melody)
        base = melody[note_idx]
        chord = [base, base * 1.26, base * 1.5]
        for i in range(min(note_len, total_samples - t)):
            sample = 0.0
            for freq in chord:
                sample += math.sin(2 * math.pi * freq * (t + i) / sample_rate) * 0.18
            for freq in [chords[(note_idx // 2) % len(chords)], chords[(note_idx // 2 + 1) % len(chords)]]:
                sample += math.sin(2 * math.pi * freq * (t + i) / sample_rate) * 0.08
            envelope = min(1.0, max(0.0, 1.0 - (i / (note_len * 0.9))))
            sample *= envelope
            sample = max(-1.0, min(1.0, sample))
            frames.append(int(sample * amplitude))
        t += note_len

    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        wav.writeframes(b"".join(struct.pack("<h", s) for s in frames))
    return path


def ensure_music_file():
    return generate_music_file(MUSIC_FILE)


def play_music_file():
    global music_started
    if winsound is None:
        return
    if music_started:
        return
    try:
        path = ensure_music_file()
        winsound.PlaySound(str(path), winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_LOOP)
        music_started = True
    except Exception:
        music_started = False


def stop_music_file():
    global music_started
    if winsound is None:
        return
    try:
        winsound.PlaySound(None, winsound.SND_PURGE)
    except Exception:
        pass
    music_started = False


def create_stars(width, height):
    stars.clear()
    for _ in range(260):
        stars.append((
            random.randint(0, int(width)),
            random.randint(0, int(height * 0.85)),
            random.uniform(0.7, 2.8),
            random.uniform(0.5, 1.4),
            random.uniform(0.0, 6.28),
        ))


def create_clouds(width, height):
    clouds.clear()
    for _ in range(10):
        clouds.append({
            "x": random.randint(0, int(width)),
            "y": random.randint(60, int(height * 0.3)),
            "size": random.uniform(0.9, 1.5),
            "speed": random.uniform(0.15, 0.45),
        })


def spawn_rocket():
    rockets.append({
        "x": random.randint(80, WIDTH - 80),
        "y": HEIGHT + 20,
        "tx": random.randint(80, WIDTH - 80),
        "ty": random.randint(80, HEIGHT // 2),
        "color": random.choice(COLORS),
        "speed": random.uniform(8, 13),
        "trail": [],
    })


def explode(rocket):
    for _ in range(110):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(2.0, 7.2)
        particles.append({
            "x": rocket["tx"],
            "y": rocket["ty"],
            "vx": math.cos(angle) * speed,
            "vy": math.sin(angle) * speed,
            "life": random.randint(40, 90),
            "size": random.uniform(2.0, 5.0),
            "color": rocket["color"],
        })


def spawn_click_burst(x, y):
    for _ in range(50):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(2.4, 7.8)
        particles.append({
            "x": x,
            "y": y,
            "vx": math.cos(angle) * speed,
            "vy": math.sin(angle) * speed,
            "life": random.randint(30, 75),
            "size": random.uniform(2.0, 5.5),
            "color": random.choice(COLORS),
        })
        flash_particles.append({
            "x": x,
            "y": y,
            "life": 12,
            "size": random.uniform(3.0, 6.0),
            "color": random.choice(COLORS),
        })


def draw_background(frame_time):
    canvas.create_rectangle(0, 0, WIDTH, HEIGHT, fill="#040615", outline="")
    for y in range(0, HEIGHT, 18):
        ratio = y / max(1, HEIGHT)
        r = int(10 + 22 * ratio)
        g = int(12 + 18 * ratio)
        b = int(34 + 36 * ratio)
        color = f"#{r:02x}{g:02x}{b:02x}"
        canvas.create_rectangle(0, y, WIDTH, y + 18, fill=color, outline="")

    for x, y, size, alpha, phase in stars:
        twinkle = 0.65 + 0.35 * math.sin(frame_time * 1.3 + phase)
        glow = int(180 + twinkle * 70)
        color = f"#{glow:02x}{glow:02x}{glow:02x}"
        canvas.create_oval(x, y, x + size, y + size, fill=color, outline="")

    for cloud in clouds:
        cloud["x"] += cloud["speed"] * 0.6
        if cloud["x"] > WIDTH + 160:
            cloud["x"] = -180
            cloud["y"] = random.randint(50, int(HEIGHT * 0.3))
        cx = cloud["x"]
        cy = cloud["y"]
        scale = cloud["size"]
        canvas.create_oval(cx, cy, cx + 110 * scale, cy + 60 * scale, fill="#ffffff", outline="", stipple="gray50")
        canvas.create_oval(cx + 32 * scale, cy - 6 * scale, cx + 128 * scale, cy + 46 * scale, fill="#ffffff", outline="", stipple="gray50")
        canvas.create_oval(cx + 58 * scale, cy + 6 * scale, cx + 142 * scale, cy + 54 * scale, fill="#ffffff", outline="", stipple="gray50")

    moon_x = WIDTH * 0.82 + math.sin(frame_time * 0.3) * 25
    moon_y = HEIGHT * 0.16 + math.cos(frame_time * 0.2) * 20
    canvas.create_oval(moon_x - 90, moon_y - 90, moon_x + 90, moon_y + 90, fill="#f7e3a5", outline="")
    canvas.create_oval(moon_x - 60, moon_y - 60, moon_x + 60, moon_y + 60, fill="#040615", outline="")

    light_x = WIDTH * 0.18 + math.sin(frame_time * 0.5) * 40
    light_y = HEIGHT * 0.24 + math.cos(frame_time * 0.4) * 30
    glow_size = 180 + 25 * math.sin(frame_time * 0.8)
    canvas.create_oval(light_x - glow_size, light_y - glow_size, light_x + glow_size, light_y + glow_size, fill="#8de9ff", outline="")

    for i in range(4):
        y_top = HEIGHT * 0.68 + i * 22 + math.sin(frame_time * 0.6 + i) * 16
        y_bottom = HEIGHT * 0.86 + i * 14 + math.cos(frame_time * 0.5 + i) * 16
        canvas.create_polygon(
            0, HEIGHT,
            WIDTH * 0.1 + i * 120, y_top,
            WIDTH * 0.3 + i * 100, HEIGHT * 0.74,
            WIDTH * 0.55 + i * 70, y_bottom,
            WIDTH, HEIGHT,
            fill="#0a1b31", outline=""
        )


def update_fireworks():
    global launch_timer
    launch_timer += 1
    if launch_timer % 16 == 0:
        spawn_rocket()

    for rocket in rockets[:]:
        dx = rocket["tx"] - rocket["x"]
        dy = rocket["ty"] - rocket["y"]
        dist = math.hypot(dx, dy)
        if dist < 6:
            explode(rocket)
            rockets.remove(rocket)
            continue
        step = min(rocket["speed"], dist)
        rocket["x"] += dx / dist * step
        rocket["y"] += dy / dist * step
        rocket["trail"].append((rocket["x"], rocket["y"]))
        if len(rocket["trail"]) > 10:
            rocket["trail"].pop(0)
        for px, py in rocket["trail"]:
            canvas.create_oval(px, py, px + 1.2, py + 1.2, fill=rocket["color"], outline="")
        canvas.create_oval(rocket["x"] - 3, rocket["y"] - 3, rocket["x"] + 3, rocket["y"] + 3, fill=rocket["color"], outline="")

    for particle in particles[:]:
        particle["x"] += particle["vx"]
        particle["y"] += particle["vy"]
        particle["vx"] *= 0.96
        particle["vy"] *= 0.96
        particle["vy"] += 0.018
        particle["life"] -= 1
        particle["size"] *= 0.985
        if particle["life"] <= 0:
            particles.remove(particle)
            continue
        canvas.create_oval(
            particle["x"] - particle["size"],
            particle["y"] - particle["size"],
            particle["x"] + particle["size"],
            particle["y"] + particle["size"],
            fill=particle["color"],
            outline="",
        )

    for flash in flash_particles[:]:
        flash["life"] -= 1
        if flash["life"] <= 0:
            flash_particles.remove(flash)
            continue
        alpha = flash["life"] / 12
        canvas.create_oval(
            flash["x"] - flash["size"] * alpha,
            flash["y"] - flash["size"] * alpha,
            flash["x"] + flash["size"] * alpha,
            flash["y"] + flash["size"] * alpha,
            fill=flash["color"],
            outline="",
        )


def draw_title(frame_time):
    global intro_time
    intro_time += 0.016
    progress = min(1.0, intro_time / 2.8)
    ease = 3 * progress * progress - 2 * progress * progress * progress

    y = HEIGHT * 0.72 + math.sin(frame_time * 1.8) * 10
    scale = 1.0 + 0.05 * math.sin(frame_time * 2.6)
    size = int(74 + 14 * scale + 24 * ease)

    canvas.create_text(WIDTH / 2 + 2, y + 4, text="天天开心", fill="#120d20", font=("Microsoft YaHei", size, "bold"))
    canvas.create_text(WIDTH / 2, y, text="天天开心", fill="#fff7b2", font=("Microsoft YaHei", size, "bold"))

    sub_y = y + 82
    canvas.create_text(WIDTH / 2, sub_y, text="愿你笑容如花，心情如春", fill="#ffe6f2", font=("Microsoft YaHei", 24, "bold"))
    canvas.create_text(WIDTH / 2, sub_y + 42, text="点击屏幕，点亮更多祝福", fill="#9cf6ff", font=("Microsoft YaHei", 18, "bold"))

    if progress > 0.2:
        canvas.create_oval(
            WIDTH * 0.18 - 180, HEIGHT * 0.22 - 140, WIDTH * 0.18 + 180, HEIGHT * 0.22 + 140,
            fill="#ffffff", outline=""
        )

    if progress > 0.6:
        canvas.create_text(
            WIDTH / 2,
            HEIGHT * 0.45,
            text="电影感祝福",
            fill="#ffd166",
            font=("Microsoft YaHei", 24, "bold"),
        )


def animate():
    global WIDTH, HEIGHT
    canvas.delete("all")
    frame_time = time.time()
    if WIDTH == 0 or HEIGHT == 0:
        WIDTH = root.winfo_screenwidth()
        HEIGHT = root.winfo_screenheight()
        canvas.configure(width=WIDTH, height=HEIGHT)
        create_stars(WIDTH, HEIGHT)
        create_clouds(WIDTH, HEIGHT)
    draw_background(frame_time)
    update_fireworks()
    draw_title(frame_time)
    root.after(16, animate)


def on_click(event):
    spawn_click_burst(event.x, event.y)
    try:
        import winsound
        winsound.Beep(1700, 60)
    except Exception:
        pass


def on_close():
    stop_music_file()
    root.destroy()


def build_app():
    global root, canvas
    root = tk.Tk()
    root.title("天天开心")
    root.configure(bg="#040615")
    root.attributes("-topmost", True)
    root.attributes("-fullscreen", True)
    root.bind("<Escape>", lambda _: on_close())
    root.bind("<Button-1>", on_click)
    root.protocol("WM_DELETE_WINDOW", on_close)

    canvas = tk.Canvas(root, bg="#040615", highlightthickness=0)
    canvas.pack(fill="both", expand=True)
    root.update_idletasks()
    global WIDTH, HEIGHT
    WIDTH = root.winfo_screenwidth()
    HEIGHT = root.winfo_screenheight()
    canvas.configure(width=WIDTH, height=HEIGHT)
    create_stars(WIDTH, HEIGHT)
    create_clouds(WIDTH, HEIGHT)
    play_music_file()
    animate()
    root.mainloop()


def main():
    build_app()


if __name__ == "__main__":
    main()
