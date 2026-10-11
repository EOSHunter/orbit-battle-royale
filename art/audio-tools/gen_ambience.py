"""Ringfall ambience beds and ion-storm audio (48 kHz mono).

All loops are synthesised circularly: noise is filtered in the frequency domain, modulators are periodic,
discrete events wrap around the loop end and the reverb is a circular convolution -> seamless loops.
Usage: python gen_ambience.py [-- ringfall|storm]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sfx import *  # noqa: E402,F403
import numpy as np  # noqa: E402
from synth import (out, ns, tvec, rng, qfreq, spec_filter, g_bp, g_hp, g_lp, g_peak, g_mul,  # noqa: E402
                   crackle, colored, white, sine, saw, square, fm, place, norm, svf, env_exp, env_pts,
                   make_ir, reverb, pad_to, saturate, TAU, SR, fade)

AMB = "ambience/ringfall-ambience/"
STORM = "ambience/ion-storm-audio/"
AMB_RMS = -22.0

IR_FOREST = make_ir(t60=1.3, predelay=0.02, bright=0.6, early=12, early_span=0.12, seed=41)
IR_OPEN = make_ir(t60=2.2, predelay=0.03, bright=0.5, early=8, early_span=0.2, seed=42)


def pink(n, r, lo, hi, slope=-3.0):
    return norm(spec_filter(colored(n, r, slope), g_bp(lo, hi, 2)))


# ---------------------------------------------------------------- Ringfall
def wind(n, r):
    g1 = per_env(n, r, 0.12, 0.2, 1.5)
    g2 = per_env(n, r, 0.2, 0.1, 2.0)
    g3 = per_env(n, r, 0.08, 0.0, 3.0)
    low = pink(n, r, 30, 220, -6) * (0.5 + 0.5 * g1)
    mid = pink(n, r, 180, 1500) * g1
    high = pink(n, r, 1800, 7000) * g2
    whistle = norm(spec_filter(white(n, r), g_mul(g_peak(780, 0.05, 30), g_peak(1170, 0.04, 24), g_bp(500, 1800))))
    grass = norm(spec_filter(crackle(n, r, 300, 0.0006, circular=True), g_bp(2000, 8000))) * g2 ** 1.5
    return 0.8 * low + 0.7 * mid + 0.25 * high + 0.12 * whistle * g3 + 0.12 * grass


def bird_call(r, kind, p):
    if kind == 0:  # rising trill
        d = 0.38
        m = ns(d)
        fr = np.geomspace(1800, 3200, m) * p
        x = sine(fr, m) * (0.5 + 0.5 * np.sin(TAU * 24 * tvec(m))) * np.sin(np.pi * tvec(m) / d)
    elif kind == 1:  # falling vibrato whistle
        d = 0.55
        m = ns(d)
        fr = np.geomspace(3600, 1500, m) * p * (1 + 0.03 * np.sin(TAU * 7 * tvec(m)))
        x = (sine(fr, m) + 0.15 * sine(fr * 2, m)) * env_pts(m, [(0, 0), (0.03, 1), (d * 0.6, 0.7), (d, 0)])
    elif kind == 2:  # wide warble
        d = 0.65
        m = ns(d)
        fr = 2200 * p + 450 * np.sin(TAU * 11 * tvec(m))
        x = sine(fr, m) * np.sin(np.pi * tvec(m) / d) ** 0.8
    elif kind == 3:  # double hoot (low, hollow)
        m = ns(0.2)
        h = lambda f: (sine(np.geomspace(f, f * 0.86, m), m) + 0.35 * sine(np.geomspace(f * 2, f * 1.72, m), m)) \
            * np.sin(np.pi * tvec(m) / 0.2) ** 1.5
        x = events(0.65, [(0.0, h(640 * p), 1.0), (0.32, h(560 * p), 0.9)])
    else:  # chirp series
        k = r.integers(4, 7)
        m = ns(0.06)
        c = sine(np.geomspace(2500 * p, 3600 * p, m), m) * np.sin(np.pi * tvec(m) / 0.06)
        x = events(0.1 * k + 0.1, [(i * 0.095, c, 1.0 - 0.08 * i) for i in range(k)])
    return norm(fade(x, 0.003, 0.01))


def wildlife(n, r):
    t = tvec(n)
    bed = pink(n, r, 900, 6000) * per_env(n, r, 0.3, 0.3) * 0.15 + pink(n, r, 40, 400, -6) * 0.25
    cic = band(n, r, 4500, 6800) * (0.5 + 0.5 * np.cos(TAU * qfreq(28, n) * t)) ** 4 * per_env(n, r, 0.06, 0.1, 2)
    crick = np.zeros(n)
    m = ns(0.03)
    pip = sine(4300, m) * np.sin(np.pi * tvec(m) / 0.03)
    t0 = 0.0
    while t0 < n / SR:
        for j in range(3):
            place(crick, pip, ns(t0 + j * 0.045), 1.0, wrap=True)
        t0 += r.uniform(0.6, 1.1)
    buzz = fm(qfreq(2800, n), qfreq(90, n), 3.0, n) * bumps(n, [7.0, 21.0], 1.2) * 0.5
    calls = np.zeros(n)
    for i in range(20):
        kind = i % 5
        x = bird_call(r, kind, r.uniform(0.85, 1.2))
        far = r.random() < 0.45
        if far:
            x = lp(x, 2500) * 0.4
        place(calls, x, r.integers(0, n), r.uniform(0.45, 1.0), wrap=True)
    x = bed + 0.3 * cic + 0.18 * crick + 0.12 * buzz + 0.7 * calls
    return reverb(x, IR_FOREST, wet=0.35, circular=True)


def water(n, r):
    L = n / SR
    waves = np.cumsum(r.uniform(1.9, 2.8, 14))
    waves = waves[waves < L - 0.5]
    wv = bumps(n, waves, 0.35)
    wv2 = bumps(n, waves + 0.35, 0.3)
    lap = pink(n, r, 60, 600) * (0.3 + wv)
    wash = pink(n, r, 500, 3500) * (0.15 + wv2)
    bub = np.zeros(n)
    for _ in range(55):
        d = r.uniform(0.01, 0.035)
        m = ns(d * 5)
        f0 = r.uniform(500, 2200)
        fr = f0 * (1 + 0.9 * tvec(m) / (d * 5))
        place(bub, sine(fr, m) * env_exp(m, d, 0.001), r.integers(0, n), r.uniform(0.2, 1.0), wrap=True)
    glass = np.zeros(n)
    for _ in range(6):
        place(glass, glass_hit(r, r.uniform(2400, 4800), 0.5, dur=2.0), r.integers(0, n), r.uniform(0.3, 1.0), wrap=True)
    x = 0.8 * lap + 0.45 * wash + 0.25 * norm(bub) + 0.05 * norm(glass)
    return reverb(x, IR_OPEN, wet=0.2, circular=True)


def colony(n, r):
    t = tvec(n)
    hum_ = sum(a * np.sin(TAU * qfreq(60 * k, n) * t + r.uniform(0, TAU))
               for k, a in [(1, 1.0), (2, 0.6), (3, 0.45), (4, 0.2), (5, 0.25), (7, 0.12), (9, 0.08)])
    buzz = saturate(np.sin(TAU * qfreq(120, n) * t) * 3, 3) * 0.3
    vent = pink(n, r, 150, 2200) * per_env(n, r, 0.15, 0.7)
    fan = (np.sin(TAU * qfreq(232, n) * t) + 0.4 * np.sin(TAU * qfreq(464, n) * t)) * (1 + 0.2 * np.sin(TAU * qfreq(7, n) * t))
    clanks = np.zeros(n)
    for t0, f in [(3.1, 520), (11.7, 740), (17.9, 430)]:
        place(clanks, lp(metal_hit(r, f, 0.12, bright=0.7), 2500), ns(t0), 1.0, wrap=True)
    beeps = np.zeros(n)
    m = ns(0.12)
    b = sine(1046.5, m) * np.sin(np.pi * tvec(m) / 0.12) ** 0.5
    for t0 in [8.0, 8.25]:
        place(beeps, b, ns(t0), 1.0, wrap=True)
    x = 0.45 * norm(hum_) + 0.15 * buzz + 0.7 * vent + 0.12 * norm(fan) + 0.25 * clanks + 0.05 * beeps
    return reverb(x, IR_OPEN, wet=0.25, circular=True)


def interior(n, r):
    t = tvec(n)
    hvac = norm(spec_filter(colored(n, r, -4), g_mul(g_lp(500, 2), g_hp(25, 2), g_peak(120, 0.5, 5), g_peak(340, 0.4, 4))))
    hum_ = sum(a * np.sin(TAU * qfreq(50 * k, n) * t) for k, a in [(1, 1.0), (2, 0.5), (3, 0.3), (4, 0.15)])
    air = pink(n, r, 1000, 4000) * per_env(n, r, 0.1, 0.7)
    return 0.9 * hvac + 0.1 * norm(hum_) + 0.12 * air


def ringfall():
    loops = [("wind-open-loop.wav", 24.0, wind, 4101), ("bloomwild-wildlife-loop.wav", 26.0, wildlife, 4102),
             ("glass-basin-water-loop.wav", 24.0, water, 4103), ("colony-hum-loop.wav", 24.0, colony, 4104),
             ("interior-tone-loop.wav", 20.0, interior, 4105)]
    for name, dur, fn, seed in loops:
        x = fn(ns(dur), rng(seed))
        out(AMB + name, x, loop=True, rms_db=AMB_RMS if name != "interior-tone-loop.wav" else -26.0)


# ---------------------------------------------------------------- Ion storm
def rumble_bursts(r, dur, count, span, lo_cut, bright=1.0):
    n = ns(dur)
    x = np.zeros(n)
    for i in range(count):
        t0 = span[0] + (span[1] - span[0]) * r.random() ** 1.3
        a = r.uniform(0.03, 0.25)
        d = r.uniform(0.25, 1.1)
        m = ns(a + d * 4)
        e = env_pts(m, [(0, 0), (a, 1), (a + d * 4, 0)]) ** 2
        b = lp(colored(m, r, -4), lo_cut * r.uniform(0.7, 1.3) * bright, order=2) * e
        place(x, b, ns(t0), r.uniform(0.3, 1.0) * (1 - 0.5 * (t0 - span[0]) / (span[1] - span[0] + 1e-9)))
    return norm(x)


def thunder_distant(r):
    x = rumble_bursts(r, 8.0, 26, (0.0, 3.5), 300)
    x = reverb(x, ir("outdoor_long"), wet=0.6)[: ns(8.0)]
    return lp(x, 450, order=2)


def thunder_close(r):
    n = ns(7.0)
    x = np.zeros(n)
    m = ns(0.35)
    crack = filt(crackle(m, r, 25000, 0.0002), [("hp", 900)]) * env_exp(m, 0.06, 0.0005)
    tear = hp(white(m, r), 400) * env_exp(m, 0.03, 0.0002)
    place(x, saturate(norm(crack + 0.8 * tear) * 2.5, 2.5), 0, 1.0)
    zz = ns(0.25)
    fz = np.geomspace(4000, 300, zz)
    place(x, fm(fz, fz * 1.5, 3.0, zz) * env_exp(zz, 0.06, 0.0005), 0, 0.35)
    place(x, thud(r, 45, 0.6, drop=2.0, noise_lp=300, dur=3.0), ns(0.02), 0.9)
    roll = rumble_bursts(r, 6.5, 30, (0.05, 3.0), 900, bright=1.0)
    place(x, roll, ns(0.05), 0.8)
    return reverb(x, ir("outdoor_long"), wet=0.4)[:n]


def storm_wall(n, r):
    t = tvec(n)
    roar = pink(n, r, 120, 2600) * per_env(n, r, 0.5, 0.45)
    throb = 1 + 0.35 * np.sin(TAU * qfreq(0.5, n) * t)
    rum = pink(n, r, 20, 110, -6) * throb
    sizzle = band(n, r, 3000, 10000) * per_env(n, r, 20, 0.2, 2)
    field = norm(spec_filter(crackle(n, r, 160, 0.0004, circular=True), g_bp(1500, 8000)))
    arcs = np.zeros(n)
    for _ in range(12):
        k = ns(r.uniform(0.03, 0.08))
        a = filt(crackle(k, r, 9000, 0.0002), [("hp", 1200), ("lp", 9000)])
        place(arcs, fade(a, 0.002, 0.01), r.integers(0, n), r.uniform(0.3, 1.0), wrap=True)
    drone = spec_filter(saw(qfreq(41.2, n), n) + saw(qfreq(41.2, n) + 3 * SR / n, n), g_lp(300, 2))
    x = 0.8 * roar + 0.7 * rum + 0.18 * sizzle + 0.3 * field + 0.35 * norm(arcs) + 0.35 * norm(drone)
    return reverb(x, IR_OPEN, wet=0.3, circular=True)


def storm_damage(n, r):
    t = tvec(n)
    f = qfreq(55, n)
    buzz = saw(f, n, 0.37) + saw(f + SR / n, n, 0.71) + 0.5 * square(qfreq(82.5, n), n, 0.13)
    buzz = saturate(spec_filter(buzz, g_bp(150, 3200, 2)) * 2.0, 2.0)
    pulse = 0.55 + 0.45 * (0.5 + 0.5 * np.cos(TAU * qfreq(1.5, n) * t)) ** 3
    sizzle = band(n, r, 3000, 11000) * per_env(n, r, 30, 0.1, 2)
    whine = np.sin(TAU * qfreq(2640, n) * t) * (0.6 + 0.4 * np.sin(TAU * qfreq(0.5, n) * t))
    sub = np.sin(TAU * qfreq(36, n) * t)
    x = 0.7 * norm(buzz) * pulse + 0.35 * sizzle + 0.05 * whine + 0.35 * sub * pulse
    return x


def storm():
    out(STORM + "storm-wall-loop.wav", storm_wall(ns(16.0), rng(4201)), loop=True, rms_db=-18.0)
    for k in range(2):
        out(STORM + f"thunder-distant-{k + 1:02d}.wav", thunder_distant(rng(4210 + k)), rms_db=-14.0, fin=0.05, fout=1.0)
        out(STORM + f"thunder-close-{k + 1:02d}.wav", thunder_close(rng(4220 + k)), rms_db=-9.0, fout=1.0)
    out(STORM + "inside-storm-damage-loop.wav", storm_damage(ns(6.0), rng(4230)), loop=True, rms_db=-18.0)


def main():
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if not args or "ringfall" in args:
        ringfall()
    if not args or "storm" in args:
        storm()


if __name__ == "__main__":
    main()
