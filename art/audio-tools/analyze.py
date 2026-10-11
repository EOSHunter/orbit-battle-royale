"""Verify every WAV under game/assets/audio: format, peak, loudness, DC, clipping, edges, loop seams, spectrum.

Usage: python analyze.py [-- <subfolder filter>]
Prints one line per file, flags problems with '!!', and ends with per-folder counts and sizes.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np  # noqa: E402
from synth import AUDIO_ROOT, read_wav, db, rms, st_max_rms, ns  # noqa: E402


def spectrum_summary(x, sr):
    m = x if x.ndim == 1 else x.mean(axis=1)
    m = m[: sr * 20]
    X = np.abs(np.fft.rfft(m)) ** 2
    f = np.fft.rfftfreq(len(m), 1 / sr)
    tot = X.sum() + 1e-20
    cen = float((f * X).sum() / tot)
    lo = X[f < 200].sum() / tot
    hi = X[f > 2000].sum() / tot
    return cen, lo, hi


def check(path, rel):
    x, sr, ch, sw = read_wav(path)
    loop = "-loop" in os.path.basename(path)
    a = np.abs(x)
    flags = []
    if sr != 48000 or sw != 2:
        flags.append(f"format {sr}/{sw * 8}bit")
    pk = db(a.max())
    if pk > -0.5:
        flags.append("hot")
    if np.sum(a >= 0.9999) > 0:
        flags.append("clip")
    dc = float(np.max(np.abs(np.mean(x, axis=0))))
    if dc > 0.002:
        flags.append(f"dc {dc:.4f}")
    first = float(np.max(np.abs(x[0])))
    last = float(np.max(np.abs(x[-1])))
    seam = ""
    if loop:
        d = np.diff(x, axis=0)
        typ = float(np.sqrt(np.mean(d ** 2))) + 1e-9
        s = float(np.max(np.abs(x[0] - x[-1]))) / typ
        w = ns(0.1)
        bal = db(rms(x[:w])) - db(rms(x[-w:]))
        seam = f" seam {s:4.2f} edgeRMS {bal:+5.1f}dB"
        if s > 4.0:
            flags.append("seam jump")
        if abs(bal) > 6.0 and s > 2.0:
            flags.append("seam level")
    else:
        if first > 0.01 or last > 0.01:
            flags.append(f"edge {first:.3f}/{last:.3f}")
    cen, lo, hi = spectrum_summary(x, sr)
    line = (f"{rel:66s} {ch}ch {len(x) / sr:6.2f}s pk {pk:6.1f} rms {db(rms(x)):6.1f} st {db(st_max_rms(x)):6.1f}"
            f" cen {cen:6.0f}Hz lo {lo * 100:3.0f}% hi {hi * 100:3.0f}%{seam}")
    if flags:
        line += "  !! " + ", ".join(flags)
    return line, bool(flags)


def main():
    filt = sys.argv[sys.argv.index("--") + 1] if "--" in sys.argv and len(sys.argv) > sys.argv.index("--") + 1 else ""
    sizes = {}
    counts = {}
    bad = 0
    total = 0
    for root, _, files in os.walk(AUDIO_ROOT):
        for fn in sorted(files):
            if not fn.endswith(".wav"):
                continue
            path = os.path.join(root, fn)
            rel = os.path.relpath(path, AUDIO_ROOT).replace("\\", "/")
            folder = os.path.dirname(rel)
            sz = os.path.getsize(path)
            sizes[folder] = sizes.get(folder, 0) + sz
            counts[folder] = counts.get(folder, 0) + 1
            total += sz
            if filt and filt not in rel:
                continue
            line, flagged = check(path, rel)
            bad += flagged
            print(line, flush=True)
    print("\nfolder summary")
    for k in sorted(sizes):
        print(f"  {k:60s} {counts[k]:3d} files {sizes[k] / 1e6:7.2f} MB")
    print(f"  TOTAL {sum(counts.values())} files {total / 1e6:.2f} MB, flagged {bad}")


if __name__ == "__main__":
    main()
