# -*- coding: utf-8 -*-
import math
import random
import threading
import time
import tkinter as tk

try:
    import winsound
except ImportError:  # pragma: no cover
    winsound = None

WIDTH = 0
HEIGHT = 0
COLORS = ["#ff6b6b", "#ffd166", "#06d6a0", "#4cc9f0", "#ff9f1c", "#f72585", "#ff7ad9", "#9b5de5"]
MELODY = [
    (523, 180),
    (659, 180),
    (784, 220),
    (659, 180),
    (587, 180),
    (523, 220),
    (392, 260),
]

music_thread = None
stop_music_event = threading.Event()
root = None
canvas = None
stars = []
clouds = []
hearts = []
sparkles = []
rockets = []
particles = []
launch_timer = 0


def play_note(freq, duration_ms):
    if winsound is not None:
        winsound.Beep(freq, duration_ms)


def music_loop():
    while not stop_music_event.is_set():
        for freq, duration in MELODY:
            if stop_music_event.is_set():
                return
            play_note(freq, duration)
            if stop_music_event.is_set():
                return
            time.sleep(0.05)


def start_music():
    global music_thread, stop_music_event
    if winsound is None:
        return
    if music_thread is not None and music_thread.is_alive():
        return
    stop_music_event = threading.Event()
    music_thread = threading.Thread(target=music_loop, daemon=True)
    music_thread.start()


def stop_music():
    global music_thread
    if music_thread is not None:
        stop_music_event.set()
        music_thread.join(timeout=0.6)
        music_thread = None


def create_stars(width, height):
    stars.clear()
    max_y = int(height * 0.8)
    for _ in range(220):
        stars.append((
            random.randint(0, int(width)),
            random.randint(0, max_y),
            random.uniform(0.7, 2.8),
            random.uniform(0.5, 1.3),
            random.uniform(0.0, 6.28),
        ))


def create_clouds(width, height):
    clouds.clear()
    for _ in range(8):
        clouds.append({
            "x": random.randint(0, width),
            "y": random.randint(60, height // 3),
            "size": random.uniform(0.9, 1.5),
            "speed": random.uniform(0.3, 0.8),
            "alpha": random.uniform(0.2, 0.5),
        })


def create_hearts(width, height):
    hearts.clear()
    for _ in range(12):
        hearts.append({
            "x": random.randint(0, int(width)),
            "y": random.randint(int(height * 0.6), int(height)),
            "size": random.uniform(0.8, 1.6),
            "speed": random.uniform(0.7, 1.6),
            "phase": random.uniform(0, 6.28),
        })


def create_sparkles(width, height):
    sparkles.clear()
    for _ in range(90):
        sparkles.append({
            "x": random.randint(0, width),
            "y": random.randint(0, height),
            "size": random.uniform(1.0, 2.6),
            "phase": random.uniform(0, 6.28),
            "speed": random.uniform(0.6, 1.4),
        })


def spawn_rocket():
    rockets.append({
        "x": random.randint(80, WIDTH - 80),
        "y": HEIGHT + 20,
        "tx": random.randint(80, WIDTH - 80),
        "ty": random.randint(80, HEIGHT // 2),
        "color": random.choice(COLORS),
        "speed": random.uniform(8, 14),
        "trail": [],
    })


def explode(rocket):
    for _ in range(105):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(1.8, 6.8)
        particles.append({
            "x": rocket["tx"],
            "y": rocket["ty"],
            "vx": math.cos(angle) * speed,
            "vy": math.sin(angle) * speed,
            "life": random.randint(36, 90),
            "size": random.uniform(1.8, 4.8),
            "color": rocket["color"],
        })


def spawn_click_burst(x, y):
    for _ in range(45):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(2.4, 7.2)
        particles.append({
            "x": x,
            "y": y,
            "vx": math.cos(angle) * speed,
            "vy": math.sin(angle) * speed,
            "life": random.randint(30, 70),
            "size": random.uniform(2.0, 5.4),
            "color": random.choice(COLORS),
        })


def draw_background(frame_time):
    step = 16
    for y in range(0, HEIGHT, step):
        ratio = y / max(1, HEIGHT)
        r = int(8 + 30 * ratio)
        g = int(12 + 26 * ratio)
        b = int(38 + 45 * ratio)
        color = f"#{r:02x}{g:02x}{b:02x}"
        canvas.create_rectangle(0, y, WIDTH, y + step, fill=color, outline="")

    center_glow = (math.sin(frame_time * 0.7) + 1) / 2
    canvas.create_oval(WIDTH * 0.18 - 220, HEIGHT * 0.16 - 220, WIDTH * 0.18 + 220, HEIGHT * 0.16 + 220, fill="#ffffff", outline="")
    canvas.create_oval(WIDTH * 0.82 - 140, HEIGHT * 0.16 - 140, WIDTH * 0.82 + 140, HEIGHT * 0.16 + 140, fill="#f8dd8f", outline="")
    canvas.create_oval(WIDTH * 0.82 - 90, HEIGHT * 0.16 - 90, WIDTH * 0.82 + 90, HEIGHT * 0.16 + 90, fill="#060816", outline="")
    canvas.create_oval(WIDTH * 0.13 - 210 - center_glow * 30, HEIGHT * 0.24 - 180, WIDTH * 0.13 + 210 + center_glow * 30, HEIGHT * 0.24 + 180, fill="#72f4ff", outline="")

    for x, y, size, alpha, phase in stars:
        twinkle = 0.65 + 0.35 * math.sin(frame_time * 1.5 + phase)
        glow = int(200 + twinkle * 55)
        color = f"#{glow:02x}{glow:02x}{glow:02x}"
        canvas.create_oval(x, y, x + size, y + size, fill=color, outline="")

    for cloud in clouds:
        cloud["x"] += cloud["speed"] * 0.02
        if cloud["x"] > WIDTH + 120:
            cloud["x"] = -180
            cloud["y"] = random.randint(50, HEIGHT // 3)
        cx = cloud["x"]
        cy = cloud["y"]
        scale = cloud["size"]
        canvas.create_oval(cx, cy, cx + 80 * scale, cy + 50 * scale, fill="#ffffff", outline="", stipple="gray50")
        canvas.create_oval(cx + 30 * scale, cy - 10 * scale, cx + 105 * scale, cy + 40 * scale, fill="#ffffff", outline="", stipple="gray50")
        canvas.create_oval(cx + 55 * scale, cy + 5 * scale, cx + 125 * scale, cy + 55 * scale, fill="#ffffff", outline="", stipple="gray50")

    for sparkle in sparkles:
        sparkle["y"] += 0.06 * sparkle["speed"]
        sparkle["x"] += 0.02 * math.sin(frame_time * 0.7 + sparkle["phase"])
        if sparkle["y"] > HEIGHT:
            sparkle["y"] = -10
        pulse = 0.7 + 0.3 * math.sin(frame_time * 2.0 + sparkle["phase"])
        size = sparkle["size"] * pulse
        canvas.create_line(
            sparkle["x"], sparkle["y"], sparkle["x"] + size * 2, sparkle["y"],
            fill="#fff7b2", width=2
        )
        canvas.create_line(
            sparkle["x"], sparkle["y"], sparkle["x"], sparkle["y"] + size * 2,
            fill="#fff7b2", width=2
        )

    for i in range(4):
        y1 = HEIGHT * 0.72 + i * 40 + math.sin(frame_time * 0.6 + i) * 20
        y2 = HEIGHT * 0.84 + i * 18 + math.cos(frame_time * 0.5 + i) * 20
        canvas.create_polygon(
            0, HEIGHT,
            WIDTH * 0.1 + i * 110, y1,
            WIDTH * 0.3 + i * 100, HEIGHT * 0.77,
            WIDTH * 0.5 + i * 80, y2,
            WIDTH, HEIGHT,
            fill="#0b1d2e", outline=""
        )

    for i in range(3):
        x = WIDTH * (0.2 + i * 0.25)
        y = HEIGHT * (0.65 + i * 0.02)
        canvas.create_line(x - 140, y + 80, x, y, fill="#6fffe9", width=8)
        canvas.create_line(x, y, x + 140, y + 80, fill="#6fffe9", width=8)
        canvas.create_line(x - 120, y + 90, x + 120, y + 100, fill="#4cc9f0", width=5)


def update_fireworks():
    global launch_timer
    launch_timer += 1
    if launch_timer % 15 == 0:
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
        particle["vy"] += 0.019
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


def draw_text(frame_time):
    y = HEIGHT * 0.74 + math.sin(frame_time * 2.0) * 12
    size = int(70 + 10 * math.sin(frame_time * 3.2))

    canvas.create_text(WIDTH / 2 + 2, y + 4, text="天天开心", fill="#130d20", font=("Microsoft YaHei", size, "bold"))
    canvas.create_text(WIDTH / 2 + 4, y + 2, text="天天开心", fill="#ffef8e", font=("Microsoft YaHei", size, "bold"))
    canvas.create_text(WIDTH / 2, y, text="天天开心", fill="#ffffff", font=("Microsoft YaHei", size, "bold"))

    canvas.create_text(WIDTH / 2, y + 78, text="愿你笑容如花，心情如春", fill="#ffe6f2", font=("Microsoft YaHei", 24, "bold"))
    canvas.create_text(WIDTH / 2, y + 112, text="点击屏幕，点亮更多祝福", fill="#9cf6ff", font=("Microsoft YaHei", 18, "bold"))

    for heart in hearts:
        heart["y"] -= heart["speed"] * 0.35
        heart["x"] += math.sin(frame_time * 0.8 + heart["phase"]) * 0.25
        if heart["y"] < HEIGHT * 0.5:
            heart["y"] = HEIGHT * 0.92
            heart["x"] = random.randint(0, WIDTH)
        size = heart["size"] * 22
        canvas.create_text(heart["x"], heart["y"], text="♡", fill="#ff7ad9", font=("Microsoft YaHei", int(size), "bold"))


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
        create_hearts(WIDTH, HEIGHT)
        create_sparkles(WIDTH, HEIGHT)
    draw_background(frame_time)
    update_fireworks()
    draw_text(frame_time)
    root.after(16, animate)


def on_click(event):
    spawn_click_burst(event.x, event.y)
    play_note(1500, 70)


def on_close():
    stop_music()
    root.destroy()


def build_app():
    global root, canvas
    root = tk.Tk()
    root.title("天天开心")
    root.configure(bg="#060816")
    root.attributes("-topmost", True)
    root.attributes("-fullscreen", True)
    root.bind("<Escape>", lambda _: on_close())
    root.bind("<Button-1>", on_click)
    root.protocol("WM_DELETE_WINDOW", on_close)

    canvas = tk.Canvas(root, bg="#060816", highlightthickness=0)
    canvas.pack(fill="both", expand=True)
    root.update_idletasks()
    global WIDTH, HEIGHT
    WIDTH = root.winfo_screenwidth()
    HEIGHT = root.winfo_screenheight()
    canvas.configure(width=WIDTH, height=HEIGHT)
    create_stars(WIDTH, HEIGHT)
    create_clouds(WIDTH, HEIGHT)
    create_hearts(WIDTH, HEIGHT)
    create_sparkles(WIDTH, HEIGHT)
    start_music()
    animate()
    root.mainloop()


def main():
    build_app()


if __name__ == "__main__":
    main()
