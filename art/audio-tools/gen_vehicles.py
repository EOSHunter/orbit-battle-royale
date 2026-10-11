"""Vehicle audio (Mule, Skimmer, Strider, Kestrel) and drop-transport audio.

Engine loops are built from phase-locked oscillators whose frequencies are quantised to the loop length,
circular band noise and periodic amplitude modulation, so every loop is seamless by construction.
Usage: python gen_vehicles.py [-- vehicles|drop]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sfx import *  # noqa: E402,F403
import numpy as np  # noqa: E402
from synth import (out, ns, tvec, rng, qfreq, spec_filter, g_bp, g_hp, g_lp, g_peak, g_mul,  # noqa: E402
                   crackle, colored, white, sine, saw, square, place, norm, svf, env_exp, env_pts,
                   make_ir, reverb, pad_to, saturate, TAU, SR, fade)

LOOP_N = ns(4.0)


class Osc:
    """Oscillator factory: loop mode quantises frequencies; one-shot mode applies a per-sample pitch scale."""

    def __init__(self, n, fscale=None):
        self.n = n
        self.fscale = fscale
        self.t = tvec(n)

    def ph(self, f):
        if self.fscale is None:
            return qfreq(f, self.n) * self.t
        return np.cumsum(f * self.fscale) / SR

    def sin(self, f, p0=0.0):
        return np.sin(TAU * (self.ph(f) + p0))


def nband(n, r, lo, hi, order=2):
    return norm(spec_filter(white(n, r), g_bp(lo, hi, order)))


def pulse_am(ph, sharp=4.0):
    """Puff-shaped periodic envelope from a phase in cycles."""
    return (0.5 + 0.5 * np.cos(TAU * ph)) ** sharp


# ---------------------------------------------------------------- engines
def combustion(o, r, f_cyc, firings, rolloff, peaks, drive, puff, irregular, roar=0.0, mech=0.15):
    n = o.n
    ph = o.ph(f_cyc)
    x = np.zeros(n)
    kmax = int(min(5000, rolloff * 4) / f_cyc)
    shape = g_mul(g_lp(rolloff, 2), *[g_peak(p, 0.6, 6) for p in peaks])
    for k in range(1, kmax + 1):
        f = k * f_cyc
        a = shape(np.array([f]))[0] * (1.0 if k % firings == 0 else irregular * r.uniform(0.3, 1.0))
        x += a * np.sin(TAU * k * ph + r.uniform(0, TAU)) / (1 + 0.02 * k)
    x = norm(x)
    puffs = nband(n, r, 120, rolloff * 2.5) * pulse_am(ph * firings, 3.0)
    roar_n = nband(n, r, 350, 1800)
    valve = nband(n, r, 2500, 8000) * (0.6 + 0.4 * pulse_am(ph * firings * 2, 2))
    y = x + puff * norm(puffs) + roar * roar_n + mech * valve
    return saturate(norm(y) * drive, drive)


def skimmer_engine(o, r, whine, fan, hover, air):
    n = o.n
    w = o.sin(whine) + 0.45 * o.sin(whine * 2) + 0.2 * o.sin(whine * 3.0) + 0.3 * o.sin(whine * 0.5)
    w *= 1 + 0.08 * o.sin(5.0)
    fanph = o.ph(fan)
    fan_n = nband(n, r, 80, 700) * (0.6 + 0.4 * pulse_am(fanph, 1.5))
    hum = o.sin(hover) + 0.5 * o.sin(hover * 2) + 0.25 * o.sin(hover * 3)
    hum *= 1 + 0.15 * o.sin(3.0)
    hiss = nband(n, r, 3500, 12000)
    return 0.35 * norm(w) + 0.6 * fan_n + 0.45 * norm(hum) + air * hiss


def strider_engine(o, r, f_cyc, whine, load):
    diesel = combustion(o, r, f_cyc, 6, 380, [90, 260], 1.3 + load, 0.6, 0.35, roar=0.15 * load, mech=0.1)
    n = o.n
    gear = o.sin(whine) + 0.3 * o.sin(whine * 2.0) + 0.15 * o.sin(whine * 3.0)
    servo = o.sin(whine * 0.25) * (1 + 0.2 * o.sin(2.0))
    clank = np.zeros(n)
    return 0.8 * diesel + (0.08 + 0.1 * load) * norm(gear) + 0.15 * norm(servo) + 0.0 * clank


def kestrel_engine(o, r, blade, turbine, wash):
    n = o.n
    bph = o.ph(blade)
    slap_src = nband(n, r, 70, 1400, 2)
    fr = bph + 0.5 - np.floor(bph + 0.5)  # offset so the loop seam falls mid-decay, not on a slap
    env = (1 - np.exp(-fr / 0.004)) * np.exp(-fr / 0.07)
    slap = slap_src * env + 0.6 * np.sin(TAU * bph) * env
    thump = o.sin(blade) + 0.6 * o.sin(blade * 2) + 0.3 * o.sin(blade * 3)
    tail = saturate(o.sin(blade * 5.3) * 2, 2) + 0.3 * o.sin(blade * 10.6)
    tur = o.sin(turbine) + 0.5 * o.sin(turbine * 1.37) + 0.3 * o.sin(turbine * 2)
    w = nband(n, r, 200, 3000) * (0.7 + 0.3 * pulse_am(bph, 1))
    return 0.8 * norm(slap) + 0.4 * norm(thump) + 0.12 * norm(lp(tail, 1200, circular=o.fscale is None)) \
        + 0.08 * norm(tur) + wash * w


VEH = {
    "mule": {
        "idle": lambda o, r: combustion(o, r, 7.5, 4, 500, [170, 520], 1.6, 0.5, 0.45, mech=0.12),
        "load": lambda o, r: combustion(o, r, 13.5, 4, 1100, [190, 640], 2.6, 0.7, 0.35, roar=0.25),
        "high": lambda o, r: combustion(o, r, 20.0, 4, 1500, [220, 760], 3.0, 0.75, 0.3, roar=0.4),
    },
    "skimmer": {
        "idle": lambda o, r: skimmer_engine(o, r, 820, 55, 72, 0.05),
        "load": lambda o, r: skimmer_engine(o, r, 1350, 95, 86, 0.12),
        "high": lambda o, r: skimmer_engine(o, r, 2050, 140, 98, 0.22),
    },
    "strider": {
        "idle": lambda o, r: strider_engine(o, r, 4.5, 360, 0.0),
        "load": lambda o, r: strider_engine(o, r, 7.0, 620, 0.6),
        "high": lambda o, r: strider_engine(o, r, 9.5, 900, 1.0),
    },
    "kestrel": {
        "idle": lambda o, r: kestrel_engine(o, r, 12.0, 2600, 0.15),
        "load": lambda o, r: kestrel_engine(o, r, 16.0, 3300, 0.3),
        "high": lambda o, r: kestrel_engine(o, r, 19.0, 3900, 0.45),
    },
}

SIZE = {"mule": 1.0, "skimmer": 0.6, "strider": 1.4, "kestrel": 1.1}


def creak(r, dur, f0, f1, center=900, q=5.0):
    n = ns(dur)
    rate = np.geomspace(f0, f1, n)
    ph = np.cumsum(rate) / SR
    pulses = np.diff(np.floor(ph), prepend=0.0) * r.uniform(0.6, 1.0, n)
    x = svf(pulses + 0.02 * white(n, r), center, q, "bp")
    return norm(fade(x * np.sin(np.pi * tvec(n) / dur) ** 0.5, 0.005, 0.02))


def door(r, size, slam=1.0):
    return events(0.6, [(0.0, thud(r, 80 / size, 0.07 * size, noise_lp=900), 1.0 * slam),
                        (0.0, metal_hit(r, 650 / size ** 0.5, 0.08, bright=0.7), 0.5 * slam),
                        (0.005, rattle(r, 0.3, 3, 1800), 0.15 * slam), (0.0, click(r, 2600), 0.4)])


def pneumatic(r, dur=0.5):
    n = ns(dur)
    return norm(filt(white(n, r), [("hp", 1500), ("lp", 9000)]) * env_pts(n, [(0, 0), (0.02, 1), (dur * 0.4, 0.5), (dur, 0)]))


def enter_exit(v, r):
    s = SIZE[v]
    if v == "mule":
        ent = [(0.0, metal_hit(r, 1600, 0.02), 0.5), (0.0, click(r, 3000), 0.5), (0.08, creak(r, 0.35, 45, 25, 700), 0.25),
               (0.55, rustle(r, 0.4), 0.4), (0.7, thud(r, 95, 0.06), 0.7), (1.1, door(r, s), 1.0)]
        ext = [(0.0, metal_hit(r, 1600, 0.02), 0.5), (0.0, click(r, 3000), 0.5), (0.06, creak(r, 0.3, 40, 22, 650), 0.25),
               (0.35, rustle(r, 0.4), 0.4), (0.65, thud(r, 110, 0.04, noise_lp=1200), 0.6), (1.0, door(r, s, 0.8), 1.0)]
    elif v == "strider":
        ent = [(0.0, metal_hit(r, 1100, 0.04), 0.6), (0.05, pneumatic(r, 0.6), 0.5), (0.1, creak(r, 0.5, 30, 18, 450), 0.2),
               (0.8, rustle(r, 0.4), 0.4), (0.95, thud(r, 85, 0.07), 0.7), (1.35, door(r, s), 1.0),
               (1.4, pneumatic(r, 0.3), 0.25)]
        ext = [(0.0, metal_hit(r, 1100, 0.04), 0.6), (0.03, pneumatic(r, 0.6), 0.5), (0.1, creak(r, 0.5, 28, 18, 420), 0.2),
               (0.6, rustle(r, 0.4), 0.4), (0.9, thud(r, 100, 0.05, noise_lp=1000), 0.6), (1.25, door(r, s, 0.9), 1.0)]
    elif v == "skimmer":
        ent = [(0.0, rustle(r, 0.45), 0.5), (0.25, metal_hit(r, 1900, 0.03), 0.5), (0.3, thud(r, 130, 0.04), 0.6),
               (0.4, creak(r, 0.2, 60, 40, 1300, 4.0), 0.2), (0.6, click(r, 2600), 0.4), (0.62, metal_hit(r, 2400, 0.015), 0.3)]
        ext = [(0.0, click(r, 2600), 0.3), (0.05, rustle(r, 0.45), 0.5), (0.2, creak(r, 0.18, 55, 35, 1200, 4.0), 0.2),
               (0.45, thud(r, 120, 0.04, noise_lp=1200), 0.7), (0.47, metal_hit(r, 1700, 0.03), 0.35)]
    else:  # kestrel
        ent = [(0.0, metal_hit(r, 1500, 0.03), 0.5), (0.02, pneumatic(r, 0.7), 0.5), (0.4, metal_hit(r, 700, 0.05), 0.4),
               (0.45, thud(r, 110, 0.05), 0.5), (0.8, rustle(r, 0.4), 0.4), (1.05, click(r, 3400), 0.5),
               (1.07, metal_hit(r, 2800, 0.02), 0.4), (1.25, door(r, s, 0.7), 1.0)]
        ext = [(0.0, click(r, 3400), 0.4), (0.05, metal_hit(r, 1500, 0.03), 0.5), (0.1, pneumatic(r, 0.7), 0.5),
               (0.6, rustle(r, 0.4), 0.4), (0.85, metal_hit(r, 650, 0.06), 0.5), (0.85, thud(r, 100, 0.05), 0.6),
               (1.2, thud(r, 110, 0.04, noise_lp=1100), 0.5)]
    e = reverb(events(2.2, ent), ir("small"), wet=0.12)
    x = reverb(events(2.2, ext), ir("small"), wet=0.12)
    return e, x


def impact(v, r, k):
    s = SIZE[v]
    n = ns(1.6)
    x = np.zeros(n)
    place(x, thud(r, 75 / s ** 0.5, 0.1 * s, noise_lp=800), 0, 1.0)
    for i in range(5):
        place(x, metal_hit(r, r.uniform(350, 1300) / s ** 0.3, r.uniform(0.06, 0.14), bright=0.75),
              ns(r.uniform(0, 0.05)), r.uniform(0.3, 0.6))
    cr = filt(crackle(ns(0.5), r, 1800, 0.0004), [("hp", 500), ("lp", 6000)]) * env_exp(ns(0.5), 0.09, 0.001)
    place(x, norm(cr), ns(0.002), 0.6)
    place(x, rattle(r, 0.9, 6, 1500), ns(0.06), 0.25)
    if k == 1:
        place(x, glass_hit(r, 3000, 0.06), ns(0.03), 0.25)
    return reverb(x, ir("outdoor"), wet=0.2)


def destroyed(v, r):
    s = SIZE[v]
    n = ns(5.0)
    x = pad_to(explosion(r, 1.1 * s ** 0.5, 5.0), n)
    for i in range(8):
        place(x, metal_hit(r, r.uniform(300, 1500), r.uniform(0.05, 0.15), bright=0.7),
              ns(0.4 + r.uniform(0, 2.2) ** 1.2), r.uniform(0.05, 0.18))
    place(x, whoosh(r, 2.0, 180, 900, q=0.7, peak=0.25), ns(0.15), 0.2)
    if v == "skimmer":
        place(x, chirp(2100, 160, 0.9, tau=0.4, shape="saw") * 0.5, 0, 0.12)
    if v == "kestrel":
        m = ns(2.5)
        rate = np.geomspace(19, 4, m)
        ph = np.cumsum(rate) / SR
        sl = nband(m, r, 80, 1200) * np.exp(-((ph - np.floor(ph)) / 0.08)) * env_exp(m, 0.9)
        place(x, norm(sl), ns(0.05), 0.25)
    return x


def passby(v, r):
    dur = 7.0
    n = ns(dur)
    t = tvec(n)
    vel, d, c = 32.0, 140.0, 343.0
    xpos = vel * (t - dur * 0.5)
    dist = np.sqrt(xpos ** 2 + d ** 2)
    # pitch: observed frequency with propagation delay approximated by radial velocity
    vr = vel * xpos / dist
    fscale = c / (c + vr)
    o = Osc(n, fscale)
    eng = VEH[v]["load"](o, r)
    gain = (d / dist) ** 1.3
    eng = eng * gain
    fc = 500 + 3000 * (d / dist) ** 3
    eng = svf(eng, fc, 0.7, "lp")
    y = reverb(eng, ir("outdoor_long"), wet=0.6, dry=1.0)[:n]
    return y


def vehicles(only=()):
    for vi, v in enumerate(VEH):
        if only and v not in only:
            continue
        d = f"vehicle-audio/{v}-audio/"
        for si, state in enumerate(["idle", "load", "high"]):
            r = rng(3000 + vi * 10 + si)
            x = VEH[v][state](Osc(LOOP_N), r)
            out(d + f"engine-{state}-loop.wav", x, loop=True, rms_db=-18.0)
        out(d + "pass-by-distant.wav", passby(v, rng(3100 + vi)), rms_db=-18.0, fin=0.3, fout=0.5)
        e, x = enter_exit(v, rng(3200 + vi))
        out(d + "enter.wav", e, rms_db=-18.0)
        out(d + "exit.wav", x, rms_db=-18.0)
        for k in range(2):
            out(d + f"impact-{k + 1:02d}.wav", impact(v, rng(3300 + vi * 10 + k), k), rms_db=-12.0)
        out(d + "destroyed.wav", destroyed(v, rng(3400 + vi)), rms_db=-10.0, fout=0.6)


# ---------------------------------------------------------------- drop transport
DROP = "drop-transport/drop-transport-audio/"


def drop():
    n = ns(8.0)
    t = tvec(n)
    L = 8.0
    o = Osc(n)
    r = rng(3501)
    rumble = spec_filter(colored(n, r, -6), g_lp(220, 2))
    roar = nband(n, r, 300, 1600)
    whine = o.sin(1240) + 0.5 * o.sin(1860) + 0.3 * o.sin(2480)
    tone = o.sin(61.0) + o.sin(61.25) + 0.5 * o.sin(122.0) + 0.5 * o.sin(122.375)
    swell = 1 + 0.15 * np.sin(TAU * t / L)
    x = (norm(rumble) + 0.5 * roar + 0.05 * norm(whine) + 0.35 * norm(tone)) * swell
    out(DROP + "engine-exterior-loop.wav", spec_filter(x, g_lp(2500, 1)), loop=True, rms_db=-18.0)

    r = rng(3502)
    rumble = spec_filter(colored(n, r, -6), g_lp(140, 2))
    h = o.sin(48) + 0.6 * o.sin(96) + 0.3 * o.sin(144) + 0.2 * o.sin(192) + 0.15 * o.sin(400)
    air = nband(n, r, 700, 4500) * (0.85 + 0.15 * np.sin(TAU * 2 * t / L))
    rat = np.zeros(n)
    for _ in range(14):
        place(rat, rattle(r, 0.25, 3, r.uniform(1200, 2600), 0.01), r.integers(0, n), r.uniform(0.2, 1), wrap=True)
    cr = np.zeros(n)
    for t0 in [1.7, 5.3]:
        place(cr, creak(r, 0.6, 30, 18, 500, 6.0), ns(t0), 1.0, wrap=True)
    x = norm(rumble) + 0.3 * norm(h) + 0.25 * air + 0.12 * norm(rat) + 0.08 * cr
    x = reverb(x, ir("room"), wet=0.2, circular=True)
    out(DROP + "hold-interior-loop.wav", x, loop=True, rms_db=-19.0)

    r = rng(3503)
    m = ns(4.6)
    tm = tvec(m)
    motor_env = env_pts(m, [(0, 0), (0.4, 0), (0.6, 1), (3.5, 1), (3.7, 0), (4.6, 0)])
    fr = 110 + 60 * np.clip((tm - 0.4) / 3.1, 0, 1)
    motor = lp(saw(fr, m), 1500) + 0.3 * sine(fr * 8.3, m)
    hyd = filt(white(m, r), [("hp", 1200), ("lp", 6000)]) * env_pts(m, [(0, 0), (0.45, 0), (0.6, 1), (3.6, 0.6), (3.8, 0), (4.6, 0)])
    wind_env = env_pts(m, [(0, 0), (0.6, 0), (3.8, 1), (4.6, 0)])
    wind = svf(white(m, r), 300 + 5000 * wind_env, 0.7, "lp") * wind_env
    x = (0.4 * norm(motor * motor_env) + 0.25 * norm(hyd) + 0.6 * norm(wind))
    x = events(4.6, [(0.0, x, 1.0), (0.1, door(r, 2.0), 0.9), (0.15, pneumatic(r, 0.5), 0.4),
                     (3.65, door(r, 2.4), 1.0)])
    out(DROP + "ramp-open.wav", reverb(x, ir("room"), wet=0.2), rms_db=-15.0, fout=0.3)

    r = rng(3504)
    g = whoosh(r, 2.2, 250, 2600, q=0.6, peak=0.3, shape=1.2)
    buff = lp(white(ns(2.2), r), 250, order=2) * env_pts(ns(2.2), [(0, 0), (0.5, 1), (2.2, 0)])
    out(DROP + "jump-wind-gust.wav", g + 0.5 * norm(buff), rms_db=-14.0, fout=0.2)

    r = rng(3505)
    n = ns(6.0)
    t = tvec(n)
    o = Osc(n)
    roar = spec_filter(colored(n, r, -2), g_mul(g_lp(3500, 2), g_hp(60, 1), g_peak(700, 1.0, 4)))
    buffet = (0.6 + 0.4 * (lambda e: (e - e.min()) / (e.max() - e.min()))(spec_filter(r.standard_normal(n), g_lp(9, 3))))
    rumble = spec_filter(colored(n, r, -6), g_lp(120, 2)) * buffet
    whistle = spec_filter(white(n, r), g_peak(1350, 0.08, 30)) * (0.5 + 0.5 * np.sin(TAU * t / 6.0 * 2))
    whistle = spec_filter(whistle, g_bp(900, 2200, 2))
    x = norm(roar) * buffet + 0.6 * norm(rumble) + 0.1 * norm(whistle)
    out(DROP + "freefall-wind-loop.wav", x, loop=True, rms_db=-15.0)

    r = rng(3506)
    dirt = filt(crackle(ns(0.5), r, 2500, 0.0005), [("hp", 400), ("lp", 5000)]) * env_exp(ns(0.5), 0.12, 0.001)
    x = events(1.5, [(0.0, thud(r, 70, 0.13, noise_lp=500), 1.0), (0.0, dirt, 0.6), (0.01, rattle(r, 0.4, 5, 1600), 0.25),
                     (0.0, rustle(r, 0.5, 200, 3000), 0.5), (0.25, thud(r, 120, 0.05), 0.3)])
    out(DROP + "landing.wav", reverb(x, ir("outdoor"), wet=0.15), rms_db=-12.0)


def main():
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    names = [a for a in args if a in VEH]
    if not args or "vehicles" in args or names:
        vehicles(names)
    if not args or "drop" in args:
        drop()


if __name__ == "__main__":
    main()
