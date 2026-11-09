"""Generate the Disneyland world datapack and print the Arnis command.

The world itself is built on your computer by Arnis (https://github.com/louis-e/arnis)
as a normal standalone world (--projection web_mercator --vanilla-height). Arnis centres
that world on the area, using a Web Mercator frame; this script uses the same formulas to
work out which blocks the stations and tour signs land on, and bakes those into the datapack.

What the datapack does in game:
- Teleport stations: one button each, which opens a map menu (a dialog) of every station.
- Tour signs at landmarks (name + short fact), on solid ground near the landmark.

Run: python3 src/generate.py
"""
import json
import math
import zipfile
from pathlib import Path

VERSION = "1.1.0"
NS = "dl"
PACK_NAME = f"disneyland-datapack-{VERSION}"
DATA_FORMAT = 101  # data pack format of Minecraft 26.1
SEARCH_RADIUS = 24  # how far (blocks) to look for solid ground around a station or sign

# The area: Disneyland Resort (both parks, Downtown Disney, hotels). min_lat, min_lon, max_lat, max_lon
AREAS = {
    "resort": ("Disneyland Resort", (33.8020, -117.9290, 33.8180, -117.9130)),
}

# Stations: key -> (menu label, lat, lon, placement). "ground" finds solid ground nearby.
STATIONS = {
    "main_street": ("Main Street, U.S.A.", 33.81050, -117.91895, "ground"),
    "castle": ("Sleeping Beauty Castle", 33.81220, -117.91900, "ground"),
    "fantasyland": ("Fantasyland", 33.81420, -117.91880, "ground"),
    "tomorrowland": ("Tomorrowland", 33.81180, -117.91720, "ground"),
    "new_orleans": ("New Orleans Square", 33.81130, -117.92130, "ground"),
    "galaxys_edge": ("Galaxy's Edge", 33.81500, -117.92250, "ground"),
    "dca": ("California Adventure", 33.80780, -117.91880, "ground"),
    "cars_land": ("Cars Land", 33.80580, -117.91950, "ground"),
    "pixar_pier": ("Pixar Pier", 33.80480, -117.92150, "ground"),
    "avengers": ("Avengers Campus", 33.80680, -117.91720, "ground"),
    "downtown_disney": ("Downtown Disney", 33.80950, -117.92280, "ground"),
    "hotel": ("Disneyland Hotel", 33.80900, -117.92580, "ground"),
}

# Tour signs: (lat, lon, four lines of at most 15 characters).
SIGNS = [
    (33.81030, -117.91900, ["Disneyland", "Opened", "July 17, 1955", ""]),
    (33.81070, -117.91880, ["Disneyland", "Railroad", "Since 1955", ""]),
    (33.81230, -117.91900, ["Sleeping Beauty", "Castle", "Opened 1955", "23 m tall"]),
    (33.81300, -117.91790, ["Matterhorn", "Bobsleds", "Opened 1959", ""]),
    (33.81130, -117.92190, ["Pirates of the", "Caribbean", "Opened 1967", ""]),
    (33.81170, -117.92240, ["Haunted", "Mansion", "Opened 1969", ""]),
    (33.81100, -117.91700, ["Space Mountain", "Opened 1977", "", ""]),
    (33.81500, -117.92280, ["Star Wars:", "Galaxy's Edge", "Opened 2019", ""]),
    (33.80800, -117.91880, ["Disney", "California", "Adventure", "Opened 2001"]),
    (33.80600, -117.91950, ["Cars Land", "Opened 2012", "", ""]),
    (33.80470, -117.92120, ["Pixar Pier", "Opened 2018", "", ""]),
    (33.80710, -117.91720, ["Avengers", "Campus", "Opened 2021", ""]),
    (33.80960, -117.92260, ["Downtown", "Disney", "Opened 2001", ""]),
    (33.80900, -117.92600, ["Disneyland", "Hotel", "Opened 1955", ""]),
]

# Block tags: what counts as solid ground to build on (Arnis's surface blocks), and air.
GROUND = ["grass_block", "dirt", "coarse_dirt", "podzol", "dirt_path", "sand", "gravel",
          "smooth_stone", "gray_concrete", "light_gray_concrete", "gray_concrete_powder",
          "cyan_terracotta", "black_concrete", "white_concrete", "yellow_concrete",
          "stone_bricks", "polished_andesite", "moss_block", "rooted_dirt"]
HOLLOW = ["air", "cave_air", "void_air"]

# Same as Arnis src/projection/web_mercator.rs
EARTH_RADIUS = 6_371_000.0
SCALE = 1.0  # blocks per metre


def mercator_y(lat):
    return EARTH_RADIUS * math.log(math.tan(math.pi / 4 + math.radians(lat) / 2))


def frame():
    min_lat, min_lon, max_lat, max_lon = next(iter(AREAS.values()))[1]
    # Arnis (standalone world, --projection web_mercator): origin = centre of the area.
    return (min_lat + max_lat) / 2, (min_lon + max_lon) / 2


def to_block(lat, lon):
    origin_lat, origin_lon = frame()
    k = SCALE * math.cos(math.radians(origin_lat))
    x = EARTH_RADIUS * math.radians(lon - origin_lon) * k
    z = -(mercator_y(lat) - mercator_y(origin_lat)) * k
    return math.floor(x), math.floor(z)


def check_inside_areas():
    for name, lat, lon in [(v[0], v[1], v[2]) for v in STATIONS.values()] + [(s[2][0], s[0], s[1]) for s in SIGNS]:
        if not any(a <= lat <= c and b <= lon <= d for _, (a, b, c, d) in AREAS.values()):
            raise SystemExit(f"{name} ({lat}, {lon}) is outside every area")


def spiral_offsets(radius):
    pts = [(dx, dz) for dx in range(-radius, radius + 1) for dz in range(-radius, radius + 1)
           if dx * dx + dz * dz <= radius * radius]
    return sorted(pts, key=lambda p: (p[0] ** 2 + p[1] ** 2, p))


def text(s):
    return json.dumps(s)


def functions():
    f = {}
    targets = []  # (id, x, z, mode)
    for key, (_, lat, lon, mode) in STATIONS.items():
        x, z = to_block(lat, lon)
        targets.append((f"station_{key}", x, z, mode))
    for i, (lat, lon, _) in enumerate(SIGNS):
        x, z = to_block(lat, lon)
        targets.append((f"sign_{i}", x, z, "ground"))

    f["load"] = [
        f"scoreboard objectives add {NS} dummy",
        f"scoreboard objectives add {NS}_go trigger",
        f"scoreboard players set #16 {NS} 16",
        f"execute unless data storage {NS}:state {{built:1b}} run function {NS}:setup",
    ]
    f["setup"] = ["# Load each station's and sign's chunk while they are built."]
    f["setup"] += sorted({f"forceload add {x} {z}" for _, x, z, _ in targets})
    f["setup"] += [f"schedule function {NS}:build 20t"]
    f["build"] = ["# Wait until every chunk is loaded, then build one item per tick."]
    f["build"] += sorted({f"execute unless loaded {x} 0 {z} run return run schedule function {NS}:build 20t"
                          for _, x, z, _ in targets})
    f["build"] += [f"function {NS}:build/0"]
    for i, (tid, x, z, mode) in enumerate(targets):
        lines = [f'data modify storage {NS}:tmp id set value "{tid}"']
        if mode == "top":
            lines.append(f"execute positioned {x + 0.5} 0 {z + 0.5} positioned over motion_blocking run function {NS}:put/{tid}")
        else:
            lines.append(f"execute positioned {x + 0.5} 0 {z + 0.5} run function {NS}:find_ground")
        nxt = f"build/{i + 1}" if i + 1 < len(targets) else "build/done"
        lines.append(f"schedule function {NS}:{nxt} 1t")
        f[f"build/{i}"] = lines
    f["build/done"] = sorted({f"forceload remove {x} {z}" for _, x, z, _ in targets}) + [
        f"data modify storage {NS}:state built set value 1b",
        'tellraw @a {"text":"Disneyland: stations and tour signs are ready. Press a station button for the map.","color":"green"}',
    ]

    # Ground search: nearest column within SEARCH_RADIUS whose top is ground (not a roof).
    f["find_ground"] = ["# Spiral out from here to the nearest solid ground; fall back to the top block."]
    for dx, dz in spiral_offsets(SEARCH_RADIUS):
        f["find_ground"].append(
            f"execute positioned ~{dx} 0 ~{dz} positioned over motion_blocking_no_leaves "
            f"if function {NS}:ground_ok run return run function {NS}:found with storage {NS}:tmp")
    f["find_ground"].append(
        f"execute positioned over motion_blocking_no_leaves run function {NS}:found with storage {NS}:tmp")
    f["found"] = [f"$function {NS}:put/$(id)"]
    f["ground_ok"] = [
        "# Standing here: ground underfoot, and solid below it (a roof has rooms or air under it).",
        f"execute unless block ~ ~-1 ~ #{NS}:ground run return fail",
        f"execute if block ~ ~-3 ~ #{NS}:hollow run return fail",
        f"execute if block ~ ~-4 ~ #{NS}:hollow run return fail",
        "# Not the top of a wall or ledge: no drop of more than 3 blocks right next to it.",
        f"execute if block ~1 ~-4 ~ #{NS}:hollow run return fail",
        f"execute if block ~-1 ~-4 ~ #{NS}:hollow run return fail",
        f"execute if block ~ ~-4 ~1 #{NS}:hollow run return fail",
        f"execute if block ~ ~-4 ~-1 #{NS}:hollow run return fail",
        "return 1",
    ]

    # Stations
    for key, (label, _, _, _) in STATIONS.items():
        tid = f"station_{key}"
        f[f"put/{tid}"] = [
            f"# {label} station, built here (standing level).",
            f'summon marker ~ ~ ~1 {{Tags:["{NS}_tmp"]}}',
            f"execute as @e[type=marker,tag={NS}_tmp,limit=1] run function {NS}:store/{key}",
            f"kill @e[type=marker,tag={NS}_tmp]",
            f"function {NS}:station/structure",
            f"setblock ~ ~2 ~-1 oak_wall_sign[facing=south]{{is_waxed:1b,front_text:{{has_glowing_text:1b,"
            f"messages:[{text('Station')},{text(label)},{text('Press button')},{text('for map menu')}]}}}}",
        ]
        f[f"store/{key}"] = [
            f"execute store result storage {NS}:stations {key}.{axis} double 0.5 run data get entity @s Pos[{i}] 2"
            for i, axis in enumerate("xyz")
        ]
        f[f"go/{key}"] = [
            f"# Teleport yourself to the {label} station.",
            f'execute unless data storage {NS}:stations {key} run return run tellraw @s {{"text":"That station is not built yet.","color":"red"}}',
            f"function {NS}:tp with storage {NS}:stations {key}",
            f'tellraw @s {{"text":"Welcome to {label}!","color":"gold"}}',
        ]
        f[f"move/{key}"] = [
            f"# Rebuild the {label} station where you are standing.",
            f"execute align xz positioned ~0.5 ~ ~0.5 run function {NS}:put/{tid}",
            f'tellraw @s {{"text":"{label} station moved here.","color":"green"}}',
        ]
    f["tp"] = ["$tp @s $(x) $(y) $(z) 180 0"]
    f["tick"] = [
        "# Map menu buttons set this trigger; teleport whoever pressed one.",
        f"scoreboard players enable @a {NS}_go",
        f"execute as @a[scores={{{NS}_go=1..}}] at @s run function {NS}:menu_choice",
    ]
    f["menu_choice"] = [
        f"execute if score @s {NS}_go matches {i + 1} run function {NS}:go/{key}"
        for i, key in enumerate(STATIONS)
    ] + [f"scoreboard players set @s {NS}_go 0"]
    f["menu"] = [f"dialog show @s {NS}:menu"]
    f["station/structure"] = [
        "# Platform, a short wall with one button that opens the map menu. You stand 2 in front.",
        "fill ~-2 ~ ~-3 ~2 ~4 ~2 air",
        "fill ~-2 ~-1 ~-3 ~2 ~-1 ~2 smooth_stone",
        "fill ~-1 ~ ~-2 ~1 ~2 ~-2 smooth_stone",
        "setblock ~-1 ~2 ~-2 sea_lantern",
        "setblock ~1 ~2 ~-2 sea_lantern",
        f'setblock ~ ~1 ~-2 command_block[facing=up]{{Command:"execute as @p run function {NS}:menu"}}',
        "setblock ~ ~1 ~-1 stone_button[face=wall,facing=south]",
    ]

    # Tour signs
    for i, (_, _, lines) in enumerate(SIGNS):
        msgs = "[" + ",".join(text(s) for s in lines) + "]"
        side = f"{{has_glowing_text:1b,messages:{msgs}}}"
        f[f"put/sign_{i}"] = [
            f"# Tour sign: {' / '.join(s for s in lines if s)}",
            "setblock ~ ~ ~ stone_brick_wall",
            f"setblock ~ ~1 ~ oak_sign[rotation=0]{{is_waxed:1b,front_text:{side},back_text:{side}}}",
        ]

    return f


def dialog():
    return {
        "type": "minecraft:multi_action",
        "title": {"text": "Disneyland map", "color": "gold"},
        "body": {"type": "minecraft:plain_message", "contents": "Where would you like to go?"},
        "columns": 2,
        "actions": [
            # /trigger needs no permissions, so the game runs it without a confirmation screen.
            {"label": label, "action": {"type": "minecraft:run_command", "command": f"trigger {NS}_go set {i + 1}"}}
            for i, (key, (label, _, _, _)) in enumerate(STATIONS.items())
        ],
        "exit_action": {"label": "Close"},
    }


def build():
    check_inside_areas()
    out = Path(__file__).resolve().parent.parent / "release" / f"{PACK_NAME}.zip"
    out.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("pack.mcmeta", json.dumps({"pack": {
            "description": f"Disneyland: stations and tour signs v{VERSION}",
            "min_format": DATA_FORMAT,
            "max_format": 1000,
        }}, indent=2))
        z.writestr("data/minecraft/tags/function/load.json", json.dumps({"values": [f"{NS}:load"]}, indent=2))
        z.writestr("data/minecraft/tags/function/tick.json", json.dumps({"values": [f"{NS}:tick"]}, indent=2))
        for tag, blocks in {"ground": GROUND, "hollow": HOLLOW}.items():
            z.writestr(f"data/{NS}/tags/block/{tag}.json", json.dumps({"values": blocks}, indent=2))
        z.writestr(f"data/{NS}/dialog/menu.json", json.dumps(dialog(), indent=2))
        for name, lines in functions().items():
            z.writestr(f"data/{NS}/function/{name}.mcfunction", "\n".join(lines) + "\n")
    print("wrote", out)


def arnis_args():
    """The Arnis options for this world (no --output-dir). Also used by the GitHub build."""
    (a, b, c, d) = next(iter(AREAS.values()))[1]
    _, lat, lon, _ = STATIONS[next(iter(STATIONS))]
    return [f"--bbox={a},{b},{c},{d}", "--projection", "web_mercator", "--vanilla-height",
            "--signage", "full", "--spawn-lat", str(lat), "--spawn-lng", str(lon)]


def commands():
    args = arnis_args()
    (Path(__file__).resolve().parent / "arnis-args.txt").write_text("\n".join(args) + "\n")
    print("\nArnis command (add --output-dir):")
    print("  " + " ".join(f'"{x}"' if "," in x else x for x in args))
    print("\nStation block coordinates (before the ground search):")
    for key, (label, lat, lon, _) in STATIONS.items():
        x, z = to_block(lat, lon)
        print(f"  {label}: x={x} z={z}")


if __name__ == "__main__":
    build()
    commands()
