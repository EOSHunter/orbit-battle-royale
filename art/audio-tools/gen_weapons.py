"""Weapon audio: fire-close (3 variations), fire-distant, reload, equip, dry-fire for each weapon.

Output: game/assets/audio/weapon-audio/<weapon>-audio/*.wav (48 kHz mono 16-bit).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sfx import *  # noqa: E402,F403
import numpy as np  # noqa: E402
from synth import out, saturate, svf, sine, fm, env_exp, ns, tvec, rng, pad_to  # noqa: E402

# Per-weapon voice. body: pitch-dropping low end; blast: muzzle noise; crack: supersonic snap;
# mech: action cycling; zap: energy layer (Spark / Wisp are hybrid "coil" weapons).
WEAPONS = {
    "ar-7-wayfarer": dict(body_hi=170, body_lo=58, body_tau=0.075, blast_tau=0.05, blast_lp=1400,
                          crack=0.9, mech_f=2100, mech_t=0.045, mech=0.22, zap=0.0, sub=0.4,
                          t60_wet=0.28, length=1.3, drive=2.2),
    "sg-4-breaker": dict(body_hi=130, body_lo=44, body_tau=0.14, blast_tau=0.09, blast_lp=1000,
                         crack=0.7, mech_f=1500, mech_t=0.07, mech=0.12, zap=0.0, sub=0.8,
                         t60_wet=0.34, length=1.7, drive=2.8, pellets=True),
    "p-12-spark": dict(body_hi=240, body_lo=90, body_tau=0.045, blast_tau=0.03, blast_lp=2000,
                       crack=0.8, mech_f=2700, mech_t=0.03, mech=0.3, zap=0.45, sub=0.15,
                       t60_wet=0.24, length=1.0, drive=1.8),
    "s-9-wisp": dict(body_hi=210, body_lo=80, body_tau=0.04, blast_tau=0.028, blast_lp=2400,
                     crack=0.85, mech_f=3000, mech_t=0.028, mech=0.28, zap=0.3, sub=0.15,
                     t60_wet=0.22, length=0.85, drive=2.0),
    "sr-8-longview": dict(body_hi=120, body_lo=36, body_tau=0.2, blast_tau=0.11, blast_lp=1100,
                          crack=1.0, mech_f=1700, mech_t=0.09, mech=0.12, zap=0.0, sub=1.0,
                          t60_wet=0.4, length=2.6, drive=2.6),
}


def shot_layers(r, p, pitch=1.0):
    n = ns(0.6)
    t = tvec(n)
    L = {}
    # supersonic crack / muzzle snap
    c = hp(burst(r, 0.02, 0.0016 * (1.6 if p.get("pellets") else 1.0), 0.00008), 1800, order=2)
    if p.get("pellets"):
        for _ in range(6):
            place(c, hp(burst(r, 0.006, 0.0006), 2500) * 0.5, ns(r.uniform(0.0005, 0.006)))
    L["crack"] = norm(pad_to(c, n))
    # muzzle blast: noise through a closing lowpass
    fc = p["blast_lp"] + 9000 * np.exp(-t / 0.012)
    b = svf(white(n, r), fc, 0.8, "lp") * env_exp(n, p["blast_tau"], 0.0004)
    L["blast"] = saturate(norm(b) * 2.0, 2.0)
    # body: pitch-dropping sine, saturated
    fr = pitch * (p["body_lo"] + (p["body_hi"] - p["body_lo"]) * np.exp(-t / 0.018))
    body = sine(fr, n) * env_exp(n, p["body_tau"], 0.0007)
    L["body"] = saturate(norm(body) * 1.8, 2.0)
    # sub kick for heavy weapons
    sub = sine(pitch * 48 * (1 + 0.6 * np.exp(-t / 0.03)), n) * env_exp(n, p["body_tau"] * 1.4, 0.002)
    L["sub"] = norm(sub)
    # mechanical action
    m = np.zeros(n)
    place(m, metal_hit(r, p["mech_f"] * pitch, 0.02, modes=6), ns(p["mech_t"]), 1.0)
    place(m, metal_hit(r, p["mech_f"] * 0.72 * pitch, 0.025, modes=5), ns(p["mech_t"] + 0.028), 0.7)
    place(m, click(r, 4200), ns(p["mech_t"] - 0.002), 0.5)
    L["mech"] = norm(m)
    # energy layer: falling FM zap plus a coil ring
    if p["zap"] > 0:
        fz = pitch * np.geomspace(5200, 700, ns(0.05))
        z = fm(fz, fz * 1.41, 2.5 * env_exp(ns(0.05), 0.015), ns(0.05)) * env_exp(ns(0.05), 0.012, 0.0003)
        ring = sine(pitch * 1870, ns(0.25)) * env_exp(ns(0.25), 0.05) * 0.3
        zz = np.zeros(n)
        place(zz, z, 0)
        place(zz, ring, ns(0.002))
        L["zap"] = norm(zz)
    return L


def fire_close(r, p, pitch):
    L = shot_layers(r, p, pitch)
    dry = (p["crack"] * L["crack"] + 1.0 * L["blast"] + 0.9 * L["body"] + p["sub"] * L["sub"] * 0.6
           + p["mech"] * L["mech"] + p["zap"] * L.get("zap", 0))
    dry = saturate(norm(dry) * p["drive"], p["drive"] * 0.8)
    wet = outdoor_tail(dry, wet=p["t60_wet"])
    return wet[: ns(p["length"])]


def fire_distant(r, p):
    L = shot_layers(r, p, 0.97)
    dry = 0.25 * L["crack"] + 1.0 * L["blast"] + 1.0 * L["body"] + p["sub"] * L["sub"] * 0.5
    dry = lp(dry, 900, order=2)
    if p["crack"] >= 1.0:  # the sniper's supersonic snap still carries
        dry += 0.35 * lp(L["crack"], 3500)
    y = reverb(dry, ir("outdoor_long"), wet=1.1, dry=0.5)
    y = echoes(y, [0.38, 0.85, 1.5], [0.4, 0.25, 0.12], [900, 700, 500], extra=1.0)
    y = lp(y, 1600, order=1)
    return y[: ns(p["length"] + 1.8)]


# ---------------------------------------------------------------- handling foley
def mag_out(r, pitch=1.0):
    return events(0.4, [(0.0, click(r, 3600), 0.5), (0.005, metal_hit(r, 2300 * pitch, 0.015, modes=5), 0.5),
                        (0.04, scrape(r, 0.13, 1500, 6000), 0.45),
                        (0.2, thud(r, 240 * pitch, 0.025, noise_lp=1500), 0.35)])


def mag_in(r, pitch=1.0, slide=0.08):
    return events(0.4, [(0.0, scrape(r, slide, 1200, 6000), 0.4),
                        (slide, metal_hit(r, 1400 * pitch, 0.03), 0.9),
                        (slide, thud(r, 160 * pitch, 0.03, noise_lp=1800), 0.9),
                        (slide + 0.001, click(r, 3000), 0.6)])


def bolt(r, pitch=1.0, slam=1.0):
    back = events(0.25, [(0.0, scrape(r, 0.1, 1500, 7000), 0.5), (0.1, metal_hit(r, 2600 * pitch, 0.018), 0.55),
                         (0.1, click(r, 4500), 0.4)])
    fwd = events(0.35, [(0.0, metal_hit(r, 1100 * pitch, 0.05), 1.0 * slam), (0.0, thud(r, 130 * pitch, 0.03), 0.8 * slam),
                        (0.0, click(r, 3200), 0.7 * slam), (0.03, rattle(r, 0.2, 3, 2600), 0.2)])
    return back, fwd


def shell_insert(r):
    return events(0.3, [(0.0, scrape(r, 0.05, 900, 5000), 0.35), (0.05, metal_hit(r, 3100, 0.012, modes=4), 0.45),
                        (0.05, thud(r, 320, 0.02, noise_lp=2500), 0.7), (0.06, rattle(r, 0.15, 2, 3500), 0.12)])


def charge_whine(r, dur=0.35, f0=500, f1=2600):
    n = ns(dur)
    fr = np.geomspace(f0, f1, n)
    x = (sine(fr, n) + 0.35 * sine(fr * 2.01, n)) * np.sin(np.pi * tvec(n) / dur) ** 1.5
    return norm(x)


def reload_seq(r, w):
    ev = []
    if w == "ar-7-wayfarer":
        b, f = bolt(r)
        ev = [(0.02, rustle(r, 0.3), 0.25), (0.22, mag_out(r), 1.0), (0.95, rustle(r, 0.25), 0.2),
              (1.0, mag_in(r), 1.0), (1.5, b, 1.0), (1.72, f, 1.0)]
        total = 2.3
    elif w == "sg-4-breaker":
        ev = [(0.02, rustle(r, 0.3), 0.25)]
        for i, t0 in enumerate([0.3, 0.72, 1.14]):
            ev.append((t0, shell_insert(rng(900 + i)), 1.0))
        back = events(0.3, [(0.0, scrape(r, 0.12, 800, 5000), 0.6), (0.12, metal_hit(r, 950, 0.04), 0.9),
                            (0.12, thud(r, 150, 0.03), 0.7)])
        fwd = events(0.4, [(0.0, scrape(r, 0.09, 800, 5000), 0.5), (0.09, metal_hit(r, 780, 0.06), 1.0),
                           (0.09, thud(r, 120, 0.04), 1.0), (0.1, rattle(r, 0.2, 3, 2000), 0.2)])
        ev += [(1.7, back, 1.0), (1.95, fwd, 1.0)]
        total = 2.6
    elif w == "p-12-spark":
        ev = [(0.02, rustle(r, 0.2), 0.2), (0.12, mag_out(r, 1.2), 1.0), (0.7, mag_in(r, 1.2, 0.06), 0.9),
              (1.1, metal_hit(r, 2100, 0.03), 0.9), (1.1, click(r, 4000), 0.6),
              (1.13, charge_whine(r, 0.3, 700, 2900), 0.22)]
        total = 1.7
    elif w == "s-9-wisp":
        b, f = bolt(r, 1.2, 1.2)
        ev = [(0.02, rustle(r, 0.2), 0.2), (0.15, mag_out(r, 1.15), 1.0), (0.8, mag_in(r, 1.15, 0.06), 1.0),
              (1.2, b, 0.8), (1.36, f, 1.0), (1.4, charge_whine(r, 0.28, 900, 3300), 0.15)]
        total = 1.9
    else:  # sr-8-longview bolt action
        up = events(0.2, [(0.0, click(r, 2800), 0.7), (0.0, metal_hit(r, 1900, 0.02), 0.6)])
        back = events(0.3, [(0.0, scrape(r, 0.16, 1200, 6000), 0.6), (0.16, metal_hit(r, 1500, 0.04), 0.9)])
        fwd = events(0.3, [(0.0, scrape(r, 0.14, 1200, 6000), 0.55), (0.14, metal_hit(r, 1250, 0.04), 0.9),
                           (0.14, thud(r, 140, 0.03), 0.6)])
        down = events(0.3, [(0.0, metal_hit(r, 1050, 0.05), 1.0), (0.0, thud(r, 120, 0.03), 0.9),
                            (0.0, click(r, 3000), 0.6)])
        ev = [(0.02, rustle(r, 0.3), 0.2), (0.2, up, 1.0), (0.32, back, 1.0), (0.75, mag_out(r, 0.9), 1.0),
              (1.5, mag_in(r, 0.9, 0.1), 1.0), (2.15, fwd, 1.0), (2.45, down, 1.0)]
        total = 3.0
    x = events(total, ev)
    return reverb(x, ir("small"), wet=0.12)


def equip(r, w, energy):
    ev = [(0.0, rustle(r, 0.32, 250, 4500), 0.6), (0.11, thud(r, 180, 0.03, noise_lp=1500), 0.5),
          (0.16, rattle(r, 0.25, 4, 2400), 0.3), (0.32, metal_hit(r, 1900, 0.025), 0.55), (0.32, click(r, 3800), 0.5)]
    if energy:
        ev.append((0.34, charge_whine(r, 0.25, 900, 3400), 0.2))
    return reverb(events(0.75, ev), ir("small"), wet=0.12)


def dry_fire(r, energy):
    ev = [(0.0, click(r, 4500, 3.0), 0.5), (0.012, metal_hit(r, 2500, 0.014, modes=5), 0.9),
          (0.012, thud(r, 420, 0.012, noise_lp=3000), 0.5)]
    if energy:
        n = ns(0.12)
        blip = sine(np.geomspace(900, 380, n), n) * env_exp(n, 0.04, 0.002)
        ev.append((0.03, blip, 0.12))
    return reverb(events(0.3, ev), ir("small"), wet=0.1)


def main():
    only = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    for wi, (w, p) in enumerate(WEAPONS.items()):
        if only and w not in only:
            continue
        d = f"weapon-audio/{w}-audio/"
        energy = p["zap"] > 0
        for v in range(3):
            r = rng(1000 + wi * 10 + v)
            pitch = [1.0, 0.965, 1.035][v]
            out(d + f"fire-close-{v + 1:02d}.wav", fire_close(r, p, pitch), rms_db=-8.0)
        out(d + "fire-distant.wav", fire_distant(rng(1100 + wi), p), rms_db=-12.0, fout=0.3)
        out(d + "reload.wav", reload_seq(rng(1200 + wi), w), rms_db=-17.0)
        out(d + "equip.wav", equip(rng(1300 + wi), w, energy), rms_db=-18.0)
        out(d + "dry-fire.wav", dry_fire(rng(1400 + wi), energy), rms_db=-19.0)


if __name__ == "__main__":
    main()
