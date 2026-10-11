"""Higher-level sound-design building blocks shared by the generator scripts."""
from synth import *  # noqa: F401,F403
from synth import (SR, TAU, ns, tvec, rng, white, colored, crackle, sine, saw, square, fm, modal,
                   env_exp, env_pts, env_ar, fade, lp, hp, bp, filt, svf, saturate, norm, place,
                   pad_to, make_ir, reverb, echoes, spec_filter, g_lp, g_hp, g_bp, karplus)
import numpy as np

_IRS = {}


def ir(name):
    """Cached reverb impulse responses for the common spaces."""
    if name not in _IRS:
        if name == "outdoor":
            _IRS[name] = make_ir(t60=1.6, predelay=0.012, bright=0.7, early=10, early_span=0.09, seed=11)
        elif name == "outdoor_long":
            _IRS[name] = make_ir(t60=3.2, predelay=0.03, bright=0.5, early=12, early_span=0.2, seed=12)
        elif name == "small":
            _IRS[name] = make_ir(t60=0.28, predelay=0.002, bright=1.0, early=6, early_span=0.02, seed=13)
        elif name == "room":
            _IRS[name] = make_ir(t60=0.7, predelay=0.006, bright=0.8, early=8, early_span=0.04, seed=14)
        elif name == "hall_st":
            _IRS[name] = make_ir(t60=4.5, predelay=0.03, bright=0.6, early=10, early_span=0.08, seed=15,
                                 stereo_out=True)
        elif name == "plate_st":
            _IRS[name] = make_ir(t60=1.8, predelay=0.01, bright=0.9, early=6, early_span=0.03, seed=16,
                                 stereo_out=True)
        else:
            raise KeyError(name)
    return _IRS[name]


def burst(r, dur, tau, attack=0.0003):
    n = ns(dur)
    return white(n, r) * env_exp(n, tau, attack)


def click(r, f=3500, q=2.0, tau=0.0008):
    """Tiny mechanical click."""
    x = bp(burst(r, tau * 10, tau, 0.00005), f, q)
    return norm(x)


def metal_hit(r, base=1800.0, decay=0.05, modes=7, bright=0.85, noise=0.6, dur=None):
    """Struck metal part: inharmonic modal bank plus a noisy contact transient."""
    ratios = [1.0, 1.47, 2.09, 2.56, 3.39, 4.17, 5.03, 6.21, 7.4][:modes]
    freqs = [base * k * (1 + 0.015 * r.standard_normal()) for k in ratios]
    freqs = [f for f in freqs if f < SR * 0.45]
    decays = [decay / (1 + 0.3 * i) for i in range(len(freqs))]
    amps = [(bright ** i) * r.uniform(0.4, 1.0) for i in range(len(freqs))]
    n = ns(dur if dur else decay * 7)
    x = norm(modal(n, freqs, decays, amps, r))
    contact = hp(burst(r, 0.01, 0.0012, 0.00005), base * 0.7)
    x = x * fade(np.ones(n), 0.0002, 0) + noise * norm(pad_to(contact, n))
    return norm(x)


def glass_hit(r, base=3200.0, decay=0.08, dur=None):
    ratios = [1.0, 2.32, 4.25, 6.63, 9.38]
    freqs = [base * k * (1 + 0.01 * r.standard_normal()) for k in ratios]
    freqs = [f for f in freqs if f < SR * 0.45]
    n = ns(dur if dur else decay * 6)
    x = norm(modal(n, freqs, [decay / (1 + 0.5 * i) for i in range(len(freqs))],
                   [0.9 ** i for i in range(len(freqs))], r))
    x += 0.5 * norm(pad_to(hp(burst(r, 0.006, 0.0006), 4000), n))
    return norm(x)


def thud(r, f=90.0, tau=0.06, drop=1.6, noise_lp=700.0, noise_amt=0.5, dur=None):
    """Low body impact: pitch-dropping sine plus lowpassed noise."""
    n = ns(dur if dur else tau * 7)
    fr = f * (1 + (drop - 1) * env_exp(n, 0.015))
    body = sine(fr, n) * env_exp(n, tau, 0.0006)
    nz = lp(white(n, r), noise_lp, order=2) * env_exp(n, tau * 0.35, 0.0003)
    return norm(norm(body) + noise_amt * norm(nz))


def scrape(r, dur, f_lo=1200.0, f_hi=7000.0, grain_rate=900.0, swell=True):
    """Friction / sliding part: granular crackle plus band noise."""
    n = ns(dur)
    g = crackle(n, r, grain_rate, decay=0.00025)[:n]
    nz = white(n, r) * 0.25 * np.std(g)
    x = filt(g + nz, [("hp", f_lo, 0.7), ("lp", f_hi, 0.7)])
    if swell:
        x *= np.sin(np.pi * np.clip(tvec(n) / dur, 0, 1)) ** 0.7
    return norm(fade(x, 0.002, 0.01))


def rustle(r, dur, f_lo=300.0, f_hi=5000.0, density=300.0):
    """Cloth / gear rustle: soft bandpassed noise with slow granular texture."""
    n = ns(dur)
    nz = white(n, r)
    am = np.abs(lp(r.standard_normal(n), 30.0, order=2))
    am /= am.max() + 1e-9
    g = crackle(n, r, density, decay=0.0015)[:n]
    x = filt(nz * (0.3 + am) + 0.5 * g / (np.std(g) + 1e-9), [("hp", f_lo), ("lp", f_hi)])
    x *= np.sin(np.pi * np.clip(tvec(n) / dur, 0, 1)) ** 1.2
    return norm(x)


def whoosh(r, dur, f0, f1, q=1.0, peak=0.5, shape=1.5):
    """Air movement: bandpassed noise with a swept centre frequency and a swell envelope."""
    n = ns(dur)
    fc = np.geomspace(f0, f1, n)
    x = svf(white(n, r), fc, q, "bp")
    t = tvec(n) / dur
    e = np.where(t < peak, (t / peak) ** shape, ((1 - t) / (1 - peak)) ** shape)
    return norm(x * e)


def rattle(r, dur, count, base=2200.0, decay=0.012):
    """Loose small parts rattling after a handling move."""
    n = ns(dur)
    out = np.zeros(n)
    for i in range(count):
        t0 = r.uniform(0, dur * 0.7) * (i / max(1, count)) ** 0.5
        h = metal_hit(r, base * r.uniform(0.7, 1.4), decay * r.uniform(0.6, 1.3), modes=5)
        place(out, h, ns(t0), r.uniform(0.3, 1.0) * (1 - i / (count + 1)))
    return norm(out)


def chirp(f0, f1, dur, tau=None, shape="sine", curve="exp"):
    n = ns(dur)
    fr = np.geomspace(f0, f1, n) if curve == "exp" else np.linspace(f0, f1, n)
    osc = {"sine": sine, "saw": saw, "square": square}[shape](fr, n)
    e = env_exp(n, tau, 0.001) if tau else np.sin(np.pi * tvec(n) / dur)
    return osc * e


def events(total, items):
    """Assemble a one-shot from (time_s, signal, gain) tuples."""
    out = np.zeros(ns(total))
    for t, s, g in items:
        place(out, s, ns(t), g)
    return out


def explosion(r, size=1.0, dur=4.0, distant=False, crack=1.0, debris=1.0):
    """Big detonation: crack, pitch-dropping boom, swept blast noise, rumble, debris, tail."""
    n = ns(dur)
    t = tvec(n)
    out = np.zeros(n)
    # boom
    fr = 30 + (110 / size ** 0.3) * np.exp(-t / 0.06)
    boom = sine(fr, n) * env_exp(n, 0.32 * size, 0.0015)
    out += 1.0 * saturate(norm(boom) * 1.5, 2.0)
    # blast noise with closing lowpass
    nb = ns(min(dur, 1.6 * size))
    fc = 300 + 8000 * np.exp(-tvec(nb) / (0.07 * size))
    blast = svf(white(nb, r), fc, 0.7, "lp") * env_exp(nb, 0.22 * size, 0.0008)
    place(out, saturate(norm(blast) * 2.5, 2.5), 0, 0.9)
    # rumble
    rum = lp(colored(n, r, -6.0), 180, order=2) * env_ar(n, 0.08, dur * 0.8, curve=2.5)
    out += 0.55 * norm(rum)
    if not distant:
        c = hp(burst(r, 0.03, 0.003, 0.0001), 1500, order=2)
        place(out, norm(c), 0, 0.8 * crack)
        # debris patter
        dn = ns(min(dur, 2.2))
        d = crackle(dn, r, 160, decay=0.0006)[:dn]
        d = filt(d, [("hp", 1500), ("lp", 7000)]) * env_pts(dn, [(0, 0), (0.12, 1), (0.6, 0.5), (2.2, 0)])
        place(out, norm(d), ns(0.1), 0.18 * debris)
        out = reverb(out, ir("outdoor_long"), wet=0.35)[:n]
    else:
        out = lp(out, 650, order=2)
        out = reverb(out, ir("outdoor_long"), wet=0.9, dry=0.6)[:n]
        out = echoes(out, [0.45, 1.1, 1.9], [0.35, 0.22, 0.12], [500, 400, 300])[:n]
    return out


def outdoor_tail(x, wet=0.25, slap=True):
    y = reverb(x, ir("outdoor"), wet=wet)
    if slap:
        y = echoes(y, [0.11, 0.24], [0.22, 0.1], [2500, 1500])
    return y


# ---------------------------------------------------------------- loop helpers (circular)
def per_env(n, r, rate, floor=0.0, power=1.0):
    """Periodic random envelope in [floor, 1] (circular lowpassed noise)."""
    x = spec_filter(r.standard_normal(n), g_lp(rate, 3))
    x = (x - x.min()) / (x.max() - x.min() + 1e-12)
    return floor + (1 - floor) * x ** power


def bumps(n, times, width, wrap=True):
    """Gaussian bumps at the given times (seconds), wrapping around the loop."""
    t = tvec(n)
    L = n / SR
    e = np.zeros(n)
    for c in times:
        d = np.abs(t - c)
        d = np.minimum(d, L - d) if wrap else d
        e += np.exp(-0.5 * (d / width) ** 2)
    return e


def band(n, r, lo, hi, order=2):
    """Circular band-limited noise, unit peak."""
    return norm(spec_filter(white(n, r), g_bp(lo, hi, order)))
