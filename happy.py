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
auroras = []
confetti = []
rockets = []
particles = []
flash_particles = []
interactive_props = []
launch_timer = 0
intro_time = 0.0
music_started = False
camera_x = 0.0
camera_y = 0.0
camera_zoom = 1.0
scene_phase = 0
subtitle_index = 0
subtitle_timer = 0.0

subtitles = [
    "愿你今天也像星光一样明亮",
    "愿你像烟花一样绽放出笑意",
    "愿你的人生被好运和欢笑拥抱",
    "愿你每一天都充满阳光和幸福",
]


def generate_music_file(path, duration_sec=24, sample_rate=22050):
    if path.exists():
        return path

    amplitude = 32000
    frames = []
    bpm = 132
    beat_samples = int(sample_rate * 60 / bpm)
    melody = [523.25, 659.25, 783.99, 659.25, 587.33, 523.25, 392.00, 440.00, 523.25, 587.33, 659.25, 698.46]
    chords = [261.63, 329.63, 392.00, 440.00]
    note_len = max(1, beat_samples // 2)
    total_samples = int(sample_rate * duration_sec)
    t = 0
    note_idx = 0

    while t < total_samples:
        base = melody[note_idx % len(melody)]
        chord = [base, base * 1.26, base * 1.5]
        for i in range(min(note_len, total_samples - t)):
            sample = 0.0
            for freq in chord:
                sample += math.sin(2 * math.pi * freq * (t + i) / sample_rate) * 0.16
            for freq in [chords[(note_idx // 2) % len(chords)], chords[(note_idx // 2 + 1) % len(chords)]]:
                sample += math.sin(2 * math.pi * freq * (t + i) / sample_rate) * 0.07
            sample += math.sin(2 * math.pi * 880 * (t + i) / sample_rate) * 0.025 * (1.0 if i % 14 == 0 else 0.0)
            envelope = min(1.0, max(0.0, 1.0 - (i / (note_len * 0.92))))
            sample *= envelope
            sample = max(-1.0, min(1.0, sample))
            frames.append(int(sample * amplitude))
        t += note_len
        note_idx += 1

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
    for _ in range(12):
        clouds.append({
            "x": random.randint(0, int(width)),
            "y": random.randint(60, int(height * 0.3)),
            "size": random.uniform(0.9, 1.6),
            "speed": random.uniform(0.18, 0.5),
            "bounce": 0.0,
            "bounce_dir": 1.0,
            "bounce_timer": 0.0,
        })


def create_auroras(width, height):
    auroras.clear()
    for _ in range(6):
        auroras.append({
            "x": random.randint(-200, int(width + 200)),
            "y": random.randint(80, int(height * 0.35)),
            "length": random.randint(240, 420),
            "color": random.choice(["#4cc9f0", "#7bdff6", "#ff7ad9", "#ffd166"]),
            "phase": random.uniform(0, 6.28),
        })


def create_confetti(width, height):
    confetti.clear()
    symbols = ["✦", "✧", "✺", "❋", "•"]
    for _ in range(120):
        confetti.append({
            "x": random.randint(0, int(width)),
            "y": random.randint(-200, int(height)),
            "size": random.uniform(12, 24),
            "speed": random.uniform(0.7, 2.2),
            "phase": random.uniform(0, 6.28),
            "color": random.choice(COLORS),
            "symbol": random.choice(symbols),
        })


def create_interactive_props(width, height):
    interactive_props.clear()
    for i in range(8):
        x = width * (0.16 + i * 0.1 + random.uniform(-0.02, 0.02))
        y = height * (0.84 + random.uniform(-0.01, 0.02))
        kind = random.choice(["flower", "star", "balloon", "lantern"])
        interactive_props.append({
            "x": x,
            "y": y,
            "kind": kind,
            "scale": random.uniform(0.8, 1.2),
            "phase": random.uniform(0, 6.28),
            "pulse": random.uniform(0.0, 1.0),
            "bounce": random.uniform(0, 6.28),
        })


def spawn_rocket():
    rockets.append({
        "x": random.randint(80, WIDTH - 80),
        "y": HEIGHT + 20,
        "tx": random.randint(80, WIDTH - 80),
        "ty": random.randint(80, HEIGHT // 2),
        "color": random.choice(COLORS),
        "speed": random.uniform(9, 16),
        "trail": [],
    })


def explode(rocket):
    for _ in range(140):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(2.2, 8.5)
        particles.append({
            "x": rocket["tx"],
            "y": rocket["ty"],
            "vx": math.cos(angle) * speed,
            "vy": math.sin(angle) * speed,
            "life": random.randint(45, 100),
            "size": random.uniform(2.2, 5.5),
            "color": rocket["color"],
        })


def spawn_click_burst(x, y, kind="burst"):
    if kind == "cloud":
        for _ in range(35):
            particles.append({
                "x": x,
                "y": y,
                "vx": random.uniform(-2.2, 2.2),
                "vy": random.uniform(-1.5, 1.5),
                "life": random.randint(20, 45),
                "size": random.uniform(1.6, 3.2),
                "color": "#e6f7ff",
            })
    elif kind == "star":
        for _ in range(24):
            particles.append({
                "x": x,
                "y": y,
                "vx": math.cos(random.uniform(0, 2 * math.pi)) * random.uniform(0.8, 2.8),
                "vy": math.sin(random.uniform(0, 2 * math.pi)) * random.uniform(0.8, 2.8),
                "life": random.randint(20, 40),
                "size": random.uniform(1.4, 3.0),
                "color": "#fff7b2",
            })
    elif kind == "title":
        for _ in range(28):
            particles.append({
                "x": x,
                "y": y,
                "vx": random.uniform(-3.0, 3.0),
                "vy": random.uniform(-5.0, -1.0),
                "life": random.randint(40, 70),
                "size": random.uniform(2.2, 4.4),
                "color": random.choice(COLORS),
            })
        for _ in range(15):
            flash_particles.append({
                "x": x,
                "y": y,
                "life": 14,
                "size": random.uniform(5.0, 8.0),
                "color": random.choice(COLORS),
            })
    else:
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
    global camera_x, camera_y, camera_zoom

    def mix_color(color_a, color_b, t):
        a = [int(color_a[i:i + 2], 16) for i in (1, 3, 5)]
        b = [int(color_b[i:i + 2], 16) for i in (1, 3, 5)]
        c = [int(a[i] + (b[i] - a[i]) * t) for i in range(3)]
        return f"#{c[0]:02x}{c[1]:02x}{c[2]:02x}"

    canvas.create_rectangle(0, 0, WIDTH, HEIGHT, fill="#040615", outline="")

    for y in range(0, HEIGHT + 1, 10):
        ratio = y / max(1, HEIGHT)
        if ratio < 0.38:
            color = mix_color("#040615", "#142b4b", ratio / 0.38)
        elif ratio < 0.7:
            color = mix_color("#142b4b", "#7a6bb6", (ratio - 0.38) / 0.32)
        elif ratio < 0.86:
            color = mix_color("#7a6bb6", "#f2b56d", (ratio - 0.7) / 0.16)
        else:
            color = mix_color("#f2b56d", "#ffdca3", (ratio - 0.86) / 0.14)
        canvas.create_rectangle(0, y, WIDTH, y + 10, fill=color, outline="")

    for x, y, size, alpha, phase in stars:
        twinkle = 0.65 + 0.35 * math.sin(frame_time * 1.3 + phase)
        glow = int(180 + twinkle * 70)
        color = f"#{glow:02x}{glow:02x}{glow:02x}"
        ox = (x - WIDTH / 2) * camera_zoom + WIDTH / 2 + camera_x
        oy = (y - HEIGHT / 2) * camera_zoom + HEIGHT / 2 + camera_y
        canvas.create_oval(ox, oy, ox + size, oy + size, fill=color, outline="")
        canvas.create_oval(ox - 0.6, oy - 0.6, ox + size + 0.6, oy + size + 0.6, outline="#ffffff", width=1)

    sun_x = WIDTH * 0.5 + math.sin(frame_time * 0.18) * 24
    sun_y = HEIGHT * 0.22 + math.cos(frame_time * 0.14) * 12
    canvas.create_oval(sun_x - 220, sun_y - 220, sun_x + 220, sun_y + 220, fill="#ffe5a8", outline="")
    canvas.create_oval(sun_x - 170, sun_y - 170, sun_x + 170, sun_y + 170, fill="#ffd18c", outline="")
    canvas.create_oval(sun_x - 110, sun_y - 110, sun_x + 110, sun_y + 110, fill="#fff5c8", outline="")
    for i in range(12):
        angle = math.radians(i * 30)
        rx = sun_x + math.cos(angle) * 180
        ry = sun_y + math.sin(angle) * 180
        lx = sun_x + math.cos(angle) * 120
        ly = sun_y + math.sin(angle) * 120
        canvas.create_line(lx, ly, rx, ry, fill="#ffd9a4", width=2, stipple="gray25")
    canvas.create_oval(sun_x - 260, sun_y - 260, sun_x + 260, sun_y + 260, outline="#fff3cb", width=2)

    for cloud in clouds:
        cloud["x"] += cloud["speed"] * 0.55
        if cloud["x"] > WIDTH + 180:
            cloud["x"] = -220
            cloud["y"] = random.randint(50, int(HEIGHT * 0.32))
        if cloud["bounce_timer"] > 0:
            cloud["bounce_timer"] -= 0.016
            cloud["bounce"] += cloud["bounce_dir"] * 3.2
            if cloud["bounce"] > 7:
                cloud["bounce_dir"] = -1.0
            elif cloud["bounce"] < 0:
                cloud["bounce"] = 0.0
                cloud["bounce_dir"] = 1.0
                cloud["bounce_timer"] = 0.0
        else:
            cloud["bounce"] = max(0.0, cloud["bounce"] * 0.8)
        cx = cloud["x"]
        cy = cloud["y"] - cloud["bounce"]
        scale = cloud["size"]
        ox = (cx - WIDTH / 2) * camera_zoom + WIDTH / 2 + camera_x
        oy = (cy - HEIGHT / 2) * camera_zoom + HEIGHT / 2 + camera_y
        canvas.create_oval(ox, oy, ox + 110 * scale, oy + 58 * scale, fill="#f7fbff", outline="", stipple="gray50")
        canvas.create_oval(ox + 30 * scale, oy - 8 * scale, ox + 126 * scale, oy + 44 * scale, fill="#f7fbff", outline="", stipple="gray50")
        canvas.create_oval(ox + 56 * scale, oy + 6 * scale, ox + 138 * scale, oy + 50 * scale, fill="#f7fbff", outline="", stipple="gray50")
        canvas.create_line(ox + 24 * scale, oy + 28 * scale, ox + 82 * scale, oy + 18 * scale, fill="#dceeff", width=2, stipple="gray25")
        canvas.create_line(ox + 70 * scale, oy + 18 * scale, ox + 128 * scale, oy + 28 * scale, fill="#dceeff", width=2, stipple="gray25")

    glow_y = HEIGHT * 0.74
    canvas.create_oval(0, glow_y - 140, WIDTH, glow_y + 180, fill="#f7c97b", outline="")
    canvas.create_oval(0, glow_y - 100, WIDTH, glow_y + 140, fill="#f0b777", outline="")
    canvas.create_polygon(
        0, HEIGHT,
        WIDTH * 0.08, HEIGHT * 0.78,
        WIDTH * 0.24, HEIGHT * 0.74,
        WIDTH * 0.44, HEIGHT * 0.82,
        WIDTH * 0.66, HEIGHT * 0.70,
        WIDTH * 0.84, HEIGHT * 0.78,
        WIDTH, HEIGHT,
        fill="#355663", outline=""
    )
    canvas.create_polygon(
        0, HEIGHT,
        WIDTH * 0.12, HEIGHT * 0.84,
        WIDTH * 0.34, HEIGHT * 0.80,
        WIDTH * 0.56, HEIGHT * 0.86,
        WIDTH * 0.76, HEIGHT * 0.80,
        WIDTH, HEIGHT,
        fill="#4d7185", outline=""
    )
    canvas.create_polygon(
        0, HEIGHT,
        WIDTH * 0.18, HEIGHT * 0.90,
        WIDTH * 0.42, HEIGHT * 0.86,
        WIDTH * 0.66, HEIGHT * 0.90,
        WIDTH * 0.86, HEIGHT * 0.86,
        WIDTH, HEIGHT,
        fill="#6d93a5", outline=""
    )

    mist_band = HEIGHT * 0.86
    canvas.create_rectangle(0, mist_band, WIDTH, HEIGHT, fill="#163645", outline="")
    canvas.create_line(0, mist_band, WIDTH, mist_band, fill="#a6e7ff", width=2, stipple="gray25")

    for prop in interactive_props:
        sway = math.sin(frame_time * 1.1 + prop["phase"]) * 4
        bob = math.sin(frame_time * 1.7 + prop["bounce"]) * 3
        x = prop["x"] + sway
        y = prop["y"] + bob
        scale = prop["scale"]
        prop["draw_x"] = x
        prop["draw_y"] = y
        if prop["kind"] == "flower":
            canvas.create_oval(x - 8 * scale, y - 8 * scale, x + 8 * scale, y + 8 * scale, fill="#ff7aa2", outline="")
            canvas.create_oval(x - 5 * scale, y - 10 * scale, x + 5 * scale, y - 2 * scale, fill="#ffb6c1", outline="")
            canvas.create_oval(x - 10 * scale, y - 5 * scale, x - 2 * scale, y + 5 * scale, fill="#ffb6c1", outline="")
            canvas.create_oval(x + 2 * scale, y - 5 * scale, x + 10 * scale, y + 5 * scale, fill="#ffb6c1", outline="")
            canvas.create_oval(x - 5 * scale, y + 2 * scale, x + 5 * scale, y + 10 * scale, fill="#ffb6c1", outline="")
            canvas.create_line(x, y - 14 * scale, x, y - 24 * scale, fill="#69c17b", width=2)
        elif prop["kind"] == "star":
            canvas.create_text(x, y, text="✦", fill="#ffd166", font=("Microsoft YaHei", int(20 * scale), "bold"))
            canvas.create_text(x, y, text="✧", fill="#fff7b2", font=("Microsoft YaHei", int(12 * scale), "bold"))
        elif prop["kind"] == "balloon":
            canvas.create_oval(x - 10 * scale, y - 16 * scale, x + 10 * scale, y + 8 * scale, fill="#ff6b6b", outline="")
            canvas.create_line(x, y + 8 * scale, x, y + 26 * scale, fill="#ff9f1c", width=2)
            canvas.create_line(x, y + 26 * scale, x - 6, y + 34 * scale, fill="#ff9f1c", width=2)
        else:
            canvas.create_oval(x - 10 * scale, y - 16 * scale, x + 10 * scale, y + 6 * scale, fill="#4cc9f0", outline="")
            canvas.create_line(x, y + 6 * scale, x, y + 24 * scale, fill="#7bdff6", width=2)
            canvas.create_line(x - 4, y + 18 * scale, x + 4, y + 18 * scale, fill="#ffffff", width=2)

    for piece in confetti:
        piece["y"] += piece["speed"] * 0.8
        piece["x"] += math.sin(frame_time * 0.8 + piece["phase"]) * 0.25
        if piece["y"] > HEIGHT + 20:
            piece["y"] = -20
            piece["x"] = random.randint(0, int(WIDTH))
        ox = (piece["x"] - WIDTH / 2) * camera_zoom + WIDTH / 2 + camera_x
        oy = (piece["y"] - HEIGHT / 2) * camera_zoom + HEIGHT / 2 + camera_y
        canvas.create_text(ox, oy, text=piece["symbol"], fill=piece["color"], font=("Microsoft YaHei", int(piece["size"] * 0.8), "bold"))


def update_fireworks():
    global launch_timer
    launch_timer += 1
    if launch_timer % 16 == 0 and random.random() < 0.55:
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
        canvas.create_oval(rocket["x"] - 5, rocket["y"] - 5, rocket["x"] + 5, rocket["y"] + 5, outline="#ffffff", width=1)

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
        canvas.create_oval(
            particle["x"] - particle["size"] * 0.55,
            particle["y"] - particle["size"] * 0.55,
            particle["x"] + particle["size"] * 0.55,
            particle["y"] + particle["size"] * 0.55,
            outline="#ffffff",
            width=1,
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
    global intro_time, scene_phase, subtitle_index, subtitle_timer, camera_x, camera_y, camera_zoom
    intro_time += 0.016
    progress = min(1.0, intro_time / 2.8)
    ease = 3 * progress * progress - 2 * progress * progress * progress

    if intro_time < 1.2:
        camera_zoom = 1.0 + 0.03 * math.sin(intro_time * 4)
    elif intro_time < 2.4:
        camera_zoom = 1.04 + 0.06 * math.sin(intro_time * 3.2)
        camera_x = math.sin(intro_time * 0.8) * 22
        camera_y = math.cos(intro_time * 0.7) * 12
    else:
        camera_zoom = 1.08 + 0.02 * math.sin(intro_time * 2.2)
        camera_x = math.sin(intro_time * 1.0) * 35
        camera_y = math.cos(intro_time * 0.9) * 20

    subtitle_timer += 0.016
    if subtitle_timer > 2.2:
        subtitle_timer = 0.0
        subtitle_index = (subtitle_index + 1) % len(subtitles)

    y = HEIGHT * 0.68 + math.sin(frame_time * 1.8) * 8
    scale = 1.0 + 0.05 * math.sin(frame_time * 2.6)
    size = int(96 + 20 * scale + 30 * ease)

    halo_r = max(140, int(size * 0.72))
    canvas.create_oval(
        WIDTH / 2 - halo_r * 1.16,
        y - halo_r * 1.10,
        WIDTH / 2 + halo_r * 1.16,
        y + halo_r * 1.10,
        outline="#ffe6f2",
        width=2,
    )
    canvas.create_oval(
        WIDTH / 2 - halo_r * 1.02,
        y - halo_r * 0.98,
        WIDTH / 2 + halo_r * 1.02,
        y + halo_r * 0.98,
        outline="#fff7b2",
        width=1,
    )

    canvas.create_text(WIDTH / 2 + 3, y + 5, text="天天开心", fill="#120d20", font=("Microsoft YaHei", size, "bold"))
    canvas.create_text(WIDTH / 2, y, text="天天开心", fill="#fff7b2", font=("Microsoft YaHei", size, "bold"))

    sub_y = y + 108
    canvas.create_text(WIDTH / 2, sub_y, text="愿你笑容如花，心情如春", fill="#ffe6f2", font=("Microsoft YaHei", 30, "bold"))
    canvas.create_text(WIDTH / 2, sub_y + 58, text=subtitles[subtitle_index], fill="#9cf6ff", font=("Microsoft YaHei", 24, "bold"))



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
        create_auroras(WIDTH, HEIGHT)
        create_confetti(WIDTH, HEIGHT)
    draw_background(frame_time)
    update_fireworks()
    draw_title(frame_time)
    root.after(16, animate)


def on_click(event):
    spawn_click_burst(event.x, event.y, "burst")
    try:
        import winsound
        winsound.Beep(1700, 60)
    except Exception:
        pass


def play_special_effect(kind):
    try:
        import winsound
        if kind == "cloud":
            winsound.Beep(1800, 45)
            winsound.Beep(2400, 25)
        else:
            winsound.Beep(1700, 60)
    except Exception:
        pass


def on_canvas_click(event):
    x, y = event.x, event.y
    if 0 <= x <= WIDTH and 0 <= y <= HEIGHT:
        spawn_click_burst(x, y, "burst")
        if abs(x - WIDTH * 0.18) < 180 and abs(y - HEIGHT * 0.22) < 140:
            spawn_click_burst(x, y, "title")
        if abs(y - (HEIGHT * 0.72 + math.sin(time.time() * 1.8) * 10)) < 70:
            spawn_click_burst(x, y, "title")

    if abs(x - WIDTH * 0.82) < 120 and abs(y - HEIGHT * 0.16) < 120:
        spawn_click_burst(x, y, "star")
    if abs(x - WIDTH * 0.18) < 160 and abs(y - HEIGHT * 0.24) < 140:
        spawn_click_burst(x, y, "star")

    for prop in interactive_props:
        if "draw_x" in prop and "draw_y" in prop:
            dx = x - prop["draw_x"]
            dy = y - prop["draw_y"]
            if abs(dx) < 24 and abs(dy) < 24:
                spawn_click_burst(x, y, "star")
                prop["phase"] += 0.8
                prop["bounce"] += 0.6
                play_special_effect("cloud")
                break

    for cloud in clouds:
        cx = (cloud["x"] - WIDTH / 2) * camera_zoom + WIDTH / 2 + camera_x
        cy = (cloud["y"] - HEIGHT / 2) * camera_zoom + HEIGHT / 2 + camera_y
        cloud_w = 110 * cloud["size"]
        cloud_h = 60 * cloud["size"]
        if abs(x - (cx + cloud_w * 0.5)) < cloud_w * 0.42 and abs(y - (cy + cloud_h * 0.35)) < cloud_h * 0.33:
            spawn_click_burst(x, y, "cloud")
            cloud["x"] = random.randint(0, int(WIDTH))
            cloud["y"] = random.randint(50, int(HEIGHT * 0.3))
            cloud["bounce_timer"] = 0.22
            cloud["bounce"] = 0.0
            cloud["bounce_dir"] = 1.0
            play_special_effect("cloud")
            break

    try:
        import winsound
        winsound.Beep(1800, 50)
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
    root.bind("<Button-1>", on_canvas_click)
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
    create_auroras(WIDTH, HEIGHT)
    create_confetti(WIDTH, HEIGHT)
    create_interactive_props(WIDTH, HEIGHT)
    play_music_file()
    animate()
    root.mainloop()


def main():
    build_app()


if __name__ == "__main__":
    main()
