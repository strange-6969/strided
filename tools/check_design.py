"""Two static gates on the design system.

1. Colour contrast: every text tone is measured against every surface it can be
   placed on. Written as a computed check, not a maintained list of ratios, so a
   future palette edit cannot quietly drop a tone below AA.
2. Token discipline: no hardcoded colour outside the :root block, so changing the
   palette is one edit rather than a grep across the stylesheet.

The earlier shell version of gate 2 filtered by line number, which broke the
moment a token was added. This parses instead.
"""

from __future__ import annotations

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CSS = ROOT / "app" / "css" / "app.css"

# Tones that carry text, against every surface they can sit on.
TONES = ["text", "body", "text-dim", "text-faint"]
SURFACES = ["bg", "surface", "surface-2", "surface-3"]
MIN_AA = 4.5

HEX = re.compile(r"#[0-9a-fA-F]{3,8}\b")
TOKEN = re.compile(r"--([a-z0-9-]+)\s*:\s*(#[0-9a-fA-F]{3,8})")


def expand(value: str) -> str:
    if len(value) == 4:
        return "#" + "".join(c * 2 for c in value[1:])
    if len(value) in (5, 9):
        # 4 or 8 digit hex with alpha: drop the alpha channel, it does not
        # participate in the luminance calculation.
        body = value[1:]
        keep = (len(value) - 1) // 2
        return "#" + body[:keep]
    return value[:7]


def luminance(colour: str) -> float:
    r, g, b = (int(colour[i:i + 2], 16) / 255 for i in (1, 3, 5))
    channel = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b)


def ratio(a: str, b: str) -> float:
    la, lb = luminance(a), luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def main() -> int:
    css = CSS.read_text()

    # ---- token block ----
    start = css.index(":root {")
    end = css.index("}", start)
    block = css[start:end]
    tokens = {name: expand(value) for name, value in TOKEN.findall(block)}

    errors: list[str] = []

    missing = [n for n in TONES + SURFACES if n not in tokens]
    if missing:
        errors.append(f"tokens missing from :root: {missing}")

    # ---- contrast ----
    print("contrast (WCAG AA needs 4.5:1)")
    for tone in TONES:
        if tone not in tokens:
            continue
        for surface in SURFACES:
            if surface not in tokens:
                continue
            r = ratio(tokens[tone], tokens[surface])
            ok = r >= MIN_AA
            print(f"  {tone:12} on {surface:11} {r:5.2f}  {'AA' if ok else 'FAIL'}")
            if not ok:
                errors.append(f"--{tone} on --{surface} is {r:.2f}:1, needs {MIN_AA}")

    # ---- token discipline ----
    outside = css[:start] + css[end:]
    stray = sorted(set(HEX.findall(outside)))
    if stray:
        errors.append(f"hardcoded colour outside :root: {stray}")
        print(f"\nhardcoded colour outside :root: {stray}")
    else:
        print("colour is tokenised")

    if errors:
        print(f"\n{len(errors)} problem(s):")
        for e in errors:
            print("  x", e)
        return 1

    print("\nOK: design tokens pass contrast and stay tokenised")
    return 0


if __name__ == "__main__":
    sys.exit(main())