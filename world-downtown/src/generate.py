"""Generate the LA & NYC World datapack and print the Arnis commands.

The world itself is built on your computer by Arnis (https://github.com/louis-e/arnis)
in "One World" mode. Arnis places every area in one Web Mercator frame centred on the
FIRST area generated (Hollywood). This script uses the same formulas to work out which
blocks the stations and tour signs land on, and bakes those into the datapack.

What the datapack does in game:
- Teleport stations: one button each, which opens a map menu (a dialog) of every station.
- Tour signs at landmarks (name + short fact), on solid ground near the landmark.
- Night lights: as you explore, lamp posts that switch on at night are added along the
  sidewalks of wide (main) roads, unless Arnis already put a lamp there.

Run: python3 src/generate.py
"""
import json
import math
import zipfile
from pathlib import Path

VERSION = "2.0.0"
NS = "lanyc"
PACK_NAME = f"la-nyc-teleport-{VERSION}"
DATA_FORMAT = 101  # data pack format of Minecraft 26.1
SEARCH_RADIUS = 24  # how far (blocks) to look for solid ground around a station or sign

# Areas, in the order they must be generated: the first one fixes the world's frame.
# min_lat, min_lon, max_lat, max_lon
AREAS = {
    "hollywood": ("Hollywood", (34.0856, -118.3524, 34.1144, -118.3176)),
    "downtown": ("Downtown LA", (34.0356, -118.2723, 34.0644, -118.2377)),
    "griffith": ("Griffith Park & Hollywood Sign", (34.1160, -118.3284, 34.1448, -118.2936)),
    "lax": ("LAX airport", (33.9281, -118.4223, 33.9569, -118.3877)),
    "times_square": ("Times Square & Midtown", (40.7436, -74.0045, 40.7724, -73.9665)),
    "central_park": ("Central Park", (40.7726, -73.9844, 40.8014, -73.9464)),
    "liberty": ("Statue of Liberty & Ellis Island", (40.6860, -74.0500, 40.7030, -74.0340)),
}

# Stations: key -> (menu label, lat, lon, placement). "ground" finds solid ground nearby;
# "top" sits on top of whatever is highest there (a rooftop viewpoint).
STATIONS = {
    "hollywood": ("Hollywood", 34.10166, -118.33869, "ground"),
    "hollywood_sign": ("Hollywood Sign", 34.13300, -118.32150, "ground"),
    "griffith": ("Griffith Observatory", 34.11800, -118.30040, "ground"),
    "downtown": ("Downtown LA", 34.05600, -118.24600, "ground"),
    "lax": ("LAX Terminals", 33.94330, -118.40700, "ground"),
    "theme_building": ("LAX Theme Building", 33.94380, -118.40250, "ground"),
    "times_square": ("Times Square", 40.75800, -73.98550, "ground"),
    "empire_state": ("Empire State roof", 40.74843, -73.98566, "top"),
    "central_park": ("Central Park", 40.77380, -73.97100, "ground"),
    "liberty": ("Statue of Liberty", 40.69000, -74.04550, "ground"),
}

# Tour signs: (lat, lon, four lines of at most 15 characters).
SIGNS = [
    # Hollywood
    (34.10200, -118.34090, ["TCL Chinese", "Theatre", "Opened 1927", "Star handprints"]),
    (34.10220, -118.34030, ["Dolby Theatre", "Home of the", "Oscars since", "2002"]),
    (34.10160, -118.32670, ["Hollywood Walk", "of Fame", "2,700+ stars", "since 1960"]),
    (34.10320, -118.32620, ["Capitol Records", "Opened 1956", "Shaped like a", "stack of discs"]),
    (34.11220, -118.33910, ["Hollywood Bowl", "Opened 1922", "Outdoor concert", "amphitheatre"]),
    # Griffith Park
    (34.11840, -118.30040, ["Griffith", "Observatory", "Opened 1935", "Free admission"]),
    (34.13410, -118.32150, ["Hollywood Sign", "Built 1923 as", "HOLLYWOODLAND", "Letters 14 m"]),
    # Downtown LA
    (34.05530, -118.24980, ["Walt Disney", "Concert Hall", "Frank Gehry", "Opened 2003"]),
    (34.05100, -118.25410, ["U.S. Bank Tower", "310 m tall", "Completed 1989", ""]),
    (34.05020, -118.26000, ["Wilshire Grand", "Center", "335 m (spire)", "Opened 2017"]),
    (34.05370, -118.24270, ["Los Angeles", "City Hall", "Built 1928", "138 m tall"]),
    (34.05080, -118.24890, ["Grand Central", "Market", "Open since 1917", ""]),
    (34.04300, -118.26730, ["Crypto.com", "Arena", "Opened 1999", "Home of Lakers"]),
    # LAX
    (33.94430, -118.40250, ["Theme Building", "Opened 1961", "Space Age", "landmark"]),
    (33.94330, -118.40850, ["Tom Bradley", "Intl Terminal", "Opened 1984", ""]),
    (33.94580, -118.39200, ["Los Angeles", "Intl Airport", "(LAX)", "Opened 1928"]),
    # Times Square & Midtown
    (40.75815, -73.98540, ["Times Square", "Named 1904", "New Year's ball", "drop since 1907"]),
    (40.74840, -73.98480, ["Empire State", "Building", "Opened 1931", "102 floors"]),
    (40.75320, -73.98220, ["NY Public", "Library", "Opened 1911", "Lions guard it"]),
    (40.75270, -73.97720, ["Grand Central", "Terminal", "Opened 1913", "44 platforms"]),
    (40.75870, -73.97870, ["Rockefeller", "Center", "30 Rock opened", "1933"]),
    (40.76510, -73.97990, ["Carnegie Hall", "Opened 1891", "", ""]),
    (40.75160, -73.97550, ["Chrysler", "Building", "Opened 1930", "319 m tall"]),
    (40.75050, -73.99340, ["Madison Square", "Garden", "Opened 1968", ""]),
    # Central Park
    (40.77400, -73.97080, ["Central Park", "Opened 1858", "843 acres", ""]),
    (40.77420, -73.97060, ["Bethesda", "Fountain", "Angel of the", "Waters, 1873"]),
    (40.77560, -73.97190, ["Bow Bridge", "Built 1862", "Cast iron", ""]),
    (40.77940, -73.96910, ["Belvedere", "Castle", "Built 1869", ""]),
    (40.77570, -73.97500, ["Strawberry", "Fields", "John Lennon", "memorial"]),
    (40.77940, -73.96320, ["The Met", "Museum of Art", "Founded 1870", ""]),
    (40.78550, -73.96260, ["Jacqueline", "Kennedy Onassis", "Reservoir", ""]),
    (40.78300, -73.95900, ["Guggenheim", "Museum", "Frank Lloyd", "Wright, 1959"]),
    # Statue of Liberty & Ellis Island
    (40.68920, -74.04450, ["Statue of", "Liberty", "Gift of France", "Dedicated 1886"]),
    (40.69950, -74.03960, ["Ellis Island", "Immigration", "station", "1892-1954"]),
]

# Block tags (what counts as ground, sidewalk, road) — Arnis's surface blocks.
GROUND = ["grass_block", "dirt", "coarse_dirt", "podzol", "dirt_path", "sand", "gravel",
          "smooth_stone", "gray_concrete", "light_gray_concrete", "gray_concrete_powder",
          "cyan_terracotta", "black_concrete", "white_concrete", "yellow_concrete",
          "stone_bricks", "polished_andesite", "moss_block", "rooted_dirt"]
SIDEWALK = ["smooth_stone", "gray_concrete", "light_gray_concrete", "polished_andesite", "stone_bricks"]
ASPHALT = ["gray_concrete_powder", "cyan_terracotta", "black_concrete", "white_concrete", "yellow_concrete"]
HOLLOW = ["air", "cave_air", "void_air"]
LAMP_TOP = ["iron_trapdoor", "daylight_detector"]  # Arnis's lamps / ours
LAMP_CHUNK_RADIUS = 2  # chunks around each player checked for lamps
LAMP_CHUNKS_PER_RUN = 2  # how many new chunks get lamps per run (every 10 ticks)
ROAD_CHECKS = (2, 6, 10)  # road must be asphalt at these distances: about 9+ blocks wide

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
        "scoreboard objectives add lanyc dummy",
        f"scoreboard objectives add {NS}_go trigger",
        "scoreboard players set #16 lanyc 16",
        f"execute unless data storage {NS}:state {{built:1b}} run function {NS}:setup",
        f"schedule function {NS}:lamps/loop 10t replace",
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
        'tellraw @a {"text":"LA & NYC: stations and tour signs are ready. Press a station button for the map.","color":"green"}',
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

    # Night lights
    f["lamps/loop"] = [
        f"execute as @a at @s run function {NS}:lamps/around",
        f"schedule function {NS}:lamps/loop 10t replace",
    ]
    f["lamps/around"] = [
        "# Check the chunks around this player; give a few new ones lamps.",
        f"scoreboard players set #done {NS} 0",
        f"execute store result score #cx {NS} run data get entity @s Pos[0]",
        f"execute store result score #cz {NS} run data get entity @s Pos[2]",
        f"scoreboard players operation #cx {NS} /= #16 {NS}",
        f"scoreboard players operation #cz {NS} /= #16 {NS}",
    ]
    for dx, dz in spiral_offsets(LAMP_CHUNK_RADIUS):
        if max(abs(dx), abs(dz)) > LAMP_CHUNK_RADIUS:
            continue
        f["lamps/around"] += [
            f"execute if score #done {NS} matches {LAMP_CHUNKS_PER_RUN}.. run return 0",
            f"scoreboard players operation #x {NS} = #cx {NS}",
            f"scoreboard players {'add' if dx >= 0 else 'remove'} #x {NS} {abs(dx)}",
            f"scoreboard players operation #x {NS} *= #16 {NS}",
            f"scoreboard players operation #z {NS} = #cz {NS}",
            f"scoreboard players {'add' if dz >= 0 else 'remove'} #z {NS} {abs(dz)}",
            f"scoreboard players operation #z {NS} *= #16 {NS}",
            f"execute store result storage {NS}:tmp x int 1 run scoreboard players get #x {NS}",
            f"execute store result storage {NS}:tmp z int 1 run scoreboard players get #z {NS}",
            f"execute store result score #r {NS} run function {NS}:lamps/chunk with storage {NS}:tmp",
            f"scoreboard players operation #done {NS} += #r {NS}",
        ]
    f["lamps/chunk"] = [
        f'$execute if data storage {NS}:lamps done."$(x)_$(z)" run return 0',
        "$execute unless loaded $(x) 0 $(z) run return 0",
        f'$data modify storage {NS}:lamps done."$(x)_$(z)" set value 1b',
        f"$execute positioned $(x) 0 $(z) run function {NS}:lamps/scan",
        "return 1",
    ]
    columns = [(dx, dz) for dx in range(16) for dz in range(16)]
    f["lamps/scan"] = ["# Skip chunks that already have a lamp (Arnis's or ours)."]
    f["lamps/scan"] += [
        f"execute positioned ~{dx + 0.5} 0 ~{dz + 0.5} positioned over motion_blocking_no_leaves "
        f"if block ~ ~-1 ~ #{NS}:lamp_top run return 0" for dx, dz in columns]
    f["lamps/scan"] += ["# Put one lamp on the first sidewalk beside a main road."]
    f["lamps/scan"] += [
        f"execute positioned ~{dx + 0.5} 0 ~{dz + 0.5} positioned over motion_blocking_no_leaves "
        f"if function {NS}:lamps/try run return 1" for dx, dz in columns]
    f["lamps/try"] = [
        f"execute unless block ~ ~-1 ~ #{NS}:sidewalk run return fail",
        f"execute if block ~ ~-3 ~ #{NS}:hollow run return fail",
    ]
    for d, (ux, uz) in {"n": (0, -1), "s": (0, 1), "e": (1, 0), "w": (-1, 0)}.items():
        f["lamps/try"].append(f"execute if function {NS}:lamps/road_{d} run return run function {NS}:lamps/place")
        f[f"lamps/road_{d}"] = [
            f"execute positioned ~{ux * k} ~ ~{uz * k} positioned over motion_blocking_no_leaves "
            f"unless block ~ ~-1 ~ #{NS}:asphalt run return fail" for k in ROAD_CHECKS] + ["return 1"]
    f["lamps/try"].append("return fail")
    f["lamps/place"] = [
        "# Lamp post that switches on at night (inverted daylight sensor on top).",
        "setblock ~ ~ ~ smooth_stone",
        "fill ~ ~1 ~ ~ ~3 ~ stone_brick_wall",
        "setblock ~ ~4 ~ redstone_lamp",
        "setblock ~ ~5 ~ daylight_detector[inverted=true]",
        "return 1",
    ]
    return f


def dialog():
    return {
        "type": "minecraft:multi_action",
        "title": {"text": "LA & NYC map", "color": "gold"},
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
            "description": f"LA & NYC World: stations, tour signs, night lights v{VERSION}",
            "min_format": DATA_FORMAT,
            "max_format": 1000,
        }}, indent=2))
        z.writestr("data/minecraft/tags/function/load.json", json.dumps({"values": [f"{NS}:load"]}, indent=2))
        z.writestr("data/minecraft/tags/function/tick.json", json.dumps({"values": [f"{NS}:tick"]}, indent=2))
        for tag, blocks in {"ground": GROUND, "sidewalk": SIDEWALK, "asphalt": ASPHALT,
                            "hollow": HOLLOW, "lamp_top": LAMP_TOP}.items():
            z.writestr(f"data/{NS}/tags/block/{tag}.json", json.dumps({"values": blocks}, indent=2))
        z.writestr(f"data/{NS}/dialog/menu.json", json.dumps(dialog(), indent=2))
        for name, lines in functions().items():
            z.writestr(f"data/{NS}/function/{name}.mcfunction", "\n".join(lines) + "\n")
    print("wrote", out)


def commands():
    print("\nArnis commands (run in this order; add --output-dir):")
    for i, (key, (name, (a, b, c, d))) in enumerate(AREAS.items()):
        spawn = ""
        if i == 0:
            _, lat, lon, _ = STATIONS["hollywood"]
            spawn = f" --spawn-lat {lat} --spawn-lng {lon}"
        print(f'  {name}: --one-world --world-name="LA and NYC" --interior --signage full '
              f'--bbox="{a},{b},{c},{d}"{spawn}')
    print("\nStation block coordinates (before the ground search):")
    for key, (label, lat, lon, _) in STATIONS.items():
        x, z = to_block(lat, lon)
        print(f"  {label}: x={x} z={z}")


if __name__ == "__main__":
    build()
    commands()
