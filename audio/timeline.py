# Picture timeline mirrored from src/videos/wobbly/story.ts for the train short so every sound lands on
# the frame: shots, story time tau per shot, train position, whistle cues, clock chimes, station sounds,
# camera distance per shot, and the camera's ease-out whooshes.
import math
import numpy as np

FPS = 30
TOTAL = 1800
DUR = TOTAL / FPS            # 60.0 s exactly
fr = lambda f: f / FPS

FLASH = fr(130)              # white 4-frame flash after the hook (frame 130)

# id: (first frame, end frame, light, crowd)
SHOTS = {
    1: (0, 130, "day", "march"),      # hook: impossible train
    2: (130, 300, "day", "march"),    # town aerial + clocks
    3: (300, 460, "day", "march"),    # timetables CU
    4: (460, 640, "day", "march"),    # train leaves Cleveland
    5: (640, 820, "day", "march"),    # arrives Pittsburgh before it left
    6: (820, 980, "day", "march"),    # confused passengers, three watches
    7: (980, 1120, "day", "march"),   # mystery: wait, how?
    8: (1120, 1280, "golden", "none"), # pivot: sun time moves west
    9: (1280, 1440, "golden", "march"), # analogy: on the train
    10: (1440, 1620, "day", "bank"),   # consequence: four time zones
    11: (1620, TOTAL, "day", "tourists"), # callback: leaves after it arrives
}
XFADE = {8: 8, 9: 8, 10: 8, 11: 8}


def shot_t(i):
    a, b = SHOTS[i][:2]
    return fr(a), fr(b)


def shot_at(t):
    f = t * FPS
    for i, (a, b, *_r) in SHOTS.items():
        if a <= f < b:
            return i
    return 11


def tau_of(shot, t):
    return t


def hh(i, s=0):
    """same hash as cast.ts (IEEE doubles, so it reproduces the JS values)"""
    v = math.sin(i * 127.1 + s * 311.7) * 43758.5453
    return v - math.floor(v)


def easeout(u):
    u = min(1.0, max(0.0, u))
    return 1 - (1 - u) ** 4


# ---- train physics (from story.ts) ----
# trainZ(tau) = -54 + 1.6 * tau  (front of train moving +z through stations)
def trainZ(tau):
    return -54 + 1.6 * tau


# clock offset per town (solar noon drift). Towns at z = -30 (Pittsburgh) and z = +30 (Cleveland)
# Cleveland noon is ~11 min behind Pittsburgh noon; a train going east loses time.
CLEVELAND_OFFSET = -11 * 60   # seconds behind Pittsburgh solar noon
PITTSBURGH_OFFSET = 0


# ---- camera -> train distance per shot (m), from story.ts camera keys ----
TRAIN_CAM = {
    1: [(0, 0, 15.0), (48, 9, 6.5), (88, 9, 4.2)],
    2: [(126, 0, 85.0), (190, 10, 70.0), (246, 10, 55.0)],
    3: [(280, 0, 50.0), (283, 14, 6.3), (353, 10, 3.4)],
    4: [(440, 0, 3.4), (444, 13, 11.5), (497, 10, 7.8)],
    5: [(530, 0, 7.8), (534, 13, 4.9), (585, 10, 3.8)],
    6: [(640, 0, 3.8), (643, 11, 3.2), (717, 12, 11.8), (768, 10, 6.9)],
    7: [(820, 0, 7.0), (823, 12, 11.3), (871, 11, 7.3), (925, 11, 4.0)],
    8: [(1067, 0, 80.0), (1200, 10, 65.0)],
    9: [(1227, 0, 9.0), (1298, 10, 6.8)],
    10: [(1387, 0, 4.0), (1428, 10, 5.7)],
    11: [(1557, 0, 8.0), (1590, 30, 5.0), (1672, 93, 80.0)],
}


def train_distance(t):
    """distance from camera to train at time t (s), interpolated from per-shot keys."""
    s = shot_at(t)
    keys = TRAIN_CAM.get(s)
    if not keys:
        return 60.0
    f = t * FPS
    ld = math.log(keys[0][2])
    for kf, dur, d in keys[1:]:
        if f < kf:
            break
        ld = ld + (math.log(d) - ld) * easeout((f - kf) / max(dur, 1))
    return math.exp(ld)


def dist_fx(d):
    """distance -> (gain dB, low-pass Hz, reverb send) for train/station sounds."""
    d = max(d, 3.5)
    g = -14.0 * math.log10(d / 3.5)
    lpf = float(np.clip(17000 * (3.5 / d) ** 0.55, 1800, 17000))
    send = 0.06 + 0.45 * float(np.clip(math.log(d / 3.5) / math.log(25), 0, 1))
    return g, lpf, send


def words(path):
    import json
    return json.load(open(path, encoding="utf-8"))
