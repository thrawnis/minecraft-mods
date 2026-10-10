"""Generate the Low Fire Texture Pack variants.

Draws original animated fire textures (no Mojang artwork) and packs one
.zip per height into ../release/.  Run: python3 src/generate.py
"""
import io
import json
import math
import random
import zipfile
from pathlib import Path

from PIL import Image

SIZE = 16      # texture width/height in pixels
FRAMES = 32    # animation frames per texture (stacked vertically)
MIN_FORMAT = 66     # resource pack formats 66+ = 26.1 and earlier 1.21.x releases
MAX_FORMAT = 1000   # no upper bound, so newer versions don't flag it as incompatible
VERSION = "1.0.0"

# name -> fraction of the texture height the flames reach
VARIANTS = {"low": 0.50, "lower": 0.35, "lowest": 0.20}

# dark red edge -> orange -> yellow -> pale core
PALETTE = [
    (0.00, (110, 20, 6)),
    (0.25, (196, 52, 8)),
    (0.50, (240, 120, 18)),
    (0.75, (252, 196, 48)),
    (1.00, (255, 246, 190)),
]

ROOT = Path(__file__).resolve().parent.parent


def color(v):
    v = max(0.0, min(1.0, v))
    for (a, ca), (b, cb) in zip(PALETTE, PALETTE[1:]):
        if v <= b:
            f = (v - a) / (b - a)
            return tuple(round(ca[i] + (cb[i] - ca[i]) * f) for i in range(3)) + (255,)
    return PALETTE[-1][1] + (255,)


def waves(seed):
    # Integer time frequencies keep the animation looping seamlessly.
    rnd = random.Random(seed)
    return [(rnd.uniform(0.5, 1.0) / k, k, rnd.choice((1, 2)) * k, rnd.uniform(0, 2 * math.pi))
            for k in (2, 3, 5, 7)]


def frame(t, height, seed):
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    w = waves(seed)
    top = SIZE * (1 - height)
    span = SIZE - top
    for x in range(SIZE):
        u = x / SIZE
        # tongue height per column, flickering over time
        tongue = sum(a * math.sin(2 * math.pi * (k * u + ft * t / FRAMES) + p) for a, k, ft, p in w)
        for y in range(SIZE):
            if y < top - 1:
                continue
            d = (y + 0.5 - top) / span            # 0 at flame top, 1 at bottom
            # turbulence moving upward through the flame
            turb = sum(a * math.sin(2 * math.pi * (k * u * 1.7 + k * d + ft * t / FRAMES) + p * 1.3)
                       for a, k, ft, p in w)
            v = d * 1.2 + 0.32 * tongue + 0.14 * turb - 0.32
            if v > 0.12:
                img.putpixel((x, y), color((v - 0.12) / 0.95))
    return img


def strip(height, seed):
    img = Image.new("RGBA", (SIZE, SIZE * FRAMES))
    for t in range(FRAMES):
        img.paste(frame(t, height, seed), (0, t * SIZE))
    return img


def png(img):
    buf = io.BytesIO()
    img.save(buf, "PNG")
    return buf.getvalue()


def build(name, height):
    pct = round(height * 100)
    mcmeta = {"pack": {
        "description": f"Low Fire ({name.title()}, {pct}%) v{VERSION}",
        "min_format": MIN_FORMAT,
        "max_format": MAX_FORMAT,
    }}
    anim = json.dumps({"animation": {}}, indent=2)
    out = ROOT / "release" / f"low-fire-texture-pack-{name}-{VERSION}.zip"
    out.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("pack.mcmeta", json.dumps(mcmeta, indent=2))
        z.writestr("pack.png", png(pack_icon(height)))
        for i, seed in ((0, 11), (1, 29)):
            base = f"assets/minecraft/textures/block/fire_{i}.png"
            z.writestr(base, png(strip(height, seed)))
            z.writestr(base + ".mcmeta", anim)
    print("wrote", out.relative_to(ROOT))


def pack_icon(height):
    return frame(0, height, 11).resize((64, 64), Image.NEAREST)


def preview():
    # side-by-side sheet of the first frames of each variant, for the README
    cols = [strip(h, 11).crop((0, 0, SIZE, SIZE * 4)) for h in VARIANTS.values()]
    sheet = Image.new("RGBA", (len(cols) * (SIZE + 4), SIZE * 4), (40, 40, 40, 255))
    for i, c in enumerate(cols):
        sheet.alpha_composite(c, (i * (SIZE + 4), 0))
    sheet.resize((sheet.width * 8, sheet.height * 8), Image.NEAREST).save(ROOT / "preview.png")


if __name__ == "__main__":
    for name, height in VARIANTS.items():
        build(name, height)
    preview()
