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
COLORS = ["#ff6b6b", "#ffd166", "#06d6a0", "#4cc9f0", "#ff9f1c", "#f72585"]
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
    for _ in range(180):
        stars.append((
            random.randint(0, width),
            random.randint(0, height),
            random.uniform(0.6, 2.4),
            random.uniform(0.6, 1.4),
        ))


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
    for _ in range(95):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(1.8, 6.4)
        particles.append({
            "x": rocket["tx"],
            "y": rocket["ty"],
            "vx": math.cos(angle) * speed,
            "vy": math.sin(angle) * speed,
            "life": random.randint(42, 90),
            "size": random.uniform(2.0, 4.6),
            "color": rocket["color"],
        })


def spawn_click_burst(x, y):
    for _ in range(36):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(2.2, 6.8)
        particles.append({
            "x": x,
            "y": y,
            "vx": math.cos(angle) * speed,
            "vy": math.sin(angle) * speed,
            "life": random.randint(28, 60),
            "size": random.uniform(2.0, 5.0),
            "color": random.choice(COLORS),
        })


def draw_background(frame_time):
    for y in range(HEIGHT):
        ratio = y / max(1, HEIGHT)
        r = int(6 + 24 * ratio)
        g = int(10 + 14 * ratio)
        b = int(32 + 35 * ratio)
        color = f"#{r:02x}{g:02x}{b:02x}"
        canvas.create_line(0, y, WIDTH, y, fill=color, width=1)

    for x, y, size, alpha in stars:
        glow = 255 - int(alpha * 65)
        color = f"#{glow:02x}{glow:02x}{glow:02x}"
        canvas.create_oval(x, y, x + size, y + size, fill=color, outline="")

    moon_x = WIDTH * 0.82
    moon_y = HEIGHT * 0.16
    canvas.create_oval(moon_x - 70, moon_y - 70, moon_x + 70, moon_y + 70, fill="#f6dca3", outline="")
    canvas.create_oval(moon_x - 48, moon_y - 48, moon_x + 48, moon_y + 48, fill="#060816", outline="")

    shimmer = (math.sin(frame_time * 1.4) + 1) / 2
    glow_x = WIDTH * 0.2 + math.sin(frame_time * 0.7) * 140
    glow_y = HEIGHT * 0.3 + math.cos(frame_time * 0.6) * 110
    glow_size = 220 + shimmer * 40
    canvas.create_oval(glow_x - glow_size, glow_y - glow_size, glow_x + glow_size, glow_y + glow_size, fill="#ffffff", outline="")


def update_fireworks():
    global launch_timer
    launch_timer += 1
    if launch_timer % 18 == 0:
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
    size = int(62 + 8 * math.sin(frame_time * 3.5))
    canvas.create_text(WIDTH / 2 + 2, y + 4, text="天天开心", fill="#120d24", font=("Microsoft YaHei", size, "bold"))
    canvas.create_text(WIDTH / 2, y, text="天天开心", fill="#fff3b0", font=("Microsoft YaHei", size, "bold"))
    canvas.create_text(WIDTH / 2, y + 76, text="愿你笑容如花，心情如春", fill="#ffd7eb", font=("Microsoft YaHei", 24, "bold"))


def animate():
    global WIDTH, HEIGHT
    canvas.delete("all")
    frame_time = time.time()
    if WIDTH == 0 or HEIGHT == 0:
        WIDTH = root.winfo_screenwidth()
        HEIGHT = root.winfo_screenheight()
        canvas.configure(width=WIDTH, height=HEIGHT)
        create_stars(WIDTH, HEIGHT)
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
    start_music()
    animate()
    root.mainloop()


def main():
    build_app()


if __name__ == "__main__":
    main()
