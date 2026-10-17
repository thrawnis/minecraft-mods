"""Generate the Rainbow Cobwebs resource pack.

Draws original (simple, thin-line) cobweb art in see-through colours and
builds ../release/rainbow-cobwebs-<VERSION>.zip.  Run: python3 src/generate.py

How it works: four animated textures each fade through the same colours, but
start at a different colour. The cobweb blockstate picks one of the four at
random per block, so a group of webs always shows a mix of colours.
"""
import io
import json
import math
import zipfile
from pathlib import Path

from PIL import Image

VERSION = "1.0.1"
MIN_FORMAT = 84     # resource pack format of Minecraft 26.1
MAX_FORMAT = 1000   # no upper bound, so newer versions don't flag it as incompatible
NS = "rainbowcobwebs"

SIZE = 16
ALPHA = 179            # 70% solid (30% see-through)
SECONDS_PER_COLOUR = 3
COLOURS = {            # in fade order
    "blue": (40, 110, 255),
    "red": (235, 40, 40),
    "yellow": (250, 215, 30),
    "green": (40, 200, 60),
}

ROOT = Path(__file__).resolve().parent.parent


def web_mask():
    """Simple web, pixel by pixel: 8 one-pixel spokes from an open centre, crossed by two rings."""
    c = 7

    def on(x, y):
        dx, dy = x - c, y - c
        if x > 2 * c or y > 2 * c:
            return False
        if dx == 0 or dy == 0 or dx == dy or dx == -dy:
            return (dx, dy) != (0, 0)
        d = math.hypot(dx, dy)
        return abs(d - 2.9) < 0.45 or abs(d - 5.8) < 0.45

    return [[on(x, y) for x in range(SIZE)] for y in range(SIZE)]


MASK = web_mask()


def frame(rgb):
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    for y in range(SIZE):
        for x in range(SIZE):
            if MASK[y][x]:
                img.putpixel((x, y), rgb + (ALPHA,))
    return img


def strip():
    """All colours stacked as animation frames."""
    cols = list(COLOURS.values())
    img = Image.new("RGBA", (SIZE, SIZE * len(cols)))
    for i, rgb in enumerate(cols):
        img.paste(frame(rgb), (0, i * SIZE))
    return img


def item_icon():
    """One quarter of the web in each colour (blue top-left, red top-right, yellow bottom-left, green bottom-right)."""
    cols = list(COLOURS.values())
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    for y in range(SIZE):
        for x in range(SIZE):
            if MASK[y][x]:
                q = (2 if y >= SIZE // 2 else 0) + (1 if x >= SIZE // 2 else 0)
                img.putpixel((x, y), cols[q] + (ALPHA,))
    return img


def png(img):
    buf = io.BytesIO()
    img.save(buf, "PNG")
    return buf.getvalue()


def dump(obj):
    return json.dumps(obj, indent=2)


def build():
    n = len(COLOURS)
    out = ROOT / "release" / f"rainbow-cobwebs-{VERSION}.zip"
    out.parent.mkdir(exist_ok=True)
    texture = png(strip())
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("pack.mcmeta", dump({"pack": {
            "description": f"Rainbow Cobwebs v{VERSION}: see-through, colour-changing webs",
            "min_format": MIN_FORMAT,
            "max_format": MAX_FORMAT,
        }}))
        z.writestr("pack.png", png(item_icon().resize((64, 64), Image.NEAREST)))
        variants = []
        for start in range(n):
            name = f"cobweb_{start}"
            # Same frames, different starting colour.
            order = [(start + i) % n for i in range(n)]
            z.writestr(f"assets/{NS}/textures/block/{name}.png", texture)
            z.writestr(f"assets/{NS}/textures/block/{name}.png.mcmeta", dump({"animation": {
                "interpolate": True,
                "frametime": SECONDS_PER_COLOUR * 20,
                "frames": order,
            }}))
            z.writestr(f"assets/{NS}/models/block/{name}.json", dump({
                "parent": "minecraft:block/cross",
                "textures": {"cross": f"{NS}:block/{name}"},
            }))
            variants.append({"model": f"{NS}:block/{name}"})
        # Each cobweb block picks one of the four at random (fixed per position).
        z.writestr("assets/minecraft/blockstates/cobweb.json", dump({"variants": {"": variants}}))
        z.writestr(f"assets/{NS}/textures/item/cobweb.png", png(item_icon()))
        z.writestr("assets/minecraft/models/item/cobweb.json", dump({
            "parent": "minecraft:item/generated",
            "textures": {"layer0": f"{NS}:item/cobweb"},
        }))
    print("wrote", out.relative_to(ROOT))


def preview():
    """README preview: the four colours plus the item icon, on a grey background."""
    tiles = [frame(rgb) for rgb in COLOURS.values()] + [item_icon()]
    sheet = Image.new("RGBA", (len(tiles) * (SIZE + 2), SIZE + 2), (70, 70, 70, 255))
    for i, t in enumerate(tiles):
        sheet.alpha_composite(t, (i * (SIZE + 2) + 1, 1))
    sheet.resize((sheet.width * 10, sheet.height * 10), Image.NEAREST).save(ROOT / "preview.png")


if __name__ == "__main__":
    build()
    preview()
