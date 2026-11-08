"""Generate the Low Shield Texture Pack variants.

Overrides the shield's item model display transforms so it is drawn
smaller (and lower in first person), both when carried and when blocking.
Only transform numbers are changed; the shield's look comes from the game.
Run: python3 src/generate.py
"""
import io
import json
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw

MIN_FORMAT = 66     # resource pack formats 66+ = 26.1 and earlier 1.21.x releases
MAX_FORMAT = 1000   # no upper bound, so newer versions don't flag it as incompatible
VERSION = "1.0.0"

# name -> (size relative to vanilla, how far to drop it in first person, in 1/16 block)
VARIANTS = {"small": (0.75, 1.0), "smaller": (0.55, 2.0), "smallest": (0.40, 3.0)}

ROOT = Path(__file__).resolve().parent.parent

# Vanilla 26.1 transforms for the display slots we change.
# Slots not listed here (gui, ground, item frames, shelves) stay vanilla.
CARRY = {
    "thirdperson_righthand": ([0, 90, 0], [10, 6, -4], 1.0),
    "thirdperson_lefthand": ([0, 90, 0], [10, 6, 12], 1.0),
    "firstperson_righthand": ([0, 180, 5], [-10, 1.75, -10], 1.25),
    "firstperson_lefthand": ([0, 180, 5], [10, 0, -10], 1.25),
}
CARRY_KEEP = {
    "gui": ([15, -25, -5], [2, 3, 0], 0.65),
    "fixed": ([0, 180, 0], [-4.5, 4.5, -5], 0.55),
    "on_shelf": ([0, 0, 0], [11, 18.5, 8.7], 1.4),
    "ground": ([0, 0, 0], [2, 4, 2], 0.25),
}
BLOCK = {
    "thirdperson_righthand": ([45, 155, 0], [-3.49, 11, -2], 1.0),
    "thirdperson_lefthand": ([45, 155, 0], [11.51, 7, 2.5], 1.0),
    "firstperson_righthand": ([0, 180, -5], [-15, 3.25, -11], 1.25),
    "firstperson_lefthand": ([0, 180, -5], [5, 5, -11], 1.25),
}
BLOCK_KEEP = {
    "gui": ([15, -25, -5], [2, 3, 0], 0.65),
}


def slot(rotation, translation, scale):
    return {"rotation": rotation, "translation": translation, "scale": [round(scale, 4)] * 3}


def model(changed, kept, size, drop):
    display = {}
    for name, (rot, tr, sc) in changed.items():
        tr = list(tr)
        if name.startswith("firstperson"):
            tr[1] = round(tr[1] - drop, 4)
        display[name] = slot(rot, tr, sc * size)
    for name, (rot, tr, sc) in kept.items():
        display[name] = slot(rot, list(tr), sc)
    return {
        "gui_light": "front",
        "textures": {"particle": "block/dark_oak_planks"},
        "display": display,
    }


def pack_icon():
    # simple original shield emblem
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.polygon([(3, 2), (12, 2), (12, 9), (7.5, 14), (3, 9)], fill=(120, 84, 48, 255))
    d.polygon([(4, 3), (11, 3), (11, 9), (7.5, 12.6), (4, 9)], fill=(176, 128, 74, 255))
    d.line([(7, 3), (7, 12)], fill=(150, 150, 160, 255))
    d.line([(8, 3), (8, 12)], fill=(150, 150, 160, 255))
    d.line([(4, 7), (11, 7)], fill=(150, 150, 160, 255))
    buf = io.BytesIO()
    img.resize((64, 64), Image.NEAREST).save(buf, "PNG")
    return buf.getvalue()


def build(name, size, drop):
    pct = round(size * 100)
    mcmeta = {"pack": {
        "description": f"Low Shield ({name.title()}, {pct}%) v{VERSION}",
        "min_format": MIN_FORMAT,
        "max_format": MAX_FORMAT,
    }}
    out = ROOT / "release" / f"low-shield-texture-pack-{name}-{VERSION}.zip"
    out.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("pack.mcmeta", json.dumps(mcmeta, indent=2))
        z.writestr("pack.png", pack_icon())
        z.writestr("assets/minecraft/models/item/shield.json",
                   json.dumps(model(CARRY, CARRY_KEEP, size, drop), indent=2))
        z.writestr("assets/minecraft/models/item/shield_blocking.json",
                   json.dumps(model(BLOCK, BLOCK_KEEP, size, drop), indent=2))
    print("wrote", out.relative_to(ROOT))


if __name__ == "__main__":
    for name, (size, drop) in VARIANTS.items():
        build(name, size, drop)
