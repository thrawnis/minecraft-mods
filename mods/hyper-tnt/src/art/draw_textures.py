"""Draws the original 16x16 textures for Hyper TNT and the Detonator.
Run: python3 src/art/draw_textures.py"""
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
TEX = ROOT / "src/main/resources/assets/hypertnt/textures"

P_DARK, P_MID, P_LIGHT = (58, 16, 84), (104, 34, 140), (156, 70, 200)
BAND, YELLOW, BLACK = (24, 20, 28), (255, 214, 40), (20, 16, 24)


def side():
    im = Image.new("RGBA", (16, 16))
    for y in range(16):
        for x in range(16):
            # vertical sticks of explosive, 4 px wide, with a light edge and a dark seam
            k = x % 4
            c = P_DARK if k == 3 else (P_LIGHT if k == 0 else P_MID)
            im.putpixel((x, y), c + (255,))
    # hazard band across the middle: yellow/black chevrons
    for y in range(6, 10):
        for x in range(16):
            stripe = ((x + y) // 2) % 2 == 0
            im.putpixel((x, y), (YELLOW if stripe else BLACK) + (255,))
    for x in range(16):
        im.putpixel((x, 5), BAND + (255,))
        im.putpixel((x, 10), BAND + (255,))
    return im


def top():
    im = Image.new("RGBA", (16, 16), P_DARK + (255,))
    # ends of the sticks: 4x4 circles
    for cy in (2, 6, 10, 14):
        for cx in (2, 6, 10, 14):
            for dy in (-1, 0):
                for dx in (-1, 0):
                    im.putpixel((cx + dx, cy + dy), P_LIGHT + (255,))
            im.putpixel((cx - 2 if cx > 2 else cx + 1, cy - 2 if cy > 2 else cy + 1), P_MID + (255,))
    # glowing core in the middle
    for y in range(6, 10):
        for x in range(6, 10):
            im.putpixel((x, y), YELLOW + (255,))
    for (x, y) in ((7, 7), (8, 8)):
        im.putpixel((x, y), (255, 255, 200, 255))
    return im


def bottom():
    im = Image.new("RGBA", (16, 16), P_DARK + (255,))
    for y in range(16):
        for x in range(16):
            if (x + y) % 5 == 0:
                im.putpixel((x, y), P_MID + (255,))
    return im


def detonator():
    im = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    body, edge, light = (90, 92, 100), (50, 52, 58), (140, 142, 150)
    for y in range(6, 15):
        for x in range(4, 12):
            c = edge if x in (4, 11) or y in (6, 14) else body
            im.putpixel((x, y), c + (255,))
    for x in range(5, 11):
        im.putpixel((x, 7), light + (255,))
    # big red button
    for y in range(9, 12):
        for x in range(6, 10):
            im.putpixel((x, y), (210, 30, 30, 255))
    im.putpixel((6, 9), (255, 110, 110, 255))
    # green ready light
    im.putpixel((9, 13), (60, 230, 80, 255))
    # antenna with red tip
    for y in range(1, 6):
        im.putpixel((10, y), (30, 30, 34, 255))
    im.putpixel((10, 0), (255, 50, 50, 255))
    return im


if __name__ == "__main__":
    (TEX / "block").mkdir(parents=True, exist_ok=True)
    (TEX / "item").mkdir(parents=True, exist_ok=True)
    side().save(TEX / "block/hyper_tnt_side.png")
    top().save(TEX / "block/hyper_tnt_top.png")
    bottom().save(TEX / "block/hyper_tnt_bottom.png")
    detonator().save(TEX / "item/detonator.png")
    # preview for the README
    sheet = Image.new("RGBA", (16 * 4 + 12, 16), (70, 70, 70, 255))
    for i, im in enumerate((side(), top(), bottom(), detonator())):
        sheet.alpha_composite(im, (i * 20, 0))
    sheet.resize((sheet.width * 8, sheet.height * 8), Image.NEAREST).save(ROOT / "preview.png")
    print("textures written")
