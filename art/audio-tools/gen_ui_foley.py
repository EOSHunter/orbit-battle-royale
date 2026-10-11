"""UI interface sounds, match feedback sounds and footstep foley (48 kHz mono).

Usage: python gen_ui_foley.py [-- ui|feedback|foley]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sfx import *  # noqa: E402,F403
import numpy as np  # noqa: E402
from synth import (mix, out, ns, tvec, rng, qfreq, spec_filter, g_bp, crackle, white, sine, saw, square, fm,  # noqa: E402
                   place, norm, env_exp, env_pts, make_ir, reverb, pad_to, saturate, TAU, SR, fade)

UI = "ui-audio/interface-sounds/"
FB = "ui-audio/match-feedback-sounds/"
FOLEY = "foley/footsteps/"
IR_UI = make_ir(t60=0.5, predelay=0.004, bright=1.0, early=4, early_span=0.02, seed=51)


def bell(f, dur, tau, ratio=2.0, index=0.8, attack=0.002):
    m = ns(dur)
    return fm(f, f * ratio, index * env_exp(m, tau * 0.6), m) * env_exp(m, tau, attack)


def blip(f, dur, tau, attack=0.001, harm=0.25):
    m = ns(dur)
    return (sine(f, m) + harm * sine(f * 2, m)) * env_exp(m, tau, attack)


def ui():
    r = rng(5001)
    x = events(0.18, [(0.0, blip(1480, 0.15, 0.03), 1.0), (0.0, click(r, 6000), 0.08)])
    out(UI + "navigate.wav", reverb(x, IR_UI, wet=0.12), rms_db=-15.0)
    x = events(0.6, [(0.0, bell(880, 0.4, 0.09), 0.8), (0.065, bell(1318.5, 0.5, 0.14), 1.0)])
    out(UI + "confirm.wav", reverb(x, IR_UI, wet=0.18), rms_db=-14.0)
    x = events(0.5, [(0.0, bell(1318.5, 0.3, 0.06, index=0.5), 0.8), (0.06, bell(880, 0.4, 0.1, index=0.5), 1.0)])
    out(UI + "back.wav", lp(reverb(x, IR_UI, wet=0.15), 4500), rms_db=-16.0)
    x = events(0.16, [(0.0, click(r, 3000, 1.5), 0.6), (0.004, blip(1175, 0.06, 0.018), 0.8), (0.03, click(r, 4200, 2.0), 0.35)])
    out(UI + "toggle.wav", reverb(x, IR_UI, wet=0.1), rms_db=-15.0)
    x = events(0.06, [(0.0, blip(2600, 0.04, 0.006, harm=0.1), 1.0), (0.0, click(r, 5000), 0.2)])
    out(UI + "slider-tick.wav", x, rms_db=-19.0, fout=0.005)
    m = ns(0.09)
    bz = lp(square(233.1, m) + 0.7 * square(246.9, m), 1800) * env_pts(m, [(0, 0), (0.004, 1), (0.07, 0.8), (0.09, 0)])
    x = events(0.32, [(0.0, bz, 1.0), (0.13, bz, 1.0)])
    out(UI + "error.wav", reverb(x, IR_UI, wet=0.1), rms_db=-14.0)


def feedback():
    for v in range(3):
        r = rng(5100 + v)
        p = [1.0, 1.06, 0.95][v]
        m = ns(0.14)
        ping = (sine(2900 * p, m) + 0.5 * sine(4350 * p, m) + 0.2 * sine(6100 * p, m)) * env_exp(m, 0.03, 0.0005)
        x = events(0.16, [(0.0, hp(burst(r, 0.01, 0.0007, 0.00005), 3000), 0.7), (0.0, ping, 0.8)])
        out(FB + f"hit-marker-{v + 1:02d}.wav", x, rms_db=-16.0, fout=0.01)

    r = rng(5110)
    sw = whoosh(r, 0.18, 1500, 6000, q=0.8, peak=0.9)
    x = events(1.3, [(0.0, sw, 0.25), (0.16, thud(r, 90, 0.07), 0.8), (0.16, bell(1174.7, 1.0, 0.25), 0.6),
                     (0.19, bell(1760, 1.0, 0.28), 0.5), (0.22, bell(2349.3, 1.0, 0.3), 0.45)])
    out(FB + "elimination-confirm.wav", reverb(x, IR_UI, wet=0.22), rms_db=-14.0)

    r = rng(5120)
    n = ns(1.4)
    shards = np.zeros(n)
    for i in range(26):
        t0 = r.exponential(0.07)
        place(shards, glass_hit(r, r.uniform(2400, 7200), r.uniform(0.04, 0.18)), ns(min(t0, 0.5)), r.uniform(0.3, 1.0))
    m = ns(0.35)
    fz = np.geomspace(3200, 260, m)
    zap = fm(fz, fz * 1.5, 3 * env_exp(m, 0.08), m) * env_exp(m, 0.1, 0.001)
    crk = filt(crackle(ns(0.3), r, 4000, 0.0003), [("hp", 2000)]) * env_exp(ns(0.3), 0.05)
    x = 0.6 * norm(shards) + pad_to(0.5 * zap, n) + pad_to(0.4 * norm(crk), n) + pad_to(0.6 * thud(r, 80, 0.08), n)
    out(FB + "shield-break.wav", reverb(x, IR_UI, wet=0.2), rms_db=-13.0)

    # low health: heartbeat loop, 1.6 s (75 bpm), circular
    r = rng(5130)
    n = ns(1.6)
    x = np.zeros(n)
    place(x, lp(thud(r, 55, 0.07, drop=1.3, noise_lp=250, noise_amt=0.3), 300), 0, 1.0, wrap=True)
    place(x, lp(thud(r, 66, 0.06, drop=1.3, noise_lp=250, noise_amt=0.3), 300), ns(0.27), 0.7, wrap=True)
    ring = np.sin(TAU * qfreq(3900, n) * tvec(n)) * 0.004
    out(FB + "low-health-loop.wav", x + ring, loop=True, rms_db=-24.0)

    r = rng(5140)
    x = events(0.3, [(0.0, rustle(r, 0.15, 500, 6000), 0.25), (0.02, blip(987.8, 0.08, 0.025), 0.8),
                     (0.07, blip(1480, 0.12, 0.04), 0.8)])
    out(FB + "pickup.wav", reverb(x, IR_UI, wet=0.12), rms_db=-15.0)

    m = ns(0.09)
    tone = lambda f: lp(square(f, m), 900) * env_pts(m, [(0, 0), (0.004, 1), (0.08, 0.5), (0.09, 0)])
    x = events(0.32, [(0.0, tone(196), 1.0), (0.12, tone(164.8), 1.0)])
    out(FB + "inventory-full.wav", reverb(x, IR_UI, wet=0.1), rms_db=-15.0)

    r = rng(5150)
    n = ns(2.6)
    t = tvec(n)
    x = np.zeros(n)
    for i, t0 in enumerate([0.0, 0.45, 0.9]):
        m = ns(0.36)
        tm = tvec(m)
        dy = (saw(440, m) + saw(466.2, m) + 0.6 * saw(220, m)) * (1 + 0.3 * np.sin(TAU * 14 * tm))
        dy = lp(dy, 2200) * env_pts(m, [(0, 0), (0.01, 1), (0.28, 0.7), (0.36, 0)])
        place(x, dy, ns(t0), 0.5 + 0.15 * i)
    rumble = lp(white(n, r), 160, order=2) * env_pts(n, [(0, 0), (1.2, 1), (2.6, 0)])
    rise = saw(np.geomspace(55, 110, n), n) * env_pts(n, [(0, 0), (1.3, 0.6), (2.6, 0)])
    x += 0.5 * norm(rumble) + 0.2 * lp(rise, 600)
    out(FB + "storm-warning.wav", reverb(x, IR_UI, wet=0.25), rms_db=-15.0, fout=0.4)


# ---------------------------------------------------------------- footsteps
def grit(r, dur, density, lo, hi, tau):
    m = ns(dur)
    g = crackle(m, r, density, 0.0003)[:m]
    return norm(filt(g, [("hp", lo), ("lp", hi)]) * env_exp(m, tau, 0.002))


def step(surface, r, p):
    toe = r.uniform(0.035, 0.06)
    if surface == "basalt":
        ev = [(0.0, thud(r, 110 * p, 0.018, noise_lp=2200, noise_amt=0.9), 0.7),
              (0.0, grit(r, 0.12, 3000, 1500, 7000, 0.02), 0.6),
              (toe, thud(r, 140 * p, 0.012, noise_lp=2500, noise_amt=0.9), 0.3),
              (toe, grit(r, 0.1, 2500, 2000, 8000, 0.015), 0.3),
              (toe + 0.01, scrape(r, 0.07, 1500, 6000, 1500), 0.15)]
    elif surface == "grass":
        swish = band(ns(0.15), r, 2000, 8000) * env_exp(ns(0.15), 0.04, 0.01)
        ev = [(0.0, thud(r, 85 * p, 0.022, noise_lp=700), 0.5), (0.0, grit(r, 0.18, 7000, 1500, 9000, 0.05), 0.8),
              (0.005, swish, 0.35), (toe, grit(r, 0.14, 6000, 2000, 9000, 0.04), 0.6)]
    elif surface == "metal":
        ev = [(0.0, thud(r, 130 * p, 0.02, noise_lp=1800), 0.7), (0.0, metal_hit(r, 520 * p, 0.08, bright=0.6, modes=7), 0.6),
              (toe, metal_hit(r, 720 * p, 0.05, bright=0.6, modes=6), 0.28), (toe, thud(r, 160, 0.012), 0.16),
              (0.004, rattle(r, 0.12, 2, 900, 0.02), 0.12)]
    elif surface == "glass":
        ev = [(0.0, hp(burst(r, 0.02, 0.0012), 1500), 0.6), (0.0, glass_hit(r, 3800 * p, 0.05), 0.5),
              (0.0, thud(r, 120, 0.015, noise_lp=2500), 0.4),
              (0.002, grit(r, 0.06, 2000, 3000, 10000, 0.015), 0.35),
              (toe, glass_hit(r, 4600 * p, 0.03), 0.27), (toe, grit(r, 0.06, 2500, 3000, 10000, 0.012), 0.24)]
    else:  # shallow water
        m = ns(0.35)
        splash = band(m, r, 400, 6500) * env_exp(m, 0.06, 0.004)
        slosh = band(m, r, 150, 1200) * env_pts(m, [(0, 0), (0.03, 1), (0.35, 0)]) ** 2
        bub = np.zeros(m)
        for _ in range(int(r.integers(6, 11))):
            d = r.uniform(0.008, 0.02)
            k = ns(d * 5)
            fr = r.uniform(700, 2400) * (1 + 0.9 * tvec(k) / (d * 5))
            place(bub, sine(fr, k) * env_exp(k, d, 0.0008), ns(r.uniform(0.02, 0.22)), r.uniform(0.3, 1.0))
        heel = 0.8 * splash + 0.5 * slosh + 0.3 * norm(bub) + pad_to(0.3 * thud(r, 80 * p, 0.02), m)
        ev = [(0.0, heel, 1.0), (toe, 0.5 * band(ns(0.12), r, 800, 6000) * env_exp(ns(0.12), 0.03, 0.003), 0.5)]
    return events(0.45, ev)


def foley():
    for si, s in enumerate(["basalt", "grass", "metal", "glass", "shallow-water"]):
        for v in range(4):
            r = rng(5200 + si * 10 + v)
            x = step(s, r, [1.0, 0.94, 1.06, 0.98][v])
            out(FOLEY + f"{s}-{v + 1:02d}.wav", reverb(x, ir("small"), wet=0.08), rms_db=-17.0, fout=0.02)
    r = rng(5300)
    x = events(0.6, [(0.0, rustle(r, 0.4, 200, 4000), 0.6), (0.02, scrape(r, 0.06, 1200, 6000, 1500), 0.5),
                     (0.03, thud(r, 140, 0.015, noise_lp=1800), 0.5), (0.08, rattle(r, 0.25, 4, 2200), 0.15)])
    out(FOLEY + "jump.wav", reverb(x, ir("small"), wet=0.08), rms_db=-18.0)
    r = rng(5301)
    x = events(0.9, [(0.0, thud(r, 72, 0.08, noise_lp=600), 1.0), (0.0, grit(r, 0.3, 4000, 500, 6000, 0.06), 0.5),
                     (0.06, thud(r, 100, 0.03, noise_lp=1200), 0.4), (0.005, rattle(r, 0.35, 5, 1900), 0.2),
                     (0.0, rustle(r, 0.4, 200, 3500), 0.4)])
    out(FOLEY + "land.wav", reverb(x, ir("small"), wet=0.1), rms_db=-14.0)


def main():
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if not args or "ui" in args:
        ui()
    if not args or "feedback" in args:
        feedback()
    if not args or "foley" in args:
        foley()


if __name__ == "__main__":
    main()
