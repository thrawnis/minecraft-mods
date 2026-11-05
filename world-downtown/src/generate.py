"""Generate the LA & NYC World teleport datapack and print the Arnis commands.

The world itself is built on your computer by Arnis (https://github.com/louis-e/arnis)
in "One World" mode. Arnis places every area in one Web Mercator frame centred on the
FIRST area generated (Hollywood). This script uses the same formulas to work out where
each teleport station lands, and bakes those block coordinates into the datapack.

Run: python3 src/generate.py
"""
import json
import math
import zipfile
from pathlib import Path

VERSION = "1.0.0"
NS = "lanyc"
PACK_NAME = f"la-nyc-teleport-{VERSION}"
DATA_FORMAT = 101  # data pack format of Minecraft 26.1

# Areas, in the order they must be generated: the first one fixes the world's frame.
# Each is about 3.2 km x 3.2 km (~10 km²): min_lat, min_lon, max_lat, max_lon.
AREAS = {
    "hollywood": ("Hollywood", (34.0856, -118.3524, 34.1144, -118.3176)),
    "downtown": ("Downtown LA", (34.0356, -118.2723, 34.0644, -118.2377)),
    "times_square": ("Times Square", (40.7436, -74.0045, 40.7724, -73.9665)),
}
# Station spots: open ground in each area (lat, lon).
STATIONS = {
    "hollywood": (34.10166, -118.33869),   # Hollywood Blvd & Highland Ave
    "downtown": (34.05600, -118.24600),    # Grand Park
    "times_square": (40.75800, -73.98550),  # Times Square plaza
}

# Same as Arnis src/projection/web_mercator.rs
EARTH_RADIUS = 6_371_000.0
SCALE = 1.0  # blocks per metre


def mercator_y(lat):
    return EARTH_RADIUS * math.log(math.tan(math.pi / 4 + math.radians(lat) / 2))


def frame():
    min_lat, min_lon, max_lat, max_lon = next(iter(AREAS.values()))[1]
    # Arnis: origin = centre of the first requested area, stored rounded to 7 decimals.
    return round((min_lat + max_lat) / 2, 7), round((min_lon + max_lon) / 2, 7)


def to_block(lat, lon):
    origin_lat, origin_lon = frame()
    k = SCALE * math.cos(math.radians(origin_lat))
    x = EARTH_RADIUS * math.radians(lon - origin_lon) * k
    z = -(mercator_y(lat) - mercator_y(origin_lat)) * k
    return math.floor(x), math.floor(z)


def station_blocks():
    return {key: to_block(*STATIONS[key]) for key in AREAS}


def functions():
    blocks = station_blocks()
    f = {}
    f["load"] = [
        "# Build the teleport stations the first time the world loads.",
        f"execute unless data storage {NS}:state {{built:1b}} run function {NS}:setup",
    ]
    f["setup"] = ["# Keep each station's chunk loaded so teleports can find it."]
    f["setup"] += [f"forceload add {x} {z}" for x, z in blocks.values()]
    f["setup"] += [f"schedule function {NS}:build 20t"]
    f["build"] = ["# Wait until every station's chunk is loaded."]
    f["build"] += [f"execute unless loaded {x} 0 {z} run return run schedule function {NS}:build 20t"
                   for x, z in blocks.values()]
    for key, (x, z) in blocks.items():
        f["build"].append(
            f"execute positioned {x + 0.5} 0 {z + 0.5} positioned over motion_blocking_no_leaves run function {NS}:station/{key}")
    f["build"] += [
        f"data modify storage {NS}:state built set value 1b",
        'tellraw @a {"text":"LA & NYC teleport stations are ready.","color":"green"}',
    ]
    for key, (name, _) in AREAS.items():
        f[f"station/{key}"] = [
            f"# Station for {name}, built at the current position (standing level).",
            f"kill @e[type=marker,tag={NS}_{key}]",
            f'summon marker ~ ~ ~ {{Tags:["{NS}","{NS}_{key}"]}}',
            f"function {NS}:station/structure",
        ]
        f[f"go/{key}"] = [
            f"# Teleport the nearest player (the one who pressed the button) to {name}.",
            f"execute as @p at @e[type=marker,tag={NS}_{key},limit=1] run tp @s ~ ~ ~1 180 0",
            f'tellraw @p {{"text":"Welcome to {name}!","color":"gold"}}',
        ]
        f[f"move/{key}"] = [
            f"# Rebuild the {name} station where you are standing.",
            f"execute at @e[type=marker,tag={NS}_{key}] run forceload remove ~ ~",
            "forceload add ~ ~",
            f"execute align xz positioned ~0.5 ~ ~0.5 run function {NS}:station/{key}",
            f'tellraw @s {{"text":"{name} station moved here.","color":"green"}}',
        ]
    sign = 'oak_wall_sign[facing=south]{{front_text:{{messages:["","{}","",""]}}}}'
    buttons = list(AREAS.items())
    f["station/structure"] = [
        "# Platform with a wall and three buttons (one per area); you stand 2 blocks in front.",
        "# Buttons are 2 apart: neighbouring command blocks would pass the signal on and all fire.",
        "fill ~-3 ~ ~-3 ~3 ~4 ~2 air",
        "fill ~-3 ~-1 ~-3 ~3 ~-1 ~2 smooth_stone",
        "fill ~-3 ~ ~-2 ~3 ~2 ~-2 smooth_stone",
        "setblock ~-3 ~2 ~-2 sea_lantern",
        "setblock ~3 ~2 ~-2 sea_lantern",
    ]
    for dx, (key, (name, _)) in zip((-2, 0, 2), buttons):
        f["station/structure"] += [
            f'setblock ~{dx} ~1 ~-2 command_block[facing=up]{{Command:"function {NS}:go/{key}"}}',
            f"setblock ~{dx} ~1 ~-1 stone_button[face=wall,facing=south]",
            f"setblock ~{dx} ~2 ~-1 " + sign.format(name),
        ]
    return f


def build():
    out = Path(__file__).resolve().parent.parent / "release" / f"{PACK_NAME}.zip"
    out.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("pack.mcmeta", json.dumps({"pack": {
            "description": f"LA & NYC World teleport stations v{VERSION}",
            "min_format": DATA_FORMAT,
            "max_format": 1000,
        }}, indent=2))
        z.writestr("data/minecraft/tags/function/load.json", json.dumps({"values": [f"{NS}:load"]}, indent=2))
        for name, lines in functions().items():
            z.writestr(f"data/{NS}/function/{name}.mcfunction", "\n".join(lines) + "\n")
    print("wrote", out)


def commands():
    print("\nArnis commands (run in this order):")
    for i, (key, (name, (a, b, c, d))) in enumerate(AREAS.items()):
        spawn = ""
        if i == 0:
            spawn = f' --spawn-lat {STATIONS[key][0]} --spawn-lng {STATIONS[key][1]}'
        print(f'  {name}: --one-world --world-name="LA and NYC" --bbox="{a},{b},{c},{d}"{spawn}')
    print("\nStation block coordinates:")
    for key, (x, z) in station_blocks().items():
        print(f"  {AREAS[key][0]}: x={x} z={z}")


if __name__ == "__main__":
    build()
    commands()
