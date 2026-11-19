# Every sound effect + ambience bed of the train short as a cue list timed to the picture (timeline.py), rendered
# into one stereo SFX stem. Levels follow the user's standard mix: each EVENT has a "naive" level (LU relative to the
# voice stem, measured as the event's max momentary loudness) and is placed SFX_DB = -6 dB under it; ambience BEDS
# (integrated loudness) are not reduced. Distance to the camera adds gain, a low-pass and more valley reverb.
import math
import numpy as np
from dsp import (SR, ns, tt, rng, dbg, lp, hp, bp, peq, colored, smooth_noise, ramp, fades, shape,
                 phase, modal, impulse_train, pan, st, place, fades as dsp_fades, widen, make_ir, convolve_st,
                 momentary_max, integrated)
import sfx_gen as G
import timeline as T

N = ns(T.DUR)
SFX_DB = -6.0


class Cue:
    def __init__(self, t, name, desc, gen, naive, kind="event", p=0.0, extra=0.0, lpf=None, send=0.12, group=None, cut=None):
        self.t, self.name, self.desc, self.gen, self.naive = t, name, desc, gen, naive
        self.kind, self.p, self.extra, self.lpf, self.send, self.cut = kind, p, extra, lpf, send, cut
        self.group = group or name
        self.applied = naive + (SFX_DB if kind == "event" else 0.0) + extra
        self.measured = None


def cues():
    C = []
    R = rng(1831)
    rr = lambda: rng(int(R.integers(1 << 30)))
    add = C.append

    # ------------------------------------------------ ambience beds (not reduced by the -6 dB event rule)
    def amb_day(dur, river=0.5, flags=0.25, seed=1):
        def g():
            r = rng(seed)
            n = ns(dur)
            x = G.breeze(dur, r, 1.0, 0.15, 850)
            rv = bp(colored(n, r, 0.8), 180, 1800, 1) * river * (0.8 + 0.2 * smooth_noise(n, r, 0.3))
            x += st(rv)
            x += pan(G.bird_chirps(dur, r, 0.45, "sparrow") * 0.08, 0.5)
            x += pan(G.bird_chirps(dur, r, 0.3, "sparrow") * 0.05, -0.6)
            x += pan(G.flag_flutter(dur, r) * flags, 0.3)
            return fades(x, 0.4, 0.6), 0.0
        return g

    add(Cue(0.0, "amb_station", "station platform air: breeze, distant river, sparrows, platform murmur (all shots)",
            _cut(amb_day(T.DUR, 0.55, 0.3, seed=1), T.DUR, 0.4, 0.4), -30, "bed", send=0.0))

    # golden-hour ambience for shots 8-9
    def amb_golden(dur, seed=43):
        def g():
            r = rng(seed)
            n = ns(dur)
            x = G.breeze(dur, r, 0.7, 0.1, 650)
            x += st(lp(bp(colored(n, r, 0.8), 150, 1400, 1), 1200) * 0.35)
            x += pan(G.bird_chirps(dur, r, 0.35, "blackbird") * 0.06, -0.5)
            x += pan(G.bird_chirps(dur, r, 0.25, "blackbird") * 0.04, 0.6)
            return fades(x, 0.3, 0.4), 0.0
        return g

    wd = T.shot_t(9)[1] - T.shot_t(8)[0]
    add(Cue(T.shot_t(8)[0], "amb_golden", "golden-hour calm: soft breeze, blackbird phrases, faint crickets (shots 8-9)",
            _env(lambda: (amb_golden(wd, 43)()[0], 0.0), wd, 0.3, 0.3), -29, "bed", send=0.0))

    # ------------------------------------------------ station ambience: crowd murmur on platform
    add(Cue(4.33, "platform_murmur", "station platform: crowd murmur ~18 voices, distant town hubbub (shot 2 onwards)",
            lambda: (_murmur(50.0, rng(21), 18, early=False), 0.0), -10, lpf=3600, send=0.35))

    # ------------------------------------------------ train whistle (mournful, distant -> close)
    add(Cue(0.5, "train_whistle_hook", "long lonesome train whistle, distant, echoing off the station (hook)",
            lambda: (G.whistle_phrase(4.0, rng(11), base=165, shape="mournful"), 0.0), -8, p=-0.25, send=0.15))
    add(Cue(3.8, "train_whistle_button", "short whistle button exactly on the white flash (frame 130)",
            lambda: (G.whistle_phrase(0.6, rng(12), base=220, shape="staccato"), 0.0), -6, p=-0.2, send=0.12))

    # train approaching / departing chug
    add(Cue(7.0, "train_chug_near", "train chugging rhythm, close on the platform, wheels clicking rails",
            lambda: (G.train_chug(8.0, rng(13), intensity=0.9), 0.0), -5, p=0.1, send=0.1))
    add(Cue(28.0, "train_chug_depart", "train pulling away, chugging fading into distance",
            lambda: (G.train_chug(10.0, rng(14), intensity=0.6), 0.0), -7, p=0.2, send=0.15))

    # ------------------------------------------------ clock chimes (town hall clocks, different times)
    # Cleveland clock strikes 11:00 as the train leaves
    add(Cue(9.5, "clock_chimes_cleveland", "Cleveland town hall clock striking eleven (train departure)",
            lambda: (G.clock_chimes(11, rng(31)), 0.0), -4, p=-0.3, send=0.2))
    # Pittsburgh clock strikes 11:11 as the train arrives (11 minutes later)
    add(Cue(24.0, "clock_chimes_pittsburgh", "Pittsburgh town hall clock striking eleven-eleven (impossible arrival)",
            lambda: (G.clock_chimes(11.18, rng(32)), 0.0), -4, p=0.3, send=0.2))

    # ------------------------------------------------ ticket punch + departure bell
    add(Cue(14.5, "ticket_punch", "conductor punches tickets: sharp clip-clop along the carriage",
            lambda: (G.ticket_punch(rng(41)), 0.0), -10, p=0.0, send=0.05))
    add(Cue(20.0, "departure_bell", "station departure bell: brass 'ding-ding', train about to leave",
            lambda: (G.departure_bell(rng(42)), 0.0), -6, p=0.0, send=0.1))

    # ------------------------------------------------ camera-move / transition whooshes
    for f, desc in [(130, "white flash cut"), (300, "cut to timetables"), (460, "train leaves station"),
                    (640, "train arrives early"), (820, "confused passengers"), (980, "wait how?"),
                    (1120, "golden-hour pivot"), (1280, "analogy on the train"),
                    (1440, "four time zones"), (1620, "tourists on rebuilt platform")]:
        add(Cue(T.fr(f), "whoosh_cam", f"camera {desc}",
                (lambda r=rr(): (G.whoosh(0.6, r, 0.09, 330, 2000, 0.8, 0.18, 0.15), 0.09)),
                -11, send=0.12))
    for f, desc in [(130, "crossfade town -> timetables"), (460, "crossfade leave -> arrive"),
                    (1120, "crossfade to golden"), (1280, "crossfade to analogy"),
                    (1440, "crossfade to time zones"), (1620, "crossfade to tourists")]:
        add(Cue(T.fr(f), "whoosh_xfade", desc,
                (lambda r=rr(): (G.whoosh(0.8, r, 0.32, 300, 1600, 0.9, 0.22, 0.1), 0.32)), -12, send=0.15))

    # ------------------------------------------------ platform footfalls (passengers walking)
    for k in range(40):
        tm = 5.0 + k * 1.25 + rr().uniform(-0.2, 0.2)
        if tm > T.DUR - 0.5:
            break
        d = T.train_distance(tm)
        g, lpf, send = T.dist_fx(d)
        pp = rr().uniform(-0.5, 0.5)
        add(Cue(tm, "platform_step", "passenger footstep on the station platform",
                (lambda r=rr(): (G.stroll_step(r, rr().uniform(0.3, 1.0)), 0.0)),
                -9, p=pp, extra=max(g, -8.0), lpf=lpf, send=send, group="platform_steps"))

    return C


# ================================================================ helpers for composite cues
def _cut(gen, dur, fin, fout):
    def g():
        x, a = gen()
        return fades(x, fin, fout), a
    return g


def _env(gen, dur, fin, fout):
    return _cut(gen, dur, fin, fout)


def _murmur(dur, r, voices, early=False):
    n = ns(dur)
    out = np.zeros((2, n))
    for v in range(voices):
        kind = r.uniform()
        base, scale = ((r.uniform(95, 140), r.uniform(0.95, 1.05)) if kind < 0.45 else
                       (r.uniform(175, 235), r.uniform(1.12, 1.2)) if kind < 0.85 else (r.uniform(260, 330), r.uniform(1.25, 1.35)))
        y = G.babble(dur, r, base, scale, r.uniform(3.6, 4.8), r.uniform(0.55, 0.8), fmax=3400)
        y = lp(y, r.uniform(2200, 3600), 1) * r.uniform(0.3, 1.0)
        out += pan(y, r.uniform(-0.85, 0.85))
    if early:
        for k in range(4):
            h = G.hurrah(r, r.uniform(110, 230), r.uniform(1.0, 1.18))
            place(out, pan(lp(h, 3000, 1) * 0.5, r.uniform(-0.8, 0.8)), r.uniform(0.2, 1.6))
    return fades(out, 0.25, 0.8)


# ================================================================ render
def render(v_ref, on_event=None):
    """v_ref = integrated loudness of the voice stem (stereo). Returns (stereo stem, cue list with measured levels).
    on_event(cue, x, t0) is called with every placed (dry) event, for analysis."""
    C = cues()
    out = np.zeros((2, N))
    send = np.zeros(N)
    for c in C:
        x, anchor = c.gen()
        x = np.asarray(x, float)
        x = pan(x, c.p) if x.ndim == 1 else x
        if c.cut is not None:
            k = ns(c.cut - (c.t - anchor))
            if 0 < k < x.shape[1]:
                x = dsp_fades(x[:, :k], 0.0, 0.02)
        tgt = v_ref + c.applied
        cur = momentary_max(x) if c.kind == "event" else integrated(x)
        if np.isfinite(cur):
            x = x * dbg(tgt - cur)
        if c.lpf:
            x = lp(x, c.lpf, 1)
        c.measured = momentary_max(x) - v_ref if c.kind == "event" else integrated(x) - v_ref
        t0 = c.t - anchor
        place(out, x, t0)
        if on_event:
            on_event(c, x, t0)
        if c.send > 0:
            G._place_mono(send, c.send * x.mean(0), t0)
    valley = make_ir(1.1, 77, pre=0.01, hf=1.6, early=[(0.09, 0.45, -0.5), (0.14, 0.3, 0.6), (0.23, 0.2, -0.2)])
    out += 0.55 * convolve_st(send, valley)
    out = hp(out, 25, 2)
    end = ns(T.DUR - 0.12)
    out[:, end:] *= np.linspace(1, 0, N - end)[None, :] ** 2
    return out, C
