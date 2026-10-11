"""Item audio: healing items, grenades and the Tethercaster.

Output: game/assets/audio/item-audio/{healing-item-audio,grenade-audio,tethercaster-audio}/ (48 kHz mono).
Loops are built circularly (periodic oscillators, circular noise / filters / reverb) so they are seamless.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sfx import *  # noqa: E402,F403
import numpy as np  # noqa: E402
from synth import (out, ns, tvec, rng, qfreq, spec_filter, g_bp, g_hp, g_lp, g_peak, g_mul,  # noqa: E402
                   crackle, colored, white, saw, sine, square, fm, place, norm, svf, env_exp, karplus,
                   make_ir, reverb, pad_to, saturate, TAU, SR)

HEAL = "item-audio/healing-item-audio/"
GREN = "item-audio/grenade-audio/"
TETH = "item-audio/tethercaster-audio/"

LOOP_RMS = -20.0
_CIRC_IR = make_ir(t60=0.35, predelay=0.003, early=6, early_span=0.02, seed=31)


# ---------------------------------------------------------------- loop helpers
def per_env(n, r, rate, floor=0.0, power=1.0):
    """Periodic random envelope in [floor, 1] (circular lowpassed noise)."""
    x = spec_filter(r.standard_normal(n), g_lp(rate, 3))
    x = (x - x.min()) / (x.max() - x.min() + 1e-12)
    return floor + (1 - floor) * x ** power


def bumps(n, times, width, wrap=True):
    """Periodic gaussian bumps at given times (seconds)."""
    t = tvec(n)
    L = n / SR
    e = np.zeros(n)
    for c in times:
        d = np.abs(t - c)
        d = np.minimum(d, L - d) if wrap else d
        e += np.exp(-0.5 * (d / width) ** 2)
    return e


def band(n, r, lo, hi, order=2):
    return norm(spec_filter(white(n, r), g_bp(lo, hi, order)))


def hum(n, f, harmonics, detune_cycles=0, r=None):
    """Periodic harmonic hum; frequencies quantised to the loop."""
    f = qfreq(f, n)
    x = np.zeros(n)
    for k, a in enumerate(harmonics, start=1):
        fk = qfreq(f * k, n)
        x += a * sine(fk, n, r.random() if r is not None else 0)
        if detune_cycles:
            x += a * 0.6 * sine(fk + detune_cycles * SR / n, n, r.random() if r is not None else 0.3)
    return norm(x)


def loop_out(rel, x, rms_db=LOOP_RMS, room=0.15):
    x = reverb(x, _CIRC_IR, wet=room, circular=True)
    return out(rel, x, loop=True, rms_db=rms_db)


# ---------------------------------------------------------------- healing
def heal_loops():
    n = ns(3.0)
    # Field Patch: fabric rustle, velcro rips, antiseptic spray puffs
    r = rng(2001)
    rust = band(n, r, 400, 5000) * per_env(n, r, 7, 0.1, 1.5)
    rips = spec_filter(crackle(n, r, 900, 0.0003, circular=True), g_bp(1500, 7000)) * per_env(n, r, 5, 0, 4)
    spray = band(n, r, 3000, 11000) * bumps(n, [0.6, 2.1], 0.12)
    out_x = 0.6 * rust + 0.5 * norm(rips) + 0.35 * spray
    loop_out(HEAL + "field-patch-use-loop.wav", out_x)

    # Trauma Kit: heavier rustle, latch clicks, long pump spray, soft tape stretch
    r = rng(2002)
    rust = band(n, r, 200, 3200) * per_env(n, r, 5, 0.15, 1.3)
    tape = spec_filter(crackle(n, r, 2500, 0.0002, circular=True), g_bp(2500, 9000)) * bumps(n, [1.2], 0.25)
    clicks = np.zeros(n)
    for t0, f in [(0.35, 2300), (1.95, 1800)]:
        place(clicks, metal_hit(r, f, 0.02, modes=5) + 0.8 * thud(r, 260, 0.02), ns(t0), 1.0, wrap=True)
    spray = band(n, r, 2000, 9000) * bumps(n, [0.9, 2.5], 0.2)
    loop_out(HEAL + "trauma-kit-use-loop.wav",
             0.7 * rust + 0.35 * norm(tape) + 0.35 * clicks + 0.3 * spray)

    # Shield Cell: electrical charging hum, small
    r = rng(2003)
    t = tvec(n)
    L = n / SR
    h = hum(n, 110, [1, 0.5, 0.35, 0.2, 0.12, 0.08], detune_cycles=1, r=r)
    trem = 1 + 0.25 * np.sin(TAU * qfreq(6, n) * t)
    shimmer = fm(qfreq(1760, n), qfreq(3, n), 1.5, n) * (0.5 + 0.5 * np.sin(TAU * t / L * 2))
    crk = spec_filter(crackle(n, r, 45, 0.0004, circular=True), g_bp(2500, 9000))
    loop_out(HEAL + "shield-cell-use-loop.wav",
             0.6 * h * trem + 0.12 * shimmer + 0.35 * norm(crk) + 0.1 * band(n, r, 4000, 12000))

    # Shield Pack: bigger, lower, swirling band layers
    r = rng(2004)
    h = hum(n, 82.5, [1, 0.6, 0.45, 0.3, 0.2, 0.12, 0.08], detune_cycles=1, r=r)
    pulse = 1 + 0.3 * np.sin(TAU * qfreq(4, n) * t)
    swirl = sum(band(n, r, f * 0.8, f * 1.25) * (0.5 + 0.5 * np.sin(TAU * (t / L * 2 + k / 3)))
                for k, f in enumerate([900, 1800, 3600]))
    crk = spec_filter(crackle(n, r, 90, 0.0005, circular=True), g_bp(2000, 9000))
    shimmer = fm(qfreq(1320, n), qfreq(4, n), 2.0, n)
    loop_out(HEAL + "shield-pack-use-loop.wav",
             0.6 * h * pulse + 0.18 * norm(swirl) + 0.4 * norm(crk) + 0.1 * shimmer)

    # Shield Core: deep, pulsing, sparkling
    r = rng(2005)
    h = hum(n, 55, [1, 0.8, 0.55, 0.4, 0.3, 0.2, 0.14, 0.1], detune_cycles=1, r=r)
    pulse = 1 + 0.45 * np.sin(TAU * qfreq(2, n) * t) ** 2
    sparkle = np.zeros(n)
    for _ in range(14):
        f = r.uniform(2400, 5200)
        m = ns(0.25)
        place(sparkle, sine(f, m) * env_exp(m, 0.04, 0.002), r.integers(0, n), r.uniform(0.3, 1), wrap=True)
    crk = spec_filter(crackle(n, r, 140, 0.0005, circular=True), g_bp(1800, 9000))
    loop_out(HEAL + "shield-core-use-loop.wav",
             0.65 * saturate(h * pulse, 1.5) + 0.25 * norm(sparkle) + 0.35 * norm(crk) + 0.08 * band(n, r, 5000, 14000))

    # Phoenix Capsule: pressurised injection hiss + warm hum + rising arpeggio shimmer (cycles each loop)
    r = rng(2006)
    hiss = band(n, r, 2500, 12000) * (0.6 + 0.4 * per_env(n, r, 3))
    h = hum(n, 73.4, [1, 0.5, 0.3, 0.2], detune_cycles=1, r=r)
    arp = np.zeros(n)
    notes = [587.3, 740.0, 880.0, 1174.7, 880.0, 740.0, 1174.7, 1480.0]
    for i, f in enumerate(notes):
        m = ns(0.6)
        bell = fm(f, f * 2.0, 1.2 * env_exp(m, 0.08), m) * env_exp(m, 0.18, 0.004)
        place(arp, bell, ns(i * 3.0 / len(notes)), 1.0, wrap=True)
    pulse = 1 + 0.2 * np.sin(TAU * qfreq(2, n) * t)
    x = 0.4 * hiss + 0.45 * h * pulse + 0.35 * norm(arp)
    loop_out(HEAL + "phoenix-capsule-use-loop.wav", x, room=0.35)


def heal_oneshots():
    r = rng(2101)
    n = ns(1.2)
    b1 = fm(1318.5, 2637, 1.4 * env_exp(n, 0.1), n) * env_exp(n, 0.3, 0.003)
    b2 = fm(1975.5, 3951, 1.2 * env_exp(n, 0.1), n) * env_exp(n, 0.35, 0.003)
    sw = whoosh(r, 0.35, 600, 5000, q=0.9, peak=0.85)
    x = events(1.4, [(0.0, sw, 0.35), (0.25, b1, 0.6), (0.33, b2, 0.55), (0.25, thud(r, 140, 0.05), 0.35)])
    out(HEAL + "use-complete.wav", reverb(x, ir("room"), wet=0.25), rms_db=-13.0)

    r = rng(2102)
    m = ns(0.35)
    tone = lp(square(np.geomspace(620, 280, m), m), 2200) * env_exp(m, 0.12, 0.003)
    fizz = filt(crackle(ns(0.3), r, 1500, 0.0003), [("hp", 2000), ("lp", 8000)]) * env_exp(ns(0.3), 0.08)
    x = events(0.7, [(0.0, rustle(r, 0.25, 300, 4000), 0.4), (0.02, tone, 0.45), (0.04, fizz, 0.35)])
    out(HEAL + "use-interrupted.wav", reverb(x, ir("small"), wet=0.15), rms_db=-19.0)

    r = rng(2103)
    x = events(0.5, [(0.0, rustle(r, 0.2, 400, 6000), 0.5), (0.06, thud(r, 300, 0.02, noise_lp=2500), 0.6),
                     (0.07, click(r, 3200), 0.4), (0.09, rattle(r, 0.2, 3, 2800), 0.18)])
    out(HEAL + "pickup.wav", reverb(x, ir("small"), wet=0.12), rms_db=-19.0)


# ---------------------------------------------------------------- grenades
def grenades():
    r = rng(2201)
    pin = events(0.4, [(0.0, scrape(r, 0.06, 2000, 8000), 0.4), (0.06, metal_hit(r, 4700, 0.09, modes=5), 0.7),
                       (0.06, click(r, 5000), 0.5)])
    spoon = metal_hit(r, 3300, 0.14, modes=6, bright=0.9)
    throw = whoosh(r, 0.42, 250, 1400, q=0.8, peak=0.55)
    x = events(1.3, [(0.0, rustle(r, 0.25), 0.25), (0.12, pin, 1.0), (0.42, spoon, 0.45),
                     (0.5, throw, 0.7), (0.5, rustle(r, 0.35, 200, 3000), 0.3)])
    out(GREN + "pin-and-throw.wav", reverb(x, ir("small"), wet=0.12), rms_db=-17.0)

    for v in range(3):
        r = rng(2210 + v)
        p = [1.0, 0.92, 1.08][v]
        hit = lambda s: events(0.4, [(0.0, thud(r, 190 * p, 0.03, noise_lp=1600), 1.0 * s),
                                     (0.0, metal_hit(r, 1250 * p, 0.05, bright=0.7), 0.55 * s),
                                     (0.0, filt(burst(r, 0.03, 0.004), [("hp", 800), ("lp", 5000)]), 0.4 * s)])
        gap = r.uniform(0.13, 0.2)
        x = events(0.9, [(0.0, hit(1.0), 1.0), (gap, hit(0.45), 1.0), (gap * 1.65, hit(0.2), 1.0),
                         (gap * 2.0, rattle(r, 0.2, 2, 1800), 0.08)])
        out(GREN + f"bounce-{v + 1:02d}.wav", reverb(x, ir("outdoor"), wet=0.1), rms_db=-16.0)

    out(GREN + "frag-detonation-close.wav", explosion(rng(2220), 1.0, 4.5), rms_db=-9.0, fout=0.5)
    out(GREN + "frag-detonation-distant.wav", explosion(rng(2221), 1.0, 6.0, distant=True), rms_db=-14.0, fout=0.8)

    # Arc burst: electrical discharge
    r = rng(2230)
    n = ns(2.4)
    t = tvec(n)
    snap = hp(burst(r, 0.02, 0.0025), 2000)
    m = ns(0.6)
    fz = np.geomspace(3200, 160, m)
    zap = fm(fz, fz * 1.5, 4 * env_exp(m, 0.08), m) * env_exp(m, 0.18, 0.001)
    buzz_f = 92 * (1 + 0.04 * np.sin(TAU * 13 * t))
    buzz = lp(saw(buzz_f, n) + 0.5 * square(buzz_f * 1.5, n), 3000) * env_exp(n, 0.35, 0.002)
    buzz *= 0.7 + 0.3 * np.sign(np.sin(TAU * 31 * t))
    field = filt(crackle(n, r, 500, 0.0003), [("hp", 2000), ("lp", 10000)]) * env_exp(n, 0.5, 0.001)
    arcs = np.zeros(n)
    for _ in range(9):
        k = ns(r.uniform(0.02, 0.06))
        a = filt(crackle(k, r, 9000, 0.0002), [("hp", 1500), ("lp", 9000)])
        place(arcs, fade(a, 0.001, 0.005), ns(r.uniform(0.02, 1.2) ** 1.5), r.uniform(0.3, 1.0))
    x = (0.8 * pad_to(norm(snap), n) + 0.7 * pad_to(norm(zap), n) + 0.5 * norm(buzz) + 0.45 * norm(field)
         + 0.5 * norm(arcs) + 0.6 * pad_to(thud(r, 70, 0.12), n))
    out(GREN + "arc-burst.wav", reverb(x, ir("outdoor"), wet=0.3), rms_db=-12.0, fout=0.3)

    # Veil: smoke canister hiss loop
    r = rng(2240)
    n = ns(4.0)
    hiss = spec_filter(white(n, r), g_mul(g_hp(700, 2), g_lp(9000, 2), g_peak(3500, 0.8, 5)))
    flutter = per_env(n, r, 9, 0.75)
    gas = spec_filter(colored(n, r, -3), g_lp(350, 2))
    sputter = spec_filter(crackle(n, r, 60, 0.001, circular=True), g_bp(600, 4000))
    x = norm(hiss) * flutter + 0.25 * norm(gas) + 0.15 * norm(sputter)
    loop_out(GREN + "veil-hiss-loop.wav", x, rms_db=-19.0, room=0.1)


# ---------------------------------------------------------------- tethercaster
def tethercaster():
    r = rng(2301)
    m = ns(0.3)
    spool = lp(square(np.geomspace(220, 70, m), m), 1800) * env_exp(m, 0.1, 0.002)
    zing_n = ns(0.25)
    zf = np.geomspace(2800, 900, zing_n)
    zing = fm(zf, zf * 1.5, 1.0, zing_n) * env_exp(zing_n, 0.06, 0.001)
    x = events(0.9, [(0.0, thud(r, 140, 0.04, noise_lp=2000), 1.0), (0.0, hp(burst(r, 0.05, 0.008), 800), 0.5),
                     (0.005, zing, 0.35), (0.01, whoosh(r, 0.4, 5500, 1200, q=1.2, peak=0.15), 0.6),
                     (0.02, spool, 0.3)])
    out(TETH + "fire.wav", reverb(x, ir("outdoor"), wet=0.15), rms_db=-14.0)

    r = rng(2302)
    tw = karplus(118, 0.8, r, decay=0.997, bright=0.55)
    tw = lp(tw, 2500) * env_exp(len(tw), 0.25, 0.002)
    deb = filt(crackle(ns(0.4), r, 400, 0.0004), [("hp", 1500), ("lp", 6000)]) * env_exp(ns(0.4), 0.1)
    x = events(1.0, [(0.0, metal_hit(r, 880, 0.08, bright=0.8), 1.0), (0.0, thud(r, 110, 0.05), 0.9),
                     (0.0, click(r, 3000), 0.6), (0.01, tw, 0.45), (0.01, deb, 0.25)])
    out(TETH + "anchor-hit.wav", reverb(x, ir("outdoor"), wet=0.2), rms_db=-14.0)

    # reel loop: motor whine + gear ratchet + cable zip, 2 s circular
    r = rng(2303)
    n = ns(2.0)
    t = tvec(n)
    L = n / SR
    wob = 0.004 * np.sin(TAU * t / L * 3)
    f0 = qfreq(420, n)
    ph = f0 * t + np.cumsum(f0 * wob) / SR
    ph -= (ph[-1] + f0 / SR - round(ph[-1] + f0 / SR)) * t / L  # keep phase periodic
    whine = np.sin(TAU * ph) + 0.4 * np.sin(TAU * 2 * ph) + 0.25 * np.sin(TAU * 3 * ph + 0.5)
    rate = qfreq(48, n)
    tick = np.zeros(n)
    k = click(r, 2200, 1.5)
    for i in range(int(round(rate * L))):
        place(tick, k * r.uniform(0.7, 1.0), ns(i / rate), 1.0, wrap=True)
    zip_ = band(n, r, 3000, 9000) * (0.7 + 0.3 * np.sin(TAU * rate * t))
    motor = hum(n, 105, [1, 0.5, 0.3], r=r)
    x = 0.4 * norm(whine) + 0.45 * norm(tick) + 0.3 * zip_ + 0.35 * motor
    loop_out(TETH + "reel-loop.wav", x, rms_db=-19.0, room=0.1)

    r = rng(2304)
    tw = karplus(88, 0.6, r, decay=0.994, bright=0.5)
    tw = lp(tw, 1800) * env_exp(len(tw), 0.15, 0.002)
    x = events(0.9, [(0.0, metal_hit(r, 2600, 0.03), 0.8), (0.0, click(r, 4200), 0.6),
                     (0.01, hp(burst(r, 0.3, 0.07, 0.003), 2000), 0.4), (0.03, tw, 0.4),
                     (0.03, whoosh(r, 0.35, 2500, 600, q=1.0, peak=0.2), 0.3)])
    out(TETH + "release.wav", reverb(x, ir("outdoor"), wet=0.15), rms_db=-16.0)

    r = rng(2305)
    rise = chirp(500, 1800, 0.2, shape="sine") * 0.6
    m = ns(0.8)
    d1 = fm(1568, 3136, 1.0 * env_exp(m, 0.06), m) * env_exp(m, 0.18, 0.002)
    d2 = fm(2349, 4698, 0.8 * env_exp(m, 0.06), m) * env_exp(m, 0.22, 0.002)
    x = events(1.0, [(0.0, rise, 0.3), (0.2, click(r, 3500), 0.4), (0.2, d1, 0.5), (0.27, d2, 0.45)])
    out(TETH + "recharge-complete.wav", reverb(x, ir("room"), wet=0.2), rms_db=-18.0)


def main():
    heal_loops()
    heal_oneshots()
    grenades()
    tethercaster()


if __name__ == "__main__":
    main()
