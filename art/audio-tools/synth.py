"""Shared DSP helpers for the Orbit Royale procedural audio generators.

Pure numpy (no scipy). Everything is deterministic given a seed.

Conventions
- Mono signals are 1-D float64 arrays, stereo signals are (n, 2) arrays.
- Time-invariant IIR filters are realised as "IR + FFT convolution": the
  impulse response of the biquad cascade is computed with a short Python loop
  and convolved with the signal. That keeps filters causal (no pre-ringing on
  transients) but fast. Pass circular=True for loops so the filter wraps.
- spec_filter() is a zero-phase magnitude filter in the frequency domain; it is
  circular by construction and is the tool of choice for seamless loops.
- Loops are generated circularly wherever possible (circular noise, periodic
  oscillators with frequencies quantised to the loop length, events wrapped
  modulo the loop, circular reverb) so the seam is seamless by construction.
"""
import math
import os
import wave

import numpy as np

SR = 48000
TAU = 2.0 * np.pi

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
AUDIO_ROOT = os.path.join(REPO, "game", "assets", "audio")


# ---------------------------------------------------------------- basics
def ns(sec):
    return max(1, int(round(sec * SR)))


def tvec(n):
    return np.arange(n, dtype=np.float64) / SR


def rng(seed):
    return np.random.default_rng(seed)


def db(x):
    return 20.0 * np.log10(max(float(x), 1e-12))


def undb(d):
    return 10.0 ** (d / 20.0)


def semis(f, s):
    return f * 2.0 ** (s / 12.0)


def midi(m):
    return 440.0 * 2.0 ** ((m - 69) / 12.0)


def qfreq(f, n_loop):
    """Quantise a frequency so it completes an integer number of cycles in n_loop samples."""
    L = n_loop / SR
    return max(1, round(f * L)) / L


def pad_to(x, n):
    if len(x) >= n:
        return x[:n]
    shape = (n - len(x),) + x.shape[1:]
    return np.concatenate([x, np.zeros(shape)])


def mix(*parts):
    n = max(len(p) for p in parts)
    out = np.zeros((n,) + parts[0].shape[1:])
    for p in parts:
        out[: len(p)] += p
    return out


def place(dst, src, start, gain=1.0, wrap=False):
    """Add src into dst at sample offset start (wrapping modulo len(dst) if wrap)."""
    start = int(start)
    n = len(dst)
    if wrap:
        start %= n
        src = src * gain
        pos = 0
        while pos < len(src):
            s = (start + pos) % n
            k = min(len(src) - pos, n - s)
            dst[s : s + k] += src[pos : pos + k]
            pos += k
        return dst
    if start >= n:
        return dst
    s0 = max(0, start)
    k0 = s0 - start
    k1 = min(len(src), n - start)
    if k1 > k0:
        dst[s0 : start + k1] += src[k0:k1] * gain
    return dst


def stereo(x, pan=0.0):
    """Equal-power pan of a mono signal; pan -1..1."""
    a = (pan + 1.0) * np.pi / 4.0
    return np.stack([x * np.cos(a), x * np.sin(a)], axis=1)


# ---------------------------------------------------------------- envelopes
def env_exp(n, tau, attack=0.0):
    e = np.exp(-tvec(n) / max(tau, 1e-6))
    if attack > 0:
        a = min(n, ns(attack))
        e[:a] *= 0.5 - 0.5 * np.cos(np.linspace(0, np.pi, a))
    return e


def env_pts(n, pts):
    """Piecewise-linear envelope from (time_s, value) points."""
    ts = np.array([p[0] for p in pts], dtype=float)
    vs = np.array([p[1] for p in pts], dtype=float)
    return np.interp(tvec(n), ts, vs)


def env_ar(n, attack, release, hold=0.0, curve=2.0):
    t = tvec(n)
    e = np.zeros(n)
    a = np.clip(t / max(attack, 1e-6), 0, 1)
    e = a ** (1.0 / curve) if curve != 1 else a
    rel = np.clip((t - attack - hold) / max(release, 1e-6), 0, 1)
    return e * (1 - rel) ** curve


def fade(x, fin=0.001, fout=0.005):
    x = x.copy()
    a = min(len(x), ns(fin)) if fin > 0 else 0
    b = min(len(x), ns(fout)) if fout > 0 else 0
    if a > 1:
        w = 0.5 - 0.5 * np.cos(np.linspace(0, np.pi, a))
        x[:a] *= w if x.ndim == 1 else w[:, None]
    if b > 1:
        w = 0.5 + 0.5 * np.cos(np.linspace(0, np.pi, b))
        x[-b:] *= w if x.ndim == 1 else w[:, None]
    return x


# ---------------------------------------------------------------- noise
def white(n, r):
    return r.standard_normal(n)


def colored(n, r, slope_db_oct=-3.0, lo=10.0):
    """Spectrally sloped noise (pink = -3, brown = -6), circular, unit RMS."""
    X = np.fft.rfft(r.standard_normal(n))
    f = np.fft.rfftfreq(n, 1 / SR)
    f[0] = lo
    X *= np.maximum(f, lo) ** (slope_db_oct / 6.0206)
    x = np.fft.irfft(X, n)
    return x / (np.sqrt(np.mean(x ** 2)) + 1e-12)


def smooth_noise(n, r, rate_hz, circular=False):
    """Slowly varying random control signal in roughly [-1, 1] (lowpassed noise)."""
    x = r.standard_normal(n)
    x = spec_filter(x, lambda f: 1.0 / (1.0 + (f / rate_hz) ** 4))
    return x / (np.max(np.abs(x)) + 1e-12)


def crackle(n, r, density, decay=0.0004, amp_spread=1.0, circular=False):
    """Sparse random impulses (Poisson with given density per second), each a tiny decaying burst."""
    out = np.zeros(n)
    count = r.poisson(density * n / SR)
    pos = r.integers(0, n, count)
    amps = r.standard_normal(count) * np.exp(r.standard_normal(count) * amp_spread * 0.5)
    np.add.at(out, pos, amps)
    k = env_exp(ns(decay * 6), decay) * r.standard_normal(ns(decay * 6))
    return fftconv(out, k, circular=circular)[:n]


# ---------------------------------------------------------------- oscillators
def phase_of(f, n):
    """Phase in cycles for scalar or per-sample frequency."""
    if np.isscalar(f):
        return f * tvec(n)
    return np.cumsum(f) / SR


def sine(f, n, ph0=0.0):
    return np.sin(TAU * (phase_of(f, n) + ph0))


def _blep(t, dt):
    out = np.zeros_like(t)
    m = t < dt
    u = t[m] / dt[m] if np.ndim(dt) else t[m] / dt
    out[m] = u + u - u * u - 1.0
    m2 = t > 1.0 - dt
    u = (t[m2] - 1.0) / (dt[m2] if np.ndim(dt) else dt)
    out[m2] = u * u + u + u + 1.0
    return out


def saw(f, n, ph0=0.0):
    ph = phase_of(f, n) + ph0
    t = ph - np.floor(ph)
    dt = np.abs(f) / SR if not np.isscalar(f) else abs(f) / SR
    return 2.0 * t - 1.0 - _blep(t, dt)


def square(f, n, ph0=0.0, duty=0.5):
    ph = phase_of(f, n) + ph0
    t = ph - np.floor(ph)
    dt = np.abs(f) / SR if not np.isscalar(f) else abs(f) / SR
    t2 = t + (1 - duty)
    t2 -= np.floor(t2)
    return np.where(t < duty, 1.0, -1.0) + _blep(t, dt) - _blep(t2, dt)


def tri(f, n, ph0=0.0):
    ph = phase_of(f, n) + ph0 + 0.25
    t = ph - np.floor(ph)
    return 4.0 * np.abs(t - 0.5) - 1.0


def fm(fc, fmod, index, n, ph0=0.0):
    """Two-operator FM; index may be an envelope array."""
    mod = np.sin(TAU * phase_of(fmod, n))
    return np.sin(TAU * (phase_of(fc, n) + ph0) + index * mod)


def modal(n, freqs, decays, amps, r=None, jitter=0.0):
    """Bank of exponentially decaying sinusoids (struck metal / glass / wood)."""
    t = tvec(n)
    out = np.zeros(n)
    for i, (f, d, a) in enumerate(zip(freqs, decays, amps)):
        if r is not None and jitter:
            f *= 1 + jitter * r.standard_normal()
        ph = r.random() if r is not None else 0.0
        out += a * np.exp(-t / d) * np.sin(TAU * (f * t + ph))
    return out


def karplus(f, dur, r, decay=0.996, bright=0.5):
    """Karplus-Strong plucked string (cable twang)."""
    n = ns(dur)
    N = max(2, int(round(SR / f)))
    buf = list(r.uniform(-1, 1, N))
    out = [0.0] * n
    b = bright
    prev = 0.0
    for i in range(n):
        v = buf[i % N]
        out[i] = v
        nv = decay * (b * v + (1 - b) * prev)
        prev = v
        buf[i % N] = nv
    return np.array(out)


# ---------------------------------------------------------------- filters
def next_fast(n):
    p = 1
    while p < n:
        p <<= 1
    if p // 4 * 3 >= n:
        return p // 4 * 3
    return p


def fftconv(x, h, circular=False):
    """Linear (or circular, length len(x)) convolution of 1-D x with 1-D h."""
    if circular:
        n = len(x)
        hh = np.zeros(n)
        if len(h) <= n:
            hh[: len(h)] = h
        else:
            # fold long kernel modulo n
            k = len(h)
            pad = (-k) % n
            hh = np.concatenate([h, np.zeros(pad)]).reshape(-1, n).sum(axis=0)
        return np.fft.irfft(np.fft.rfft(x) * np.fft.rfft(hh), n)
    m = len(x) + len(h) - 1
    nf = next_fast(m)
    return np.fft.irfft(np.fft.rfft(x, nf) * np.fft.rfft(h, nf), nf)[:m]


def _rbj(kind, f0, q=0.7071, gain_db=0.0):
    f0 = min(max(f0, 5.0), SR * 0.49)
    w = TAU * f0 / SR
    cw, sw = math.cos(w), math.sin(w)
    al = sw / (2 * q)
    A = 10 ** (gain_db / 40.0)
    if kind == "lp":
        b = [(1 - cw) / 2, 1 - cw, (1 - cw) / 2]
        a = [1 + al, -2 * cw, 1 - al]
    elif kind == "hp":
        b = [(1 + cw) / 2, -(1 + cw), (1 + cw) / 2]
        a = [1 + al, -2 * cw, 1 - al]
    elif kind == "bp":  # constant 0 dB peak gain
        b = [al, 0.0, -al]
        a = [1 + al, -2 * cw, 1 - al]
    elif kind == "notch":
        b = [1, -2 * cw, 1]
        a = [1 + al, -2 * cw, 1 - al]
    elif kind == "peak":
        b = [1 + al * A, -2 * cw, 1 - al * A]
        a = [1 + al / A, -2 * cw, 1 - al / A]
    elif kind == "ls":
        sq = 2 * math.sqrt(A) * al
        b = [A * ((A + 1) - (A - 1) * cw + sq), 2 * A * ((A - 1) - (A + 1) * cw), A * ((A + 1) - (A - 1) * cw - sq)]
        a = [(A + 1) + (A - 1) * cw + sq, -2 * ((A - 1) + (A + 1) * cw), (A + 1) + (A - 1) * cw - sq]
    elif kind == "hs":
        sq = 2 * math.sqrt(A) * al
        b = [A * ((A + 1) + (A - 1) * cw + sq), -2 * A * ((A - 1) + (A + 1) * cw), A * ((A + 1) + (A - 1) * cw - sq)]
        a = [(A + 1) - (A - 1) * cw + sq, 2 * ((A - 1) - (A + 1) * cw), (A + 1) - (A - 1) * cw - sq]
    else:
        raise ValueError(kind)
    return [v / a[0] for v in b], [1.0, a[1] / a[0], a[2] / a[0]]


def _lfilter(b, a, x):
    b0, b1, b2 = b
    _, a1, a2 = a
    y = [0.0] * len(x)
    x1 = x2 = y1 = y2 = 0.0
    for i, xi in enumerate(x):
        yi = b0 * xi + b1 * x1 + b2 * x2 - a1 * y1 - a2 * y2
        x2 = x1
        x1 = xi
        y2 = y1
        y1 = yi
        y[i] = yi
    return y


_IR_CACHE = {}


def cascade_ir(sections, max_len=1 << 15):
    key = tuple(tuple(s) for s in sections)
    if key in _IR_CACHE:
        return _IR_CACHE[key]
    coefs = [_rbj(*s) for s in sections]
    m = 1024
    while True:
        h = [0.0] * m
        h[0] = 1.0
        for b, a in coefs:
            h = _lfilter(b, a, h)
        h = np.array(h)
        peak = np.max(np.abs(h))
        if m >= max_len or np.max(np.abs(h[-m // 8:])) < peak * 1e-6:
            break
        m *= 4
    mag = np.abs(h)
    thr = mag.max() * 1e-6
    idx = np.nonzero(mag > thr)[0]
    h = h[: idx[-1] + 1 if len(idx) else 1]
    _IR_CACHE[key] = h
    return h


def filt(x, sections, circular=False):
    """Apply a cascade of RBJ biquads, e.g. [("lp", 2000, 0.7), ("hp", 80)]."""
    sections = [tuple(s) if len(s) > 2 else (s[0], s[1], 0.7071) for s in sections]
    h = cascade_ir(sections)
    if x.ndim == 2:
        return np.stack([filt(x[:, c], sections, circular) for c in range(x.shape[1])], axis=1)
    y = fftconv(x, h, circular=circular)
    return y if circular else y[: len(x)]


def lp(x, f, q=0.7071, order=1, circular=False):
    return filt(x, [("lp", f, q)] * order, circular)


def hp(x, f, q=0.7071, order=1, circular=False):
    return filt(x, [("hp", f, q)] * order, circular)


def bp(x, f, q=1.0, order=1, circular=False):
    return filt(x, [("bp", f, q)] * order, circular)


def spec_filter(x, gain_fn):
    """Zero-phase, circular magnitude filter. gain_fn(freqs_hz) -> gains."""
    if x.ndim == 2:
        return np.stack([spec_filter(x[:, c], gain_fn) for c in range(x.shape[1])], axis=1)
    n = len(x)
    f = np.fft.rfftfreq(n, 1 / SR)
    return np.fft.irfft(np.fft.rfft(x) * gain_fn(f), n)


def g_lp(fc, order=2):
    return lambda f: 1.0 / np.sqrt(1.0 + (f / fc) ** (2 * order))


def g_hp(fc, order=2):
    return lambda f: 1.0 / np.sqrt(1.0 + (fc / np.maximum(f, 1e-3)) ** (2 * order))


def g_bp(lo, hi, order=2):
    a, b = g_hp(lo, order), g_lp(hi, order)
    return lambda f: a(f) * b(f)


def g_peak(fc, width_oct, gain_db):
    def g(f):
        d = np.log2(np.maximum(f, 1e-3) / fc) / max(width_oct, 1e-3)
        return 10 ** (gain_db * np.exp(-d * d) / 20.0)
    return g


def g_mul(*fns):
    def g(f):
        out = np.ones_like(f)
        for fn in fns:
            out = out * fn(f)
        return out
    return g


def svf(x, fc, q=0.7071, mode="lp"):
    """Time-varying TPT state-variable filter (fc scalar or per-sample array)."""
    n = len(x)
    fc = np.clip(np.broadcast_to(np.asarray(fc, dtype=float), (n,)), 10.0, SR * 0.45)
    g = np.tan(np.pi * fc / SR)
    k = 1.0 / q
    a1 = 1.0 / (1.0 + g * (g + k))
    a2 = g * a1
    a3 = g * a2
    A1, A2, A3, X = a1.tolist(), a2.tolist(), a3.tolist(), list(map(float, x))
    out = [0.0] * n
    ic1 = ic2 = 0.0
    m = {"lp": 0, "bp": 1, "hp": 2}[mode]
    for i in range(n):
        v3 = X[i] - ic2
        v1 = A1[i] * ic1 + A2[i] * v3
        v2 = ic2 + A2[i] * ic1 + A3[i] * v3
        ic1 = 2 * v1 - ic1
        ic2 = 2 * v2 - ic2
        if m == 0:
            out[i] = v2
        elif m == 1:
            out[i] = v1
        else:
            out[i] = X[i] - k * v1 - v2
    return np.array(out)


# ---------------------------------------------------------------- shaping
def saturate(x, drive=2.0):
    return np.tanh(x * drive) / np.tanh(drive)


def norm(x, peak=1.0):
    m = np.max(np.abs(x))
    return x * (peak / m) if m > 0 else x


def rms(x):
    return float(np.sqrt(np.mean(np.square(x)) + 1e-20))


def st_max_rms(x, win=0.1):
    """Maximum short-term RMS (sliding window) -- a loudness proxy for one-shots."""
    m = x if x.ndim == 1 else np.mean(x, axis=1)
    w = min(len(m), ns(win))
    c = np.concatenate([[0.0], np.cumsum(m * m)])
    e = (c[w:] - c[:-w]) / w
    return float(np.sqrt(max(e.max(), 1e-20)))


def _sliding_max(a, w, circular=False):
    """Centered sliding maximum over ~w samples (log-step doubling)."""
    n = len(a)
    if circular:
        a2 = np.concatenate([a[-w:], a, a[:w]])
    else:
        a2 = np.concatenate([np.zeros(w), a, np.zeros(w)])
    m = a2.copy()
    s = 1
    while s < w:
        m[:-s] = np.maximum(m[:-s], m[s:])
        s *= 2
    # m[i] = max(a2[i : i+s]); center it
    half = s // 2
    out = np.roll(m, half)
    return out[w : w + n]


def limiter(x, ceiling_db=-1.0, window=0.003, circular=False):
    c = undb(ceiling_db)
    a = np.abs(x) if x.ndim == 1 else np.max(np.abs(x), axis=1)
    w = max(4, ns(window))
    env = _sliding_max(a, 2 * w, circular)
    g = np.minimum(1.0, c / np.maximum(env, 1e-9))
    # centered moving average of length w: every gain inside +-w/2 already satisfies
    # the requirement of the centre sample (thanks to the 2w max), so the average does too.
    n = len(a)
    if circular:
        g2 = np.concatenate([g[-w:], g, g[:w]])
    else:
        g2 = np.concatenate([np.ones(w), g, np.ones(w)])
    cs = np.concatenate([[0.0], np.cumsum(g2)])
    ma = (cs[w:] - cs[:-w]) / w
    sm = ma[w - w // 2 : w - w // 2 + n]
    g = np.minimum(sm, 1.0)
    y = x * (g if x.ndim == 1 else g[:, None])
    return np.clip(y, -c, c)


# ---------------------------------------------------------------- reverb / space
def make_ir(t60=1.5, length=None, predelay=0.008, bright=1.0, early=8, early_span=0.06,
            seed=0, stereo_out=False, lo_mult=1.3, hi_mult=0.45):
    """Synthetic reverb impulse response with frequency-dependent decay."""
    r = rng(seed)
    n = ns(length if length else t60 * 1.15)
    t = tvec(n)
    chans = []
    for c in range(2 if stereo_out else 1):
        nz = r.standard_normal(n)
        lo = spec_filter(nz, g_lp(400, 2))
        hi = spec_filter(nz, g_hp(3500 * bright, 2))
        mid = nz - lo - hi
        h = (lo * np.exp(-6.91 * t / (t60 * lo_mult)) + mid * np.exp(-6.91 * t / t60)
             + hi * np.exp(-6.91 * t / (t60 * hi_mult)))
        # soft onset of the diffuse tail
        h *= 1 - np.exp(-t / 0.012)
        er = np.zeros(n)
        for _ in range(early):
            p = int(r.uniform(0.004, early_span) * SR)
            if p < n:
                er[p] += r.uniform(-1, 1) * (1 - p / (early_span * SR)) * 3.0
        h = h / np.sqrt(np.sum(h ** 2)) + er / max(1.0, np.sqrt(np.sum(er ** 2))) * 0.35
        h = np.concatenate([np.zeros(ns(predelay)), h])
        chans.append(h / np.sqrt(np.sum(h ** 2)))
    if stereo_out:
        m = max(len(c) for c in chans)
        return np.stack([pad_to(c, m) for c in chans], axis=1)
    return chans[0]


def reverb(x, ir, wet=0.3, dry=1.0, circular=False):
    """Convolve with an IR. Mono x + stereo IR -> stereo out. Linear output is lengthened."""
    if ir.ndim == 2:
        if x.ndim == 1:
            xs = [x, x]
        else:
            xs = [x[:, 0], x[:, 1]]
        chans = [reverb(xs[c], ir[:, c], wet, dry, circular) for c in range(2)]
        return np.stack(chans, axis=1)
    if x.ndim == 2:
        return np.stack([reverb(x[:, c], ir, wet, dry, circular) for c in range(2)], axis=1)
    w = fftconv(x, ir, circular=circular)
    d = x if circular else pad_to(x, len(w))
    return dry * d + wet * w


def echoes(x, delays, gains, lps, circular=False, extra=0.0):
    """Discrete reflections: each tap is delayed, scaled and lowpassed (terrain slapback)."""
    n = len(x) if circular else len(x) + ns(max(delays) + extra)
    out = pad_to(x.copy(), n) if not circular else x.copy()
    for d, g, f in zip(delays, gains, lps):
        tap = lp(x, f, order=2, circular=circular)
        place(out, tap, ns(d), g, wrap=circular)
    return out


# ---------------------------------------------------------------- loops
def crossfade_loop(x, L, xf):
    """Fold x (len >= L + xf) into a loop of length L with an equal-power crossfade."""
    assert len(x) >= L + xf
    out = x[:L].copy()
    th = np.linspace(0, np.pi / 2, xf)
    fi, fo = np.sin(th), np.cos(th)
    if x.ndim == 2:
        fi, fo = fi[:, None], fo[:, None]
    out[:xf] = x[:xf] * fi + x[L : L + xf] * fo
    return out


# ---------------------------------------------------------------- mastering / IO
def trim_tail(x, thresh_db=-66.0, min_len=0.05):
    a = np.abs(x) if x.ndim == 1 else np.max(np.abs(x), axis=1)
    thr = a.max() * undb(thresh_db)
    idx = np.nonzero(a > thr)[0]
    end = max(ns(min_len), (idx[-1] + 1) if len(idx) else 1)
    return x[: min(len(x), end + ns(0.01))]


def master(x, peak_db=-1.0, rms_db=None, loop=False, fin=0.0004, fout=0.03, trim=True):
    """Final processing: DC removal, edge fades (one-shots), loudness / peak normalisation."""
    x = np.asarray(x, dtype=np.float64)
    if loop:
        x = spec_filter(x, g_hp(18, 2))
        x = x - np.mean(x, axis=0)
    else:
        x = filt(x, [("hp", 18, 0.7071)])
        if trim:
            x = trim_tail(x)
        x = fade(x, fin, fout)
    if rms_db is not None:
        cur = rms(x) if loop else st_max_rms(x)
        x = x * (undb(rms_db) / max(cur, 1e-12))
        if np.max(np.abs(x)) > undb(peak_db):
            x = limiter(x, peak_db, circular=loop)
            if not loop:
                x = fade(x, fin, fout)
    else:
        x = norm(x, undb(peak_db))
    return x


def write_wav(rel_path, x, root=None):
    path = os.path.join(root or AUDIO_ROOT, rel_path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    x = np.asarray(x, dtype=np.float64)
    ch = 1 if x.ndim == 1 else x.shape[1]
    r = rng(len(x) * 7 + ch)
    d = (r.random(x.shape) - r.random(x.shape)) / 32768.0  # TPDF dither, deterministic
    y = np.clip(np.round((x + d) * 32767.0), -32768, 32767).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(ch)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(y.tobytes())
    return path


def read_wav(path):
    with wave.open(path, "rb") as w:
        ch, sw, sr, nfr = w.getnchannels(), w.getsampwidth(), w.getframerate(), w.getnframes()
        y = np.frombuffer(w.readframes(nfr), dtype="<i2").astype(np.float64) / 32768.0
    if ch > 1:
        y = y.reshape(-1, ch)
    return y, sr, ch, sw


def analyze(x, loop=False):
    m = x if x.ndim == 1 else x
    a = np.abs(m)
    res = {
        "dur": len(m) / SR,
        "peak_db": db(a.max()),
        "rms_db": db(rms(m)),
        "st_db": db(st_max_rms(m)),
        "dc": float(np.max(np.abs(np.mean(m, axis=0)))),
        "clip": int(np.sum(a >= 0.9999)),
        "start": float(np.max(np.abs(m[0]))),
        "end": float(np.max(np.abs(m[-1]))),
    }
    if loop:
        d = np.diff(m, axis=0)
        typ = float(np.sqrt(np.mean(d ** 2))) + 1e-9
        seam = np.max(np.abs(m[0] - m[-1]))
        res["seam"] = float(seam / typ)
        w = ns(0.05)
        res["seam_rms_ratio_db"] = db(rms(m[:w])) - db(rms(m[-w:]))
    return res


def out(rel, x, loop=False, **kw):
    """Master + write + print a one-line report."""
    y = master(x, loop=loop, **kw)
    write_wav(rel, y)
    a = analyze(y, loop)
    line = f"{rel:70s} {a['dur']:6.2f}s pk {a['peak_db']:6.1f} rms {a['rms_db']:6.1f} st {a['st_db']:6.1f}"
    if loop:
        line += f" seam {a['seam']:.2f}"
    print(line, flush=True)
    return y
