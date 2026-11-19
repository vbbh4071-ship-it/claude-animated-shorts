# Original light march-style score for the train short (Bb major, 120 bpm:
# one quarter note = one train wheel click / footfall step).
# Sections follow the picture: hook whistle | town march | confusion stumble |
# pivot slow-down | analogy sway | consequence march | callback lazy ending.
import numpy as np
from dsp import SR, ns, rng, pan, place, fades, dbg, make_ir, convolve_st, integrated, lp, hp
import instruments as I
import timeline as T

N = ns(T.DUR)
Q = 0.5  # quarter note (s)

# theme A: (bar, beat, length in quarters, midi) - fife / whistle register
THEME = [
    (1, 0, 1, 82), (1, 1, .75, 82), (1, 1.75, .25, 84), (1, 2, 1, 86), (1, 3, 1, 82),
    (2, 0, 1, 77), (2, 1, .5, 79), (2, 1.5, .5, 81), (2, 2, 1, 82), (2, 3.5, .5, 77),
    (3, 0, .75, 79), (3, .75, .25, 81), (3, 1, .5, 82), (3, 1.5, .5, 79), (3, 2, 1, 87), (3, 3, .5, 86), (3, 3.5, .5, 84),
    (4, 0, 2, 84),
    (5, 0, 1, 82), (5, 1, .75, 82), (5, 1.75, .25, 84), (5, 2, 1, 86), (5, 3, 1, 89),
    (6, 0, .5, 87), (6, .5, .5, 86), (6, 1, .5, 84), (6, 1.5, .5, 82), (6, 2, 1, 81), (6, 3, .5, 82), (6, 3.5, .5, 84),
    (7, 0, .75, 86), (7, .75, .25, 84), (7, 1, .5, 82), (7, 1.5, .5, 81), (7, 2, 1, 79), (7, 3, 1, 84),
    (8, 0, 1, 82), (8, 1, .5, 77), (8, 1.5, .5, 74), (8, 2, 1, 70),
]
PICKUP3 = [(0, 2.5, .5, 74), (0, 3, .5, 75), (0, 3.5, .5, 77)]
CHB = {1: ["Bb"] * 4, 2: ["F", "F", "Bb", "Bb"], 3: ["Cm", "Cm", "Eb", "Eb"], 4: ["F7"] * 4, 5: ["Bb"] * 4,
       6: ["Eb", "Eb", "F", "F"], 7: ["Gm", "Gm", "Cm", "F7"], 8: ["Bb"] * 4}
CH = {
    "Bb": dict(oom=(34, 41), pah=[53, 58, 62], hi=[58, 62, 65]),
    "F": dict(oom=(41, 36), pah=[53, 57, 60], hi=[57, 60, 65]),
    "F7": dict(oom=(41, 36), pah=[51, 57, 60], hi=[57, 60, 63]),
    "Cm": dict(oom=(36, 43), pah=[55, 60, 63], hi=[60, 63, 67]),
    "Eb": dict(oom=(39, 46), pah=[55, 58, 63], hi=[58, 63, 67]),
    "Gm": dict(oom=(43, 38), pah=[55, 58, 62], hi=[58, 62, 67]),
    "F#o7": dict(oom=(42, 42), pah=[54, 57, 60, 63], hi=[57, 60, 63]),
    "G#o7": dict(oom=(44, 44), pah=[56, 59, 62, 65], hi=[59, 62, 65]),
}
F = I.m2f

# where each section of the music sits (used for the cue sheet and the level automation)
SECTIONS = [
    ("hook", 0.0, T.FLASH),            # 0 - 4.33: whistle fanfare
    ("town", T.FLASH, 10.0),           # 4.33 - 10: town march
    ("march", 10.0, 16.0),             # 10 - 16: full band march
    ("confusion", 16.0, 24.0),         # 16 - 24: stumbling rhythm
    ("pivot", 24.0, 32.0),             # 24 - 32: slow, explanatory
    ("analogy", 32.0, 40.0),           # 32 - 40: warm sway
    ("consequence", 40.0, 52.0),       # 40 - 52: steady march
    ("callback", 52.0, T.DUR),         # 52 - 60: relaxed ending
]


def swingb(b):
    fl = np.floor(b)
    fr_ = b - fl
    return fl + (2 / 3 if fr_ in (0.5, 0.75) else (1 / 3 if fr_ == 0.25 else fr_))


def theme(t_bar1, bars=range(1, 9), transpose=0, pickup=False, swing=False, late=0.0):
    ev = []
    for (b, beat, d, m) in THEME + (PICKUP3 if pickup else []):
        if b == 0 and not pickup:
            continue
        if b != 0 and b not in bars:
            continue
        bb = swingb(beat) if swing else beat
        ev.append((t_bar1 + (b - 1) * 4 * Q + bb * Q + late, d * Q, m + transpose))
    return sorted(ev)


class Band:
    def __init__(self):
        self.tr = {}
        self.send = {}
        self.cues = []

    def track(self, name, send):
        if name not in self.tr:
            self.tr[name] = np.zeros((2, N))
            self.send[name] = send
        return self.tr[name]

    def add(self, name, x, t, p=0.0, g=1.0, send=0.15):
        buf = self.track(name, send)
        place(buf, pan(x, p) if np.ndim(x) == 1 else x, t, g)


R = rng(1831)


def _r():
    return rng(int(R.integers(1 << 30)))


def oompah(b, t_bar, chords, vel=0.6, every=True, pah_vel=0.4, bounce=False, pah=True):
    """tuba on the beats (root/fifth alternating) + after-beat horns on the &s; bounce = octave eighths"""
    for beat in range(4):
        c = CH[chords[beat]]
        t = t_bar + beat * Q
        if bounce:
            lo = c["oom"][0] if c["oom"][0] >= 36 else c["oom"][0] + 12
            b.add("tuba", I.brass(F(lo), 0.2, vel, _r(), "tuba", scoop=-30), t, -0.1)
            b.add("tuba", I.brass(F(lo + 12), 0.16, vel * 0.85, _r(), "tuba", scoop=-45), t + Q / 2, -0.1)
        elif every or beat in (0, 2):
            m = c["oom"][beat % 2] if every else c["oom"][0 if beat == 0 else 1]
            b.add("tuba", I.brass(F(m), 0.3, vel * (1.0 if beat in (0, 2) else 0.88), _r(), "tuba"), t, -0.1)
        if pah:
            if every:
                for k, m in enumerate(c["pah"]):
                    b.add("pah", I.brass(F(m), 0.15, pah_vel, _r(), "horn", scoop=-12), t + Q / 2 + 0.004 * k, 0.32 - 0.12 * k)
            elif beat in (1, 3):
                for k, m in enumerate(c["pah"]):
                    b.add("pah", I.brass(F(m), 0.17, pah_vel, _r(), "horn", scoop=-12), t + 0.004 * k, 0.32 - 0.12 * k)


SN = {
    "light": [1, 0, 0, 0, 2, 0, 0, 0, 1, 0, 0, 0, 2, 0, 1, 1],
    "march": [3, 0, 1, 1, 2, 0, 1, 0, 3, 0, 1, 1, 2, 0, 1, 0],
    "drive": [2, 1, 1, 1, 2, 1, 1, 1, 2, 1, 1, 1, 2, 1, 1, 1],
}


def snare_bar(b, t_bar, pat, vel, steps=range(16), cres=0.0):
    for s in steps:
        v = SN[pat][s]
        if not v:
            continue
        t = t_bar + s * Q / 4
        vv = vel * (1 + cres * s / 16) * {1: 0.5, 2: 0.9, 3: 0.95}[v] * R.uniform(0.93, 1.05)
        if v == 3:
            b.add("snare", I.snare(vv * 0.4, _r()), t - 0.026, 0.05)
        b.add("snare", I.snare(vv, _r()), t + R.normal(0, 0.002), 0.05)


def roll(b, t0, t1, v0, v1, accent=None, at=None):
    for t, v in I.snare_roll(t0, t1, v0, v1, _r()):
        b.add("snare", I.snare(v, _r(), dur=0.14, buzz=True), t, 0.05)
    if accent:
        at = t1 if at is None else at
        b.add("snare", I.snare(accent * 0.4, _r()), at - 0.026, 0.05)
        b.add("snare", I.snare(accent, _r()), at, 0.05)


def melody(b, name, notes, vel, transpose=0, fn="glock", p=0.0, gate=0.9):
    for (t, d, m) in notes:
        m = m + transpose
        if fn == "glock":
            x = I.glock(F(m), vel * R.uniform(0.92, 1.05), _r())
        elif fn == "fife":
            x = I.fife(F(m), d * gate, vel * R.uniform(0.94, 1.04), _r())
        elif fn == "vibes":
            x = I.vibes(F(m), vel * R.uniform(0.92, 1.05), _r(), dur=max(1.2, d + 0.8), damp=d + 0.35)
        elif fn == "musicbox":
            x = I.musicbox(F(m), vel * R.uniform(0.92, 1.05), _r())
        elif fn == "pluck":
            x = I.pluck(F(m), vel * R.uniform(0.92, 1.05), _r())
        b.add(name, x, t, p)


def chorus(b, name, notes, voices, seed, joins=None, falters=None, spread=0.75, vel=1.0, solo_gain=1.0):
    """several people whistling the same tune: own detune, timing, vibrato, breath"""
    rr = rng(seed)
    for v in range(voices):
        rv = rng(seed * 101 + v)
        nv = [(t, d, m, vel * rv.uniform(0.85, 1.0)) for (t, d, m) in notes if joins is None or t >= joins[v] - 1e-6]
        if not nv:
            continue
        fal = (falters[v], -rv.uniform(1.2, 3.2)) if falters else None
        t0, y = I.whistle(nv, rv, detune=rv.uniform(-11, 11) if v else 0.0, jit=0.010,
                          lag=rv.uniform(0, 0.022) if v else 0.0,
                          vib_rate=rv.uniform(5.0, 6.6), vib_depth=rv.uniform(10, 22),
                          breath=rv.uniform(0.04, 0.07), falter=fal)
        g = (solo_gain if v == 0 else rv.uniform(0.45, 0.8))
        p = 0.0 if v == 0 else spread * rr.uniform(-1, 1)
        if v:
            y = lp(y, rv.uniform(5000, 9000), 1)
        b.add(name, y, t0, p, g)


def build():
    b = Band()
    for name, send in [("whistle", 0.0), ("fife", 0.16), ("glock", 0.22), ("tuba", 0.10),
                       ("pah", 0.18), ("snare", 0.13), ("cymbal", 0.16), ("stab", 0.16),
                       ("timpani", 0.18), ("pad", 0.25), ("vibes", 0.26), ("musicbox", 0.26),
                       ("pluck", 0.18), ("brush", 0.12), ("triangle", 0.25)]:
        b.track(name, send)

    # ============ HOOK 0 - 4.33: whistle fanfare, single whistler then more join
    h = theme(0.0, bars=[1, 2])
    chorus(b, "whistle", h, 4, 11, solo_gain=1.1)
    melody(b, "glock", h, 0.5, 12, "glock", -0.35)
    for bar in (1, 2):
        tb = (bar - 1) * 2.0
        oompah(b, tb, CHB[bar], 0.6, True, 0.4)
        snare_bar(b, tb, "march", 0.55, steps=range(16) if bar == 1 else range(8))
    roll(b, 3.0, 4.28, 0.25, 0.6)
    b.add("cymbal", I.cymbal(0.4, _r()), 0.0, 0.0)
    b.cues.append((0.0, "hook: whistle fanfare theme A1-A2, tuba/snare/cymbal"))
    hook_cut = np.ones(N)
    a, z = ns(T.FLASH - 0.03), ns(T.FLASH + 0.015)
    hook_cut[a:z] = np.linspace(1, 0, z - a)
    hook_cut[z:] = 0
    for k in b.tr:
        b.tr[k] *= hook_cut[None, :]
    b.cues.append((T.FLASH, "band cut exactly on the white flash (frame 130)"))

    # ============ TOWN MARCH 4.5 - 10: band plays theme A, light and sunny
    s0 = 5.0
    roll(b, s0, s0 + 0.4, 0.15, 0.5, accent=0.5, at=5.0)
    a12 = theme(s0, bars=[1, 2])
    melody(b, "glock", a12, 0.36, 12, "glock", -0.35)
    melody(b, "fife", a12, 0.42, 0, "fife", 0.25)
    for bar in (1, 2):
        tb = s0 + (bar - 1) * 2
        oompah(b, tb, CHB[bar], 0.5, False, 0.34)
        snare_bar(b, tb, "light", 0.36)
    b.cues.append((s0, "town: theme A1-A2 light (glock + fife, tuba on 1/3)"))
    a38 = theme(s0, bars=range(3, 9))
    melody(b, "glock", a38, 0.5, 12, "glock", -0.35)
    melody(b, "fife", a38, 0.58, 0, "fife", 0.25)
    b.add("cymbal", I.cymbal(0.42, _r()), 9.0, 0.0)
    for bar in range(3, 9):
        tb = s0 + (bar - 1) * 2
        oompah(b, tb, CHB[bar], 0.64, True, 0.44)
        snare_bar(b, tb, "march", 0.58, steps=range(16))
    b.cues.append((9.0, "town: full band theme A3-A8 (cymbal)"))
    # vamp: wait for the confusion
    oompah(b, 10.0, ["Bb"] * 4, 0.5, True, 0.38)
    snare_bar(b, 10.0, "light", 0.45)
    b.cues.append((10.0, "vamp bar, no melody: room for timetables confusion"))

    # ============ CONFUSION 16 - 24: stumbling snare drive, dominant pedal, chromatic discomfort
    oompah(b, 16.0, ["F7"] * 4, 0.65, True, 0.5)
    snare_bar(b, 16.0, "march", 0.62, steps=range(8))
    snare_bar(b, 16.0, "drive", 0.5, steps=range(8, 16), cres=0.3)
    climb = [("F7", 18.0), ("F#o7", 19.0), ("Gm", 20.0), ("G#o7", 21.0)]
    for i, (c, t) in enumerate(climb):
        m = CH[c]["oom"][0]
        for k in range(2):
            b.add("tuba", I.brass(F(m), 0.2, 0.65 + 0.05 * i, _r(), "tuba"), t + k * 0.25, -0.1)
        for k, mm in enumerate(CH[c]["pah"]):
            b.add("pah", I.brass(F(mm), 0.14, 0.45 + 0.05 * i, _r(), "horn"), t + 0.25 + 0.004 * k, 0.32 - 0.12 * k)
        for k in range(4):
            b.add("glock", I.glock(F(96 + i), 0.2 + 0.04 * i, _r(), dur=0.5), t + k * Q / 4, -0.35)
    snare_bar(b, 19.0, "drive", 0.58, steps=range(8), cres=0.45)
    roll(b, 21.5, 24.0, 0.4, 0.9)
    b.cues.append((16.0, "confusion: F7 pedal, chromatic climb, snare drive"))
    b.cues.append((24.0, "build-up to pivot - roll into silence"))

    # ============ PIVOT 24 - 32: slow pad, warm, explanatory (music pulls back)
    chords = [(24.0, 25.5, [46, 58, 62, 65]), (25.5, 27.2, [46, 55, 63, 67]),
              (27.2, 28.7, [46, 58, 62, 65]), (28.7, 30.4, [41, 57, 60, 63]), (30.4, 32.0, [46, 58, 62, 65])]
    for (ta, tb_, ms) in chords:
        b.add("pad", I.pad([F(m) for m in ms], tb_ - ta, 0.5, _r(), att=0.5, rel=0.6), ta, 0.0)
    for tb_, m in zip([24.2, 25.8, 27.4, 29.0, 30.6], [86, 82, 87, 82, 84]):
        b.add("vibes", I.vibes(F(m), 0.45, _r(), dur=1.4, damp=0.7), tb_, -0.25)
    b.cues.append((24.0, "pivot: warm pad Bb-Eb/Bb-Bb-F7-Bb, vibes, 'You see, sun time moves west'"))

    # ============ ANALOGY 32 - 40: music-box waltz, gentle swing
    beat = T.SWING_T / 3 if hasattr(T, 'SWING_T') else 0.25
    ch3 = ["Bb", "Bb", "Eb", "F7", "Bb"]
    bass = [46, 46, 39, 41, 46]
    up = [[None, None, 77], [82, 86, 89], [87, 91, 94], [89, 93, 96], [94, None, None]]
    for k, tb_ in enumerate([32.0, 33.75, 35.5, 37.25, 39.0]):
        b.add("pluck", I.pluck(F(bass[k]), 0.8, _r(), dur=1.0), tb_, -0.05)
        if k < 4:
            for j in (1, 2):
                for mm in CH[ch3[k]]["hi"][1:]:
                    b.add("pluck", I.pluck(F(mm), 0.4, _r(), dur=0.5, bright=0.6), tb_ + j * beat, 0.25)
        for j, m in enumerate(up[k]):
            if m:
                b.add("musicbox", I.musicbox(F(m), 0.6, _r()), tb_ + j * beat, 0.2)
        if k >= 1:
            b.add("triangle", I.triangle(0.3, _r()), tb_, 0.35)
    for (ta, tb_, ms) in [(32.0, 34.0, [58, 62, 65]), (34.0, 36.0, [58, 63, 67]),
                          (36.0, 38.0, [57, 60, 63]), (38.0, 40.0, [58, 62, 65])]:
        b.add("pad", I.pad([F(m) for m in ms], tb_ - ta, 0.3, _r(), att=0.3, rel=0.4), ta, 0.0)
    b.cues.append((32.0, "analogy: music-box waltz, 'Imagine you're on that train'"))

    # ============ CONSEQUENCE 40 - 52: march returns, steady, four time zones
    m2 = theme(40.0, bars=[1, 2, 3, 4])
    m2 = [n for n in m2 if n[0] < 51.8]
    chorus(b, "whistle", m2, 5, 54, spread=0.7, vel=0.85, solo_gain=0.9)
    melody(b, "glock", m2, 0.34, 12, "glock", -0.35)
    b.add("cymbal", I.cymbal(0.25, _r()), 40.0, 0.0)
    for bar in (1, 2, 3, 4):
        tb = 40.0 + (bar - 1) * 2
        oompah(b, tb, CHB[bar], 0.52, False, 0.34)
        snare_bar(b, tb, "march", 0.42, steps=range(16))
    b.cues.append((40.0, "consequence: march returns, four standard time zones"))

    # ============ CALLBACK 52 - 60: lazy swung version, vibes melody, walking bass
    tn = theme(52.0, bars=[1, 2], swing=True, late=0.025)
    tn += [(56.0 + 0.025, Q, 82), (56.5 + 0.025, Q / 2, 77),
           (56.5 + Q * 2 / 3 + 0.025, Q / 2, 74), (57.0 + 0.02, 0.5, 70)]
    melody(b, "vibes", tn, 0.6, 0, "vibes", -0.25)
    walk = [46, 50, 53, 50, 41, 45, 46, 48, 46, 41, 34]
    for k, m in enumerate(walk):
        b.add("pluck", I.pluck(F(m), 0.85 if k < 10 else 0.95, _r(), dur=0.9 if k < 10 else 0.6), 52.0 + k * Q, -0.05)
    for k in range(8):
        t = 52.0 + k * Q
        b.add("brush", I.brush(0.55 if k % 2 else 0.35, _r(), dur=0.42, swish=True), t - 0.05, 0.1)
        b.add("brush", I.brush(0.35, _r()), t + Q * 2 / 3, 0.15)
    for (t, c) in [(52.5, "Bb"), (53.5, "Bb"), (54.5, "F"), (55.5, "Bb")]:
        for mm in CH[c]["hi"]:
            b.add("vibes", I.vibes(F(mm), 0.22, _r(), dur=0.9, damp=0.3, trem_depth=0.2), t + 0.02, 0.3)
    for mm in [58, 62, 65, 70]:
        b.add("vibes", I.vibes(F(mm), 0.32, _r(), dur=0.6, damp=None, trem_depth=0.3), 58.0, 0.2)
    b.add("triangle", I.triangle(0.25, _r(), dur=0.5), 58.0, 0.3)
    b.cues.append((52.0, "callback: relaxed swung ending, 'every train leaves after it arrives'"))
    end = np.ones(N)
    a = ns(59.5)
    end[a:] = np.linspace(1, 0, N - a) ** 1.5
    for k in b.tr:
        b.tr[k] *= end[None, :]
    return b


TARGET = {
    "whistle": 0.0, "fife": -3.0, "glock": -6.0, "tuba": -2.5, "pah": -7.5,
    "snare": -5.5, "cymbal": -11.0, "stab": -3.0, "timpani": -5.0, "pad": -3.5,
    "vibes": -2.0, "musicbox": -1.5, "pluck": -4.0, "brush": -13.0, "triangle": -15.0,
}


def render(b, ref=-20.0):
    hall = make_ir(1.5, 7, pre=0.018, hf=1.4)
    dry = np.zeros((2, N))
    wet_hall = np.zeros((2, N))
    levels = {}
    for k, x in b.tr.items():
        if not np.any(x):
            continue
        L = integrated(x)
        g = dbg(ref + TARGET.get(k, -6) - L)
        levels[k] = (round(L, 1), round(ref + TARGET.get(k, -6), 1))
        x = x * g
        b.tr[k] = x
        dry += x
        if k == "whistle":
            wet_hall += 0.16 * x
        else:
            wet_hall += b.send[k] * x
    out = dry + 0.7 * convolve_st(wet_hall.mean(0), hall)
    out = hp(out, 30, 2)
    return out, levels
