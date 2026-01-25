import os
import numpy as np
from PIL import Image, ImageDraw
import random

# =======================
# GLOBAL CONFIG
# =======================
IMG_SIZE = 512
CENTER = IMG_SIZE // 2
SCALE = 200
POINTS = 1200
DATASET_PATH = "orbit_dataset"

# =======================
# GRID DRAWING
# =======================
def draw_grid(draw, step=32):
    for x in range(0, IMG_SIZE, step):
        draw.line((x, 0, x, IMG_SIZE), fill=(200,200,200), width=1)
    for y in range(0, IMG_SIZE, step):
        draw.line((0, y, IMG_SIZE, y), fill=(200,200,200), width=1)

# =======================
# BASE ORBITS
# =======================
def orbit_ellipse():
    t = np.linspace(0, 2*np.pi, POINTS)
    return np.cos(t), 0.7*np.sin(t)

def orbit_circle():
    t = np.linspace(0, 2*np.pi, POINTS)
    return np.cos(t), np.sin(t)

def orbit_inner8():
    t = np.linspace(0, 2*np.pi, POINTS)
    return np.sin(2*t), np.sin(t)

def orbit_outer8():
    t = np.linspace(0, 2*np.pi, POINTS)
    return np.sin(t), np.sin(2*t)

def orbit_petal():
    t = np.linspace(0, 2*np.pi, POINTS)
    petals = random.randint(3, 6)       # must be 3 or more
    r = 1 + 0.3*np.cos(petals * t)
    x = r * np.cos(t)
    y = r * np.sin(t)
    return x, y

def orbit_banana():
    t = np.linspace(0, 2*np.pi, POINTS)
    x = np.cos(t)
    y = np.sin(t)
    y[y > 0.2] = 0.2   # flattening
    return x, y

def orbit_spikes():
    t = np.linspace(0, 2*np.pi, POINTS)
    x = np.cos(t)
    y = np.sin(t)
    for _ in range(random.randint(2, 5)):
        idx = random.randint(20, len(x)-20)
        factor = random.uniform(1.6, 2.6)
        x[idx] *= factor
        y[idx] *= factor
    return x, y

# ============================
# CLASS 5A (MULTI DOTS ONLY)
# ============================
def orbit_5A():
    t = np.linspace(0, 2*np.pi, POINTS)
    x = np.cos(t)
    y = 0.7*np.sin(t)

    dots = []
    for _ in range(random.randint(2,4)):
        ang = random.uniform(0, 2*np.pi)
        dx = np.cos(ang)
        dy = 0.7*np.sin(ang)
        dots.append((dx, dy))

    return x, y, dots

# ============================
# CLASS 5B (MULTI DOTS + LOOP)
# ============================
def orbit_5B():
    t = np.linspace(0, 2*np.pi, POINTS)

    x = np.cos(t)
    y = 0.7*np.sin(t)

    t2 = np.linspace(0, 2*np.pi, POINTS)
    x2 = 0.4*np.cos(3*t2)
    y2 = 0.4*np.sin(2*t2)

    X = np.concatenate([x, x2])
    Y = np.concatenate([y, y2])

    dots = []
    for _ in range(random.randint(2,4)):
        ang = random.uniform(0, 2*np.pi)
        dx = np.cos(ang)
        dy = 0.7*np.sin(ang)
        dots.append((dx, dy))

    return X, Y, dots

# =======================
# CLEAN VERSION (same as original)
# =======================
def clean_noise(x, y):
    x += np.random.normal(0, 0.003, len(x))
    y += np.random.normal(0, 0.003, len(y))
    return x, y

def draw_clean(x, y, filename):
    img = Image.new("RGB", (IMG_SIZE, IMG_SIZE), "white")
    d = ImageDraw.Draw(img)

    pts = []
    for i in range(len(x)):
        px = int(CENTER + x[i] * SCALE)
        py = int(CENTER - y[i] * SCALE)
        pts.append((px, py))

    d.line(pts, fill=(0,0,200), width=1)
    img.save(filename)

# =======================
# REALISTIC (noisy) VERSION
# =======================
def realistic_noise(x, y):
    x += np.cumsum(np.random.normal(0, 0.010, len(x)))
    y += np.cumsum(np.random.normal(0, 0.010, len(y)))

    x += np.random.normal(0, 0.015, len(x))
    y += np.random.normal(0, 0.015, len(y))

    for _ in range(random.randint(2,5)):
        idx = random.randint(20, len(x)-20)
        factor = random.uniform(1.4,2.4)
        x[idx] *= factor
        y[idx] *= factor

    return x, y

def draw_realistic(x, y, filename, dots=None):

    img = Image.new("RGB", (IMG_SIZE, IMG_SIZE), "white")
    d = ImageDraw.Draw(img)

    draw_grid(d)

    pts=[]
    for i in range(len(x)):
        px=int(CENTER + x[i]*SCALE)
        py=int(CENTER - y[i]*SCALE)
        pts.append((px,py))

    d.line(pts, fill=(0,0,200), width=2)

    if dots:
        for (dx,dy) in dots:
            px=int(CENTER + dx*SCALE)
            py=int(CENTER - dy*SCALE)
            d.ellipse((px-6,py-6,px+6,py+6), fill="black")

    kp = random.randint(50,len(pts)-50)
    d.ellipse((pts[kp][0]-6, pts[kp][1]-6,
               pts[kp][0]+6, pts[kp][1]+6),
              fill="red")

    img.save(filename)

# =======================
# CLASS MAPPING
# =======================
CLASS_MAP = {
    "class1": lambda: orbit_ellipse(),
    "class2": lambda: orbit_ellipse(),
    "class3": lambda: orbit_circle(),
    "class4": lambda: orbit_spikes(),
    "class5A": lambda: orbit_5A(),
    "class5B": lambda: orbit_5B(),
    "class6": lambda: orbit_banana(),
    "class7": lambda: orbit_inner8(),
    "class8": lambda: orbit_outer8(),
    "class9": lambda: orbit_petal(),
}

# =======================
# GENERATE ALL
# =======================
def generate_all():

    for mode in ["clean", "realistic"]:
        for cname, func in CLASS_MAP.items():

            folder = f"{DATASET_PATH}/{mode}/{cname}"
            os.makedirs(folder, exist_ok=True)

            for i in range(100):

                out_file = f"{folder}/{cname}_{i}.png"

                result = func()

                if cname in ["class5A", "class5B"]:
                    x, y, dots = result
                else:
                    x, y = result
                    dots = None

                if mode == "clean":
                    x, y = clean_noise(x, y)
                    draw_clean(x, y, out_file)

                else:
                    x, y = realistic_noise(x, y)
                    draw_realistic(x, y, out_file, dots)

            print("Generated:", mode, cname)

    print("\n🎉 ALL DONE — DATASET READY!")

generate_all()
