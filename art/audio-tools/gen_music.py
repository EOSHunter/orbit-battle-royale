"""Music: main-menu theme loop (stereo, 64 s, D major, 90 BPM) and five match stingers (stereo).

The theme is rendered circularly: every note is placed modulo the loop length (release tails, delays and
the stereo hall reverb wrap from the end back to the start), so the loop is seamless by construction.
Usage: python gen_music.py [-- theme|stingers]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sfx import *  # noqa: E402,F403
import numpy as np  # noqa: E402
from synth import (out, ns, tvec, rng, spec_filter, g_lp, g_hp, g_bp, g_mul, g_peak, white, colored, sine,  # noqa: E402
                   saw, square, tri, fm, place, norm, svf, env_exp, env_pts, reverb, pad_to, saturate,
                   midi, make_ir, TAU, SR, fade)

BPM = 90.0
BEAT = 60.0 / BPM
BAR = 4 * BEAT
THEME = "music/main-menu-theme/"
STING = "music/match-stingers/"

HALL = make_ir(t60=4.5, predelay=0.035, bright=0.6, early=10, early_span=0.08, seed=61, stereo_out=True)

# note names -> midi
NOTE = {"C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3, "E": 4, "F": 5, "F#": 6, "Gb": 6, "G": 7,
        "G#": 8, "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11}


def nm(s):
    name, octv = s[:-1], int(s[-1])
    return 12 * (octv + 1) + NOTE[name]


def hz(s):
    return midi(nm(s))


# chords: (bass, pad voicing, arp tones)
CHORDS = [
    ("D2", ["A3", "C#4", "E4", "F#4"], ["D4", "F#4", "A4", "C#5", "E5", "F#5"]),
    ("B1", ["F#3", "B3", "C#4", "D4"], ["B3", "D4", "F#4", "A4", "C#5", "D5"]),
    ("G1", ["B3", "C#4", "D4", "F#4"], ["G3", "B3", "D4", "F#4", "A4", "C#5"]),
    ("A1", ["E3", "A3", "B3", "E4"], ["A3", "C#4", "E4", "B4", "C#5", "E5"]),
]


# ---------------------------------------------------------------- instruments
def pad_note(f, dur, r, attack=1.2, release=1.8, det=9.0):
    n = ns(dur + release)
    env = env_pts(n, [(0, 0), (attack, 1), (dur, 0.85), (dur + release, 0)]) ** 1.5
    chans = []
    for c in range(2):
        cents = [-det, det * 0.35] if c == 0 else [-det * 0.4, det]
        x = sum(saw(f * 2 ** (ct / 1200.0), n, r.random()) for ct in cents)
        x += 0.5 * sine(f * 0.5 if f > 200 else f, n, r.random())
        chans.append(x * env)
    return np.stack(chans, axis=1)


def pluck(f, dur=0.6, tau=0.22, index=2.2, bright=1.0):
    n = ns(dur)
    x = 0.6 * fm(f, f, bright * index * env_exp(n, 0.06), n) + 0.4 * tri(f, n)
    return x * env_exp(n, tau, 0.003)


def bellv(f, dur=3.0, tau=0.9, ratio=3.5, index=1.6):
    n = ns(dur)
    x = fm(f, f * ratio, index * env_exp(n, tau * 0.25), n) + 0.3 * sine(f * 2.0, n) * env_exp(n, tau * 0.4)
    return x * env_exp(n, tau, 0.004)


def bass_note(f, dur, release=0.6):
    n = ns(dur + release)
    env = env_pts(n, [(0, 0), (0.25, 1), (dur, 0.9), (dur + release, 0)])
    return (sine(f, n) + 0.25 * sine(f * 2, n) + 0.08 * tri(f * 3, n)) * env


def kick(r, f=55.0):
    n = ns(0.5)
    fr = f * (1 + 1.5 * env_exp(n, 0.02))
    return sine(fr, n) * env_exp(n, 0.12, 0.002)


def place_st(dst, src, start, gain=1.0, pan=0.0, wrap=True):
    if src.ndim == 1:
        a = (pan + 1) * np.pi / 4
        src = np.stack([src * np.cos(a), src * np.sin(a)], axis=1)
    place(dst, src, start, gain, wrap=wrap)


# ---------------------------------------------------------------- theme
def theme():
    r = rng(6001)
    bars = 24
    n = ns(bars * BAR)
    pad = np.zeros((n, 2))
    bass = np.zeros((n, 2))
    arp = np.zeros((n, 2))
    bells = np.zeros((n, 2))
    perc = np.zeros((n, 2))
    for ci in range(bars // 2):
        b, voices, tones = CHORDS[ci % 4]
        t0 = ci * 2 * BAR
        for v in voices:
            place_st(pad, pad_note(hz(v), 2 * BAR, r), ns(t0), 0.22)
        place_st(bass, bass_note(hz(b), 2 * BAR - 0.2), ns(t0), 0.9)
        if ci >= 4:  # arp from bar 9
            pattern = [0, 2, 4, 5, 3, 1, 4, 2]
            for s in range(32):  # 16ths over 2 bars
                k = pattern[s % 8] + (1 if (s // 8) % 2 and pattern[s % 8] < 5 else 0)
                f = hz(tones[min(k, 5)])
                acc = 1.0 if s % 4 == 0 else (0.7 if s % 2 == 0 else 0.5)
                if ci >= 8:
                    acc *= 1.1
                pan = 0.35 * np.sin(s * 0.7)
                place_st(arp, pluck(f, bright=0.8 + 0.4 * (ci >= 8)), ns(t0 + s * BEAT / 4), 0.16 * acc, pan)
        if ci >= 8:  # pulse + shaker from bar 17
            for bt in range(8):
                place_st(perc, kick(r), ns(t0 + bt * BEAT), 0.5)
                sh = hp(white(ns(0.06), r), 6000) * env_exp(ns(0.06), 0.012, 0.002)
                place_st(perc, sh, ns(t0 + bt * BEAT + BEAT / 2), 0.12, 0.3)
    # bell melody over the last 8 bars (D major, gentle)
    mel = [("F#5", 0, 2), ("E5", 2, 1), ("D5", 3, 1), ("A5", 4, 3), ("F#5", 7, 1),
           ("D5", 8, 2), ("E5", 10, 1), ("F#5", 11, 1), ("B5", 12, 3), ("A5", 15, 1),
           ("G5", 16, 2), ("F#5", 18, 1), ("E5", 19, 1), ("D5", 20, 2), ("E5", 22, 2),
           ("C#5", 24, 2), ("E5", 26, 2), ("A5", 28, 4)]
    start = 16 * BAR
    for i, (nt, b0, ln) in enumerate(mel):
        place_st(bells, bellv(hz(nt), dur=3.5, tau=0.8 + 0.2 * ln), ns(start + b0 * BEAT), 0.3, 0.25 * np.sin(i))
    # sparse high sparkle in bars 1-8 so the opening is not empty
    for i, (nt, bt) in enumerate([("A5", 2), ("F#5", 6), ("E6", 11), ("C#6", 15), ("D6", 20), ("B5", 26), ("A5", 29)]):
        place_st(bells, bellv(hz(nt), dur=3.5, tau=1.2, index=0.8), ns(bt * BEAT), 0.16, -0.4 + 0.12 * i)

    # pad: tone filter, gentle sidechain pump in the pulse section
    pad = spec_filter(pad, g_mul(g_lp(1900, 2), g_hp(90, 1)))
    t = tvec(n)
    beatph = (t / BEAT) % 1.0
    pump = 1 - 0.3 * np.exp(-beatph / 0.18) * (t >= 16 * BAR)
    pad *= pump[:, None]
    # ping-pong delay on the arp (dotted eighth), circular
    dly = ns(0.75 * BEAT)
    tap1 = np.roll(spec_filter(arp, g_lp(3500, 1)), dly, axis=0)
    tap2 = np.roll(spec_filter(arp, g_lp(2500, 1)), 2 * dly, axis=0)
    arp = arp + 0.35 * tap1[:, ::-1] + 0.2 * tap2
    # air texture
    air = np.stack([spec_filter(colored(n, r, -1), g_bp(3000, 9000, 2)) for _ in range(2)], axis=1)
    air *= (0.5 + 0.5 * np.sin(TAU * t / (8 * BAR)))[:, None] ** 2
    air = 0.012 * air / np.max(np.abs(air))
    bus = pad + arp + bells
    wet = reverb(bus, HALL, wet=1.0, dry=0.0, circular=True)
    mixd = 0.8 * bus + 0.45 * wet + 0.55 * bass + perc + air
    out(THEME + "main-menu-theme-loop.wav", mixd, loop=True, rms_db=-18.0)


# ---------------------------------------------------------------- stingers
def chord_st(notes, dur, r, release=2.5, gain=0.2, attack=0.02):
    n = ns(dur + release)
    x = np.zeros((n, 2))
    for v in notes:
        place_st(x, pad_note(hz(v), dur, r, attack=attack, release=release), 0, gain, wrap=False)
    return x


def brass(notes, dur, r, release=0.5, gain=0.2):
    """Brass-like stab: detuned saws through a lowpass with a filter envelope."""
    n = ns(dur + release)
    env = env_pts(n, [(0, 0), (0.03, 1), (dur, 0.8), (dur + release, 0)])
    fc = 400 + 3200 * env_pts(n, [(0, 0), (0.06, 1), (0.4, 0.5), (dur + release, 0.3)])
    chans = []
    for c in range(2):
        s = sum(saw(hz(v) * 2 ** ((c * 2 - 1) * 6 / 1200), n, r.random()) for v in notes)
        chans.append(svf(s, fc, 0.9, "lp") * env)
    return np.stack(chans, axis=1) * gain


def finish(x, wet=0.4):
    return reverb(x, HALL, wet=wet, dry=1.0)


def stingers():
    # drop start: riser into a bright D major hit
    r = rng(6101)
    total = ns(7.5)
    x = np.zeros((total, 2))
    rn = ns(2.6)
    riser = svf(white(rn, r), np.geomspace(300, 7000, rn), 1.2, "bp") * np.linspace(0, 1, rn) ** 2
    place_st(x, riser, 0, 0.35, wrap=False)
    seq = ["D4", "E4", "F#4", "A4", "B4", "D5", "E5", "F#5", "A5", "B5", "D6", "E6", "F#6", "A6"]
    tt = 0.0
    for i, nt in enumerate(seq):
        place_st(x, pluck(hz(nt), 0.5, 0.15), ns(tt), 0.25, 0.4 * np.sin(i), wrap=False)
        tt += 0.26 * (0.9 ** i)
    hit = ns(2.6)
    place_st(x, chord_st(["D3", "A3", "D4", "F#4", "A4", "E5"], 0.8, r, release=3.5, gain=0.18), hit, 1.0, wrap=False)
    place_st(x, kick(r, 45) * 1.2, hit, 0.9, wrap=False)
    place_st(x, thud(r, 50, 0.5, dur=2.0), hit, 0.5, wrap=False)
    for i, nt in enumerate(["D6", "A6", "F#6"]):
        place_st(x, bellv(hz(nt), 3.5, 1.0), hit + ns(0.08 * i), 0.22, -0.3 + 0.3 * i, wrap=False)
    cym = hp(white(ns(3.0), r), 5000) * env_exp(ns(3.0), 0.7, 0.003)
    place_st(x, cym, hit, 0.15, wrap=False)
    out(STING + "drop-start.wav", finish(x)[: ns(6.5)], rms_db=-14.0, fout=0.6)

    # storm closing: dissonant low drone, accelerating ticks, falling tone
    r = rng(6102)
    total = ns(6.0)
    x = np.zeros((total, 2))
    dn = ns(5.0)
    drone = sum(saw(hz(v), dn, r.random()) for v in ["D2", "Eb2", "A2"])
    drone = lp(drone, 700) * env_pts(dn, [(0, 0), (1.2, 1), (3.8, 0.9), (5.0, 0)])
    place_st(x, drone, 0, 0.25, -0.2, wrap=False)
    gl = ns(3.5)
    fall = sine(np.geomspace(hz("A4"), hz("D4"), gl), gl) * env_pts(gl, [(0, 0), (0.3, 1), (3.5, 0)])
    place_st(x, fall, ns(0.5), 0.25, 0.3, wrap=False)
    tt, step_ = 0.2, 0.42
    while tt < 4.2:
        tick = blip_tick(r) + 0.6 * pad_to(click(r, 1800, 4.0), ns(0.05))
        place_st(x, tick, ns(tt), 0.35, 0.2, wrap=False)
        tt += step_
        step_ *= 0.9
    place_st(x, thud(r, 48, 0.6, dur=2.5), 0, 0.6, wrap=False)
    out(STING + "storm-closing.wav", finish(x, 0.45)[: ns(6.0)], rms_db=-15.0, fout=0.6)

    # final survivors: taiko-like pattern under a suspended chord resolving to D
    r = rng(6103)
    total = ns(7.0)
    x = np.zeros((total, 2))
    for tt, g in [(0.0, 1.0), (0.667, 0.7), (1.333, 0.9), (1.833, 0.6), (2.333, 1.0), (2.667, 0.8), (3.0, 1.0)]:
        drum = thud(r, 68, 0.25, drop=1.8, noise_lp=900, noise_amt=0.7, dur=1.0)
        place_st(x, drum, ns(tt), 0.55 * g, wrap=False)
    place_st(x, chord_st(["D3", "G3", "A3", "D4", "G4"], 3.0, r, release=0.4, gain=0.12, attack=1.5), 0, 1.0, wrap=False)
    place_st(x, chord_st(["D3", "F#3", "A3", "D4", "F#4", "A4"], 0.6, r, release=3.0, gain=0.14, attack=0.05), ns(3.0), 1.0, wrap=False)
    place_st(x, brass(["D4", "A4", "D5"], 0.5, r, release=1.5, gain=0.15), ns(3.0), 1.0, wrap=False)
    place_st(x, kick(r, 45), ns(3.0), 0.8, wrap=False)
    out(STING + "final-survivors.wav", finish(x)[: ns(7.0)], rms_db=-14.0, fout=0.6)

    # victory: brass fanfare D - G - A - D with timpani, bells and a cymbal swell
    r = rng(6104)
    total = ns(8.0)
    x = np.zeros((total, 2))
    hits = [(0.0, ["D3", "A3", "D4", "F#4", "A4"], 0.25), (0.333, ["D3", "B3", "D4", "G4", "B4"], 0.25),
            (0.667, ["E3", "A3", "C#4", "E4", "C#5"], 0.25), (1.0, ["D3", "A3", "D4", "F#4", "A4", "D5"], 2.2),
            (3.3, ["G2", "B3", "D4", "G4", "B4"], 0.6), (4.0, ["D3", "A3", "D4", "F#4", "A4", "F#5"], 2.0)]
    for tt, notes, d in hits:
        place_st(x, brass(notes, d, r, release=0.8, gain=0.11), ns(tt), 1.0, wrap=False)
        place_st(x, thud(r, 62, 0.3, drop=1.5, noise_lp=700, dur=1.2), ns(tt), 0.45, wrap=False)
    for i, nt in enumerate(["D6", "F#6", "A6", "D7", "A6", "F#6"]):
        place_st(x, bellv(hz(nt), 3.0, 0.9), ns(1.0 + 0.12 * i), 0.13, -0.5 + 0.2 * i, wrap=False)
        place_st(x, bellv(hz(nt), 3.0, 1.2), ns(4.0 + 0.15 * i), 0.12, 0.5 - 0.2 * i, wrap=False)
    sw = hp(white(ns(1.2), r), 4000) * np.linspace(0, 1, ns(1.2)) ** 3
    place_st(x, sw, ns(2.8), 0.12, wrap=False)
    place_st(x, hp(white(ns(3.5), r), 5000) * env_exp(ns(3.5), 0.9, 0.003), ns(4.0), 0.15, wrap=False)
    out(STING + "victory.wav", finish(x)[: ns(7.0)], rms_db=-13.0, fout=0.8)

    # eliminated: muffled hit, falling minor melody over Bm -> G -> F#
    r = rng(6105)
    total = ns(6.0)
    x = np.zeros((total, 2))
    place_st(x, lp(thud(r, 50, 0.5, dur=2.0), 300), 0, 0.7, wrap=False)
    place_st(x, chord_st(["B2", "F#3", "B3", "D4"], 1.6, r, release=1.0, gain=0.11, attack=0.6), 0, 1.0, wrap=False)
    place_st(x, chord_st(["G2", "D3", "B3", "D4"], 1.4, r, release=1.2, gain=0.11, attack=0.6), ns(1.6), 1.0, wrap=False)
    place_st(x, chord_st(["F#2", "C#3", "A#3", "C#4"], 1.5, r, release=2.0, gain=0.11, attack=0.6), ns(3.0), 1.0, wrap=False)
    for i, (nt, tt) in enumerate([("F#5", 0.2), ("E5", 0.8), ("D5", 1.6), ("C#5", 2.4), ("B4", 3.0), ("A#4", 3.6)]):
        place_st(x, bellv(hz(nt), 2.5, 0.9, index=0.9), ns(tt), 0.18, 0.2 * np.sin(i), wrap=False)
    x = spec_filter(x, g_lp(2800, 2))
    out(STING + "eliminated.wav", finish(x, 0.5)[: ns(6.0)], rms_db=-16.0, fout=0.8)


def blip_tick(r):
    n = ns(0.05)
    return sine(1320, n) * env_exp(n, 0.012, 0.001) * 0.5


def main():
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if not args or "theme" in args:
        theme()
    if not args or "stingers" in args:
        stingers()


if __name__ == "__main__":
    main()
