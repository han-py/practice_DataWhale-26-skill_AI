# -*- coding: utf-8 -*-
import math
import random
import sys
import time
import tkinter as tk

sys.stdout.reconfigure(encoding="utf-8")

WIDTH = 1100
HEIGHT = 720
COLORS = ["#ff6b6b", "#ffd166", "#06d6a0", "#4cc9f0", "#ff9f1c", "#f72585"]

root = tk.Tk()
root.title("天天开心")
root.attributes("-topmost", True)
root.configure(bg="#060816")
root.bind("<Escape>", lambda _: root.destroy())
root.geometry(f"{WIDTH}x{HEIGHT}+0+0")
root.resizable(False, False)

canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="#060816", highlightthickness=0)
canvas.pack(fill="both", expand=True)

stars = []
for _ in range(140):
    stars.append((random.randint(0, WIDTH), random.randint(0, HEIGHT), random.uniform(0.5, 2.2), random.uniform(0.6, 1.4)))

rockets = []
particles = []
launch_timer = 0


def draw_background(frame_time):
    for y in range(HEIGHT):
        ratio = y / max(1, HEIGHT)
        r = int(6 + 24 * ratio)
        g = int(10 + 12 * ratio)
        b = int(30 + 35 * ratio)
        color = f"#{r:02x}{g:02x}{b:02x}"
        canvas.create_line(0, y, WIDTH, y, fill=color, width=1)

    for x, y, size, alpha in stars:
        glow = 255 - int(alpha * 65)
        color = f"#{glow:02x}{glow:02x}{glow:02x}"
        canvas.create_oval(x, y, x + size, y + size, fill=color, outline="")

    moon_x = WIDTH * 0.82
    moon_y = HEIGHT * 0.18
    canvas.create_oval(moon_x - 70, moon_y - 70, moon_x + 70, moon_y + 70, fill="#f3d7a1", outline="")
    canvas.create_oval(moon_x - 48, moon_y - 48, moon_x + 48, moon_y + 48, fill="#060816", outline="")

    shimmer = (math.sin(frame_time * 1.5) + 1) / 2
    glow_x = WIDTH * 0.2 + math.sin(frame_time * 0.7) * 130
    glow_y = HEIGHT * 0.3 + math.cos(frame_time * 0.6) * 110
    glow_size = 220 + shimmer * 40
    canvas.create_oval(glow_x - glow_size, glow_y - glow_size, glow_x + glow_size, glow_y + glow_size, fill="#ffffff", outline="")


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
    for _ in range(90):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(1.6, 5.8)
        particles.append({
            "x": rocket["tx"],
            "y": rocket["ty"],
            "vx": math.cos(angle) * speed,
            "vy": math.sin(angle) * speed,
            "life": random.randint(45, 90),
            "size": random.uniform(1.8, 4.2),
            "color": rocket["color"],
        })


def update_fireworks(frame_time):
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
    scale = 1.0 + 0.03 * math.sin(frame_time * 3.5)
    size = int(58 + scale * 8)

    shadow_y = y + 4
    canvas.create_text(WIDTH / 2 + 2, shadow_y + 2, text="天天开心", fill="#120d24", font=("Microsoft YaHei", size, "bold"))
    canvas.create_text(WIDTH / 2, y, text="天天开心", fill="#fff3b0", font=("Microsoft YaHei", size, "bold"))

    sub_y = y + 70
    canvas.create_text(WIDTH / 2, sub_y, text="愿你笑容如花，心情如春", fill="#ffd7eb", font=("Microsoft YaHei", 22, "bold"))


def animate():
    canvas.delete("all")
    frame_time = time.time()
    draw_background(frame_time)
    update_fireworks(frame_time)
    draw_text(frame_time)
    root.after(16, animate)


animate()
root.mainloop()

