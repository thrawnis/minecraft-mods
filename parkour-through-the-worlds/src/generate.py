"""Generate the Parkour Through the Worlds datapack (and the path file the bot test uses).

The course is described below as zones of jumps. Each jump is an offset from the block you
stand on to the next one: (forward, up, sideways), plus what you land on. The script turns
that into block placements, checkpoints and the game logic (timer, falls, leaderboard).

Run: python3 src/generate.py
"""
import json
import zipfile
from pathlib import Path

VERSION = "1.0.0"
NS = "ptw"
DATA_FORMAT = 101  # data pack format of Minecraft 26.1
BUILD_Y = 200      # the course floats at this height in any world

ROOT = Path(__file__).resolve().parent.parent

DIRS = {"E": (1, 0), "S": (0, 1), "W": (-1, 0), "N": (0, -1)}
YAW = {"E": -90, "S": 0, "W": 90, "N": 180}
FACING = {(1, 0): "east", (-1, 0): "west", (0, 1): "south", (0, -1): "north"}

# Jump kinds: "b" = the zone's block, "alt" = its second block, "pad:L" = an L-long runway
# of the zone's pad block, "ladder:H" / "vine:H" = a wall H high you climb, then stand on top,
# "fence" = land on a fence/wall post, "rod" = land on an end rod, "ice:L" = blue-ice runway.
ZONES = [
    {"name": "Plains", "dir": "E", "block": "grass_block", "alt": "oak_planks", "pad": "moss_block",
     "decor": ["oak_log", "oak_leaves[persistent=true]"], "light": "lantern",
     "jumps": [(2, 0, 0, "b"), (3, 0, 0, "b"), (2, 1, 0, "alt"), (3, 0, 1, "b"), (3, 0, -1, "b"),
               (2, 1, 0, "alt"), (3, 0, 0, "pad:3"), (3, -1, 1, "b"), (2, 1, 0, "alt"), (3, 0, 0, "b"),
               (3, 0, -1, "b"), (2, 1, 0, "alt")]},
    {"name": "Jungle", "dir": "S", "block": "jungle_log", "alt": "mossy_cobblestone", "pad": "jungle_planks",
     "decor": ["jungle_log", "jungle_leaves[persistent=true]"], "light": "lantern",
     "jumps": [(3, 0, 0, "b"), (4, 0, 0, "b"), (3, 1, 0, "alt"), (4, 0, 1, "b"), (3, 0, 0, "vine:4"),
               (3, 0, 0, "b"), (4, -1, 0, "alt"), (4, 0, -1, "b"), (3, 1, 0, "b"), (4, 0, 0, "pad:2"),
               (3, 1, 1, "alt"), (4, 0, 0, "b")]},
    {"name": "Desert", "dir": "E", "block": "sandstone", "alt": "chiseled_sandstone", "pad": "smooth_sandstone",
     "decor": ["sandstone", "cut_sandstone"], "light": "lantern",
     "jumps": [(4, 0, 0, "b"), (3, 1, 0, "alt"), (4, 0, 1, "b"), (5, -1, 0, "b"), (3, 1, -1, "alt"),
               (4, 0, 0, "b"), (3, 0, 0, "fence"), (4, 0, 2, "b"), (4, 0, 0, "alt"), (5, -1, 0, "b"),
               (3, 1, 0, "b"), (4, 0, -1, "alt")]},
    {"name": "Ocean", "dir": "N", "block": "prismarine", "alt": "sea_lantern", "pad": "dark_prismarine",
     "decor": ["prismarine_bricks", "tube_coral_block"], "light": "sea_lantern",
     "jumps": [(4, 0, 0, "b"), (3, 1, 0, "alt"), (4, 0, 0, "b"), (3, 0, 0, "ladder:5"), (4, 0, 0, "b"),
               (5, -1, 0, "alt"), (3, 1, 0, "b"), (4, 0, 1, "b"), (3, 0, 0, "pad:3"), (5, -1, 0, "alt"),
               (4, 0, -1, "b"), (3, 1, 0, "b")]},
    {"name": "Ice", "dir": "E", "block": "packed_ice", "alt": "snow_block", "pad": "blue_ice",
     "decor": ["packed_ice", "snow_block"], "light": "lantern",
     "jumps": [(4, 0, 0, "b"), (4, 0, 1, "b"), (3, 0, 0, "ice:6"), (6, -1, 0, "alt"), (3, 1, 0, "b"),
               (5, -1, 0, "b"), (4, 0, -1, "alt"), (3, 0, 0, "ice:6"), (6, -1, 0, "alt"), (3, 1, 0, "b"),
               (4, 0, 1, "alt"), (3, 1, 0, "b")]},
    {"name": "Nether", "dir": "S", "block": "nether_bricks", "alt": "soul_sand", "pad": "blackstone",
     "decor": ["crimson_stem", "shroomlight"], "light": "glowstone",
     "jumps": [(4, 0, 0, "b"), (2, 0, 0, "alt"), (2, 0, 0, "b"), (3, 0, 0, "pad:3"), (4, 0, 0, "b"),
               (3, 0, 0, "fence"), (4, 0, 1, "b"), (5, -1, 0, "b"), (2, 0, 0, "alt"), (2, 1, 0, "b"),
               (3, 0, 0, "fence"), (3, 0, -1, "b"), (3, 1, 0, "b")]},
    {"name": "Deep Dark", "dir": "E", "block": "deepslate_tiles", "alt": "sculk", "pad": "polished_deepslate",
     "decor": ["deepslate_bricks", "sculk"], "light": "soul_lantern",
     "jumps": [(3, 1, 0, "b"), (3, 0, 0, "pad:3"), (5, -1, 0, "b"), (4, 0, 2, "alt"), (5, -1, 0, "b"),
               (3, 0, 0, "fence"), (4, 0, 0, "b"), (3, 0, 0, "ladder:5"), (4, 0, 0, "b"), (5, -1, 1, "alt"),
               (3, 0, 0, "pad:3"), (4, 0, 0, "b"), (4, 0, 0, "b"), (3, 1, -1, "b")]},
    {"name": "The End", "dir": "N", "block": "end_stone", "alt": "purpur_block", "pad": "end_stone_bricks",
     "decor": ["purpur_pillar", "obsidian"], "light": "end_rod",
     "jumps": [(3, 1, 0, "b"), (3, 0, 0, "pad:3"), (5, -1, 0, "alt"), (4, 0, 0, "rod"), (4, 0, 0, "b"),
               (5, -1, 1, "b"), (3, 0, 0, "pad:3"), (4, 0, 0, "alt"), (4, 0, 0, "b"), (3, 1, 0, "rod"),
               (4, -1, 0, "b"), (4, 0, -1, "alt"), (3, 0, 0, "pad:3"), (5, -1, 0, "b"), (3, 1, 0, "b")]},
]
CP_SIZE = 5   # checkpoint pads are 5x5
LOBBY = 7     # start platform is 7x7
FENCE = {"Desert": "sandstone_wall", "Nether": "nether_brick_fence", "Deep Dark": "deepslate_tile_wall"}


class Course:
    def __init__(self):
        self.blocks = {}      # (x, y, z) -> block
        self.nodes = []       # bot path: {"blocks": [[x,y,z],...], "entry": [x,y,z], "kind": ...}
        self.markers = []     # (kind, id, x, y, z, yaw, floor)
        self.signs = []       # (x, y, z, facing, lines)

    def put(self, x, y, z, block, keep=False):
        if keep and (x, y, z) in self.blocks:
            return
        self.blocks[(x, y, z)] = block

    def node(self, blocks, kind, entry=None):
        self.nodes.append({"blocks": [list(b) for b in blocks], "entry": list(entry or blocks[0]), "kind": kind})


def build_course():
    c = Course()
    # Lobby: 7x7 at the origin, you stand on y=0 blocks. Course leaves towards +x.
    h = LOBBY // 2
    lobby = [(x, 0, z) for x in range(-h, h + 1) for z in range(-h, h + 1)]
    for p in lobby:
        c.put(*p, "polished_andesite")
    for x in range(-h, h + 1):
        c.put(x, 0, -h, "gold_block")
    c.markers.append(("lobby", 0, 0, 1, 0, YAW["E"], None))
    c.node([(h, 0, 0)], "lobby", entry=(0, 0, 0))
    # signs on the lobby's back (west) side, facing east
    c.signs.append((-h, 1, -1, "east", ["Parkour", "Through the", "Worlds", "8 zones"]))
    c.signs.append((-h, 1, 1, "east", ["Run east to", "start the timer", "Fall = back to", "checkpoint"]))
    c.put(-h, 0, -1, "polished_andesite")
    pos = (h, 0, 0)  # block you jump from
    zone_floor = []
    for zi, zone in enumerate(ZONES):
        fx, fz = DIRS[zone["dir"]]
        rx, rz = -fz, fx  # to the right of forward
        ys = [pos[1]]
        for j, (fwd, up, side, kind) in enumerate(zone["jumps"]):
            x = pos[0] + fx * fwd + rx * side
            y = pos[1] + up
            z = pos[2] + fz * fwd + rz * side
            if kind.startswith("pad:") or kind.startswith("ice:"):
                length = int(kind.split(":")[1])
                mat = zone["pad"] if kind.startswith("pad:") else "blue_ice"
                run = [(x + fx * k, y, z + fz * k) for k in range(length)]
                for p in run:
                    c.put(*p, mat)
                c.node(run, kind)
                pos = run[-1]
            elif kind.startswith("ladder:") or kind.startswith("vine:"):
                height = int(kind.split(":")[1])
                base = (x, y, z)
                c.put(*base, zone["block"])
                wall = (x + fx, z + fz)
                for dy in range(1, height + 1):
                    c.put(wall[0], y + dy, wall[1], zone["alt"] if kind.startswith("ladder") else "jungle_log")
                    if kind.startswith("ladder"):
                        c.put(x, y + dy, z, f"ladder[facing={FACING[(-fx, -fz)]}]")
                    else:
                        c.put(x, y + dy, z, f"vine[{FACING[(fx, fz)]}=true]")
                top = (wall[0], y + height, wall[1])
                c.node([base], kind)
                c.node([top], "top")
                pos = top
            else:
                block = {"b": zone["block"], "alt": zone["alt"]}.get(kind)
                if kind == "fence":
                    block = FENCE.get(zone["name"], "oak_fence")
                elif kind == "rod":
                    block = "end_rod"
                c.put(x, y, z, block)
                c.node([(x, y, z)], kind)
                pos = (x, y, z)
            ys.append(pos[1])
            # side decoration every third jump: a pillar hanging below, light on top
            if j % 3 == 1:
                s = 4 if j % 2 else -4
                dx, dz = pos[0] + rx * s, pos[2] + rz * s
                for dy in range(-6, 0):
                    c.put(dx, pos[1] + dy, dz, zone["decor"][0], keep=True)
                c.put(dx, pos[1], dz, zone["decor"][1], keep=True)
                c.put(dx, pos[1] + 1, dz, zone["light"], keep=True)
        zone_floor.append(min(ys) - 3)
        # Checkpoint pad (or the finish after the last zone), 3 ahead of the last block.
        last = zi == len(ZONES) - 1
        size = 7 if last else CP_SIZE
        hs = size // 2
        cx, cy, cz = pos[0] + fx * (2 + hs), pos[1], pos[2] + fz * (2 + hs)
        pad = [(cx + a, cy, cz + b) for a in range(-hs, hs + 1) for b in range(-hs, hs + 1)]
        mat = "gold_block" if last else zone["pad"]
        for p in pad:
            c.put(*p, mat)
        c.put(cx, cy, cz, "emerald_block" if not last else "diamond_block")
        nxt = ZONES[zi + 1]["dir"] if not last else zone["dir"]
        nfx, nfz = DIRS[nxt]
        if last:
            c.markers.append(("finish", 99, cx, cy + 1, cz, YAW[zone["dir"]], None))
            c.node(pad, "finish", entry=(cx, cy, cz))
            c.signs.append((cx - nfx * hs, cy + 1, cz - nfz * hs, FACING[(nfx, nfz)],
                            ["FINISH", "Well done!", "", ""]))
        else:
            c.markers.append(("cp", zi + 1, cx, cy + 1, cz, YAW[nxt], None))
            c.node(pad, "cp", entry=(cx, cy, cz))
            nz = ZONES[zi + 1]
            # sign at the pad's far corner, facing back at you
            c.signs.append((cx + nfx * hs - (-nfz) * hs, cy + 1, cz + nfz * hs - nfx * hs,
                            FACING[(-nfx, -nfz)],
                            [f"Checkpoint {zi + 1}", f"Next: zone {zi + 2}", nz["name"], ""]))
            pos = (cx + nfx * hs, cy, cz + nfz * hs)
    # floors: checkpoint k (0 = lobby) leads into zone k+1; the finish uses the last zone's.
    floors = zone_floor
    c.markers = [(k, i, x, y, z, yaw, floors[min(i, len(floors) - 1)] if k != "finish" else floors[-1])
                 for (k, i, x, y, z, yaw, _) in c.markers]
    return c


def sign_cmd(x, y, z, facing, lines):
    msgs = "[" + ",".join(json.dumps(s) for s in lines) + "]"
    return (f"setblock ~{x} ~{y} ~{z} oak_wall_sign[facing={facing}]{{is_waxed:1b,front_text:"
            f"{{has_glowing_text:1b,messages:{msgs}}}}}")


def fmt_time_fn():
    """Split @s ptw_time into minutes, seconds, tenths (scores) and a padded copy in storage."""
    return [
        f"scoreboard players operation @s {NS}_m = @s {NS}_time",
        f"scoreboard players operation @s {NS}_m /= #1200 {NS}_c",
        f"scoreboard players operation @s {NS}_s = @s {NS}_time",
        f"scoreboard players operation @s {NS}_s %= #1200 {NS}_c",
        f"scoreboard players operation @s {NS}_s /= #20 {NS}_c",
        f"scoreboard players operation @s {NS}_t = @s {NS}_time",
        f"scoreboard players operation @s {NS}_t %= #20 {NS}_c",
        f"scoreboard players operation @s {NS}_t /= #2 {NS}_c",
        f"execute store result storage {NS}:tmp m int 1 run scoreboard players get @s {NS}_m",
        f"execute store result storage {NS}:tmp s int 1 run scoreboard players get @s {NS}_s",
        f"execute store result storage {NS}:tmp t int 1 run scoreboard players get @s {NS}_t",
        f'data modify storage {NS}:tmp pad set value ""',
        f'execute if score @s {NS}_s matches ..9 run data modify storage {NS}:tmp pad set value "0"',
    ]


def functions(c):
    f = {}
    zones = len(ZONES)
    # --- build ---
    xs = [p[0] for p in c.blocks]
    zs = [p[2] for p in c.blocks]
    bounds = (min(xs) - 8, min(zs) - 8, max(xs) + 8, max(zs) + 8)
    f["build"] = [
        "# Build the course at height 200 above where you stand. Run once.",
        f"execute align xz positioned ~0.5 {BUILD_Y} ~0.5 run function {NS}:build_here",
    ]
    f["build_here"] = [
        f"kill @e[type=marker,tag={NS}]",
        f"forceload add ~{bounds[0]} ~{bounds[1]} ~{bounds[2]} ~{bounds[3]}",
        f"summon marker ~ ~ ~ {{Tags:[\"{NS}\",\"{NS}_origin\"]}}",
        f"schedule function {NS}:build_go 20t",
    ]
    f["build_go"] = [f"execute at @e[type=marker,tag={NS}_origin,limit=1] run function {NS}:build_blocks"]
    lines = [f"setblock ~{x} ~{y} ~{z} {b}" for (x, y, z), b in sorted(c.blocks.items(), key=lambda kv: (kv[0][1], kv[0]))
             if not (b.startswith("ladder") or b.startswith("vine") or b == "lantern" or b == "soul_lantern" or b == "end_rod")]
    # attached blocks last, so their supports exist
    lines += [f"setblock ~{x} ~{y} ~{z} {b}" for (x, y, z), b in c.blocks.items()
              if b.startswith("ladder") or b.startswith("vine") or b in ("lantern", "soul_lantern", "end_rod")]
    lines += [sign_cmd(*s) for s in c.signs]
    for kind, i, x, y, z, yaw, floor in c.markers:
        tags = f'"{NS}","{NS}_cp"' + (f',"{NS}_lobby"' if kind == "lobby" else "") + (f',"{NS}_finish"' if kind == "finish" else "")
        # The marker carries its own number and fall height; ptw:init_marker reads them in once
        # its chunk's entities are loaded (that can be later than the build, far from the start).
        lines.append(f"summon marker ~{x} ~{y} ~{z} {{Tags:[{tags}],Rotation:[{yaw}f,0f],data:{{id:{i},drop:{y - floor}}}}}")
    lines += [
        f"forceload remove ~{bounds[0]} ~{bounds[1]} ~{bounds[2]} ~{bounds[3]}",
        f'summon marker ~ ~1 ~ {{Tags:["{NS}_tmp"]}}',
        f"execute as @e[type=marker,tag={NS}_tmp,limit=1] run function {NS}:save_state",
        f"kill @e[type=marker,tag={NS}_tmp]",
        f"data modify storage {NS}:state built set value 1b",
        f"execute as @a run function {NS}:restart",
        'tellraw @a {"text":"Parkour Through the Worlds is ready! You\'re at the start.","color":"green"}',
    ]
    f["build_blocks"] = lines
    lobby_floor = next(fl for k, _, _, _, _, _, fl in c.markers if k == "lobby")
    ys = [p[1] for p in c.blocks]
    def add(score, n):
        return f"scoreboard players {'add' if n >= 0 else 'remove'} {score} {NS}_c {abs(n)}"
    f["save_state"] = [
        "# Run as a marker standing at the start. Saves where the course is, for restart and tracking.",
        *[f"execute store result storage {NS}:state l{a} double 0.5 run data get entity @s Pos[{i}] 2" for i, a in enumerate("xyz")],
        f"execute store result score #v {NS}_c run data get entity @s Pos[1]",
        add("#v", lobby_floor - 1),
        f"execute store result storage {NS}:state lfloor int 1 run scoreboard players get #v {NS}_c",
        "# the box everyone on the course is in",
        f"execute store result score #v {NS}_c run data get entity @s Pos[0]",
        add("#v", bounds[0]),
        f"execute store result storage {NS}:state x1 int 1 run scoreboard players get #v {NS}_c",
        f"execute store result score #v {NS}_c run data get entity @s Pos[1]",
        add("#v", min(ys) - 41),
        f"execute store result storage {NS}:state y1 int 1 run scoreboard players get #v {NS}_c",
        f"execute store result score #v {NS}_c run data get entity @s Pos[2]",
        add("#v", bounds[1]),
        f"execute store result storage {NS}:state z1 int 1 run scoreboard players get #v {NS}_c",
        f"data modify storage {NS}:state dx set value {bounds[2] - bounds[0]}",
        f"data modify storage {NS}:state dy set value {max(ys) - min(ys) + 60}",
        f"data modify storage {NS}:state dz set value {bounds[3] - bounds[1]}",
    ]

    # --- load / tick ---
    f["load"] = [
        f"scoreboard objectives add {NS}_c dummy",
        *[f"scoreboard players set #{n} {NS}_c {n}" for n in (2, 20, 1200)],
        *[f"scoreboard objectives add {NS}_{o} dummy" for o in ("id", "cp", "floor", "run", "time", "falls", "best", "y", "m", "s", "t")],
        f'scoreboard objectives add {NS}_board dummy {{"text":"Best times","color":"gold"}}',
        f"scoreboard objectives add {NS}_use minecraft.used:minecraft.carrot_on_a_stick",
        f"scoreboard objectives add {NS}_restart trigger",
        f"scoreboard objectives add {NS}_back trigger",
        f"scoreboard objectives setdisplay sidebar {NS}_board",
    ]
    f["tick"] = [
        f"execute as @e[type=marker,tag={NS}_cp,tag=!{NS}_init] run function {NS}:init_marker",
        f"execute if data storage {NS}:state {{built:1b}} run function {NS}:tick_players with storage {NS}:state",
    ]
    f["tick_players"] = [
        "# Everyone inside the course's box (saved at build time) is on the course.",
        f"$execute as @a[x=$(x1),y=$(y1),z=$(z1),dx=$(dx),dy=$(dy),dz=$(dz),gamemode=!spectator] at @s run function {NS}:player",
    ]
    f["player"] = [
        f"tag @s add {NS}_self",
        f"function {NS}:player_tick",
        f"tag @s remove {NS}_self",
    ]
    f["player_tick"] = [
        "# Anything that teleports you ends this tick for you, so the checks below don't use",
        "# your old position.",
        f"scoreboard players enable @s {NS}_restart",
        f"scoreboard players enable @s {NS}_back",
        f"execute unless score @s {NS}_cp matches 0.. run return run function {NS}:restart",
        f"execute if score @s {NS}_restart matches 1.. run return run function {NS}:restart",
        f"execute if score @s {NS}_back matches 1.. run return run function {NS}:back",
        f"execute if score @s {NS}_use matches 1.. run return run function {NS}:use_item",
        "# reached a new checkpoint?",
        f"execute as @e[type=marker,tag={NS}_cp,tag=!{NS}_lobby,tag=!{NS}_finish,distance=..3] "
        f"if score @s {NS}_id > @p[tag={NS}_self] {NS}_cp run function {NS}:reach_cp",
        "# left the start platform: start the timer",
        f"execute if score @s {NS}_run matches 0 if score @s {NS}_cp matches 0 run function {NS}:start_check with storage {NS}:state",
        "# fell below this section: back to the checkpoint",
        f"execute store result score @s {NS}_y run data get entity @s Pos[1]",
        f"execute if score @s {NS}_y < @s {NS}_floor run return run function {NS}:fall",
        f"execute if score @s {NS}_run matches 1 run scoreboard players add @s {NS}_time 1",
        f"execute if score @s {NS}_run matches 1 run function {NS}:hud",
        f"execute if score @s {NS}_run matches 1 if entity @e[type=marker,tag={NS}_finish,distance=..3.5] run function {NS}:finish",
    ]
    f["init_marker"] = [
        f"execute store result score @s {NS}_id run data get entity @s data.id",
        f"execute store result score @s {NS}_floor run data get entity @s Pos[1]",
        f"execute store result score #drop {NS}_c run data get entity @s data.drop",
        f"scoreboard players operation @s {NS}_floor -= #drop {NS}_c",
        f"tag @s add {NS}_init",
    ]
    f["restart"] = [
        "# Back to the start, timer reset.",
        f"scoreboard players set @s {NS}_restart 0",
        f"scoreboard players set @s {NS}_cp 0",
        f"scoreboard players set @s {NS}_run 0",
        f"scoreboard players set @s {NS}_time 0",
        f"scoreboard players set @s {NS}_falls 0",
        f"function {NS}:to_lobby with storage {NS}:state",
        f"function {NS}:give_items",
        'title @s actionbar {"text":"At the start: run east to begin","color":"yellow"}',
    ]
    f["to_lobby"] = [
        "$scoreboard players set @s ptw_floor $(lfloor)",
        "$tp @s $(lx) $(ly) $(lz) -90 0",
    ]
    f["give_items"] = [
        f'clear @s carrot_on_a_stick[custom_data={{{NS}:"back"}}]',
        f'clear @s carrot_on_a_stick[custom_data={{{NS}:"restart"}}]',
        f'item replace entity @s hotbar.7 with carrot_on_a_stick[custom_data={{{NS}:"back"}},item_model="minecraft:recovery_compass",'
        f'custom_name={{text:"Back to checkpoint",color:"green",italic:false}},unbreakable={{}}]',
        f'item replace entity @s hotbar.8 with carrot_on_a_stick[custom_data={{{NS}:"restart"}},item_model="minecraft:clock",'
        f'custom_name={{text:"Restart course",color:"red",italic:false}},unbreakable={{}}]',
    ]
    f["use_item"] = [
        f"scoreboard players set @s {NS}_use 0",
        f'execute if items entity @s weapon.mainhand carrot_on_a_stick[custom_data={{{NS}:"back"}}] run function {NS}:back',
        f'execute if items entity @s weapon.mainhand carrot_on_a_stick[custom_data={{{NS}:"restart"}}] run function {NS}:restart',
    ]
    f["back"] = [
        f"scoreboard players set @s {NS}_back 0",
        f"function {NS}:to_cp",
    ]
    f["start_check"] = [
        "# Uses the start's saved position, which works even before that area has loaded.",
        f"$execute unless entity @s[x=$(lx),y=$(ly),z=$(lz),distance=..5.2] run function {NS}:start",
    ]
    f["start"] = [
        f"scoreboard players set @s {NS}_run 1",
        f"scoreboard players set @s {NS}_time 0",
        f"scoreboard players set @s {NS}_falls 0",
        "playsound minecraft:block.note_block.pling master @s ~ ~ ~ 1 1.5",
    ]
    f["reach_cp"] = [
        "# as the checkpoint marker",
        f"scoreboard players operation @p[tag={NS}_self] {NS}_cp = @s {NS}_id",
        f"scoreboard players operation @p[tag={NS}_self] {NS}_floor = @s {NS}_floor",
        f"execute as @p[tag={NS}_self] at @s run playsound minecraft:entity.player.levelup master @s ~ ~ ~ 1 1.2",
    ]
    for i, z in enumerate(ZONES[1:], start=1):
        f["reach_cp"].append(
            f'execute if score @s {NS}_id matches {i} run title @p[tag={NS}_self] subtitle '
            f'{{"text":"Checkpoint {i}/{zones - 1}: next is {z["name"]}","color":"green"}}')
    f["reach_cp"].append(f'title @p[tag={NS}_self] title ""')
    f["fall"] = [
        f"execute if score @s {NS}_run matches 1 run scoreboard players add @s {NS}_falls 1",
        f"function {NS}:to_cp",
        "playsound minecraft:entity.enderman.teleport master @s ~ ~ ~ 0.6 1",
    ]
    f["to_cp"] = [
        "# Teleport to your current checkpoint (facing the way to go).",
        f"tag @s add {NS}_tp",
        f"execute as @e[type=marker,tag={NS}_cp] if score @s {NS}_id = @p[tag={NS}_tp] {NS}_cp run tp @p[tag={NS}_tp] @s",
        f"execute if score @s {NS}_cp matches 0 run function {NS}:to_lobby with storage {NS}:state",
        f"tag @s remove {NS}_tp",
    ]
    f["hud"] = fmt_time_fn() + [f"function {NS}:hud_show with storage {NS}:tmp"]
    f["hud_show"] = [
        f'$title @s actionbar [{{"text":"Time $(m):$(pad)$(s).$(t)","color":"gold"}},{{"text":"   Falls ","color":"gray"}},'
        f'{{"score":{{"name":"@s","objective":"{NS}_falls"}},"color":"white"}},{{"text":"   Checkpoint ","color":"gray"}},'
        f'{{"score":{{"name":"@s","objective":"{NS}_cp"}},"color":"white"}},{{"text":"/{zones - 1}","color":"white"}}]',
    ]
    f["finish"] = [
        f"scoreboard players set @s {NS}_run 0",
        *fmt_time_fn(),
        f"execute if entity @s[gamemode=creative] run return run function {NS}:finish_creative",
        f"function {NS}:finish_msg with storage {NS}:tmp",
        f"execute if score @s {NS}_best matches 1.. if score @s {NS}_time >= @s {NS}_best run tellraw @s "
        '{"text":"Not a new best this time. Keep trying!","color":"gray"}',
        f"execute unless score @s {NS}_best matches 1.. run function {NS}:new_best with storage {NS}:tmp",
        f"execute if score @s {NS}_time < @s {NS}_best run function {NS}:new_best with storage {NS}:tmp",
        f"execute unless entity @s[tag={NS}_trophy] run function {NS}:trophy",
        f"function {NS}:fireworks",
    ]
    f["finish_creative"] = [
        'tellraw @s {"text":"Finished in creative mode, so it doesn\'t count for the leaderboard. Switch to adventure or survival.","color":"yellow"}',
    ]
    f["finish_msg"] = [
        'title @s title {"text":"Finished!","color":"gold"}',
        f'$title @s subtitle {{"text":"$(m):$(pad)$(s).$(t)","color":"yellow"}}',
        f'$tellraw @a [{{"selector":"@s","color":"aqua"}},{{"text":" finished Parkour Through the Worlds in $(m):$(pad)$(s).$(t) with ","color":"white"}},'
        f'{{"score":{{"name":"@s","objective":"{NS}_falls"}}}},{{"text":" falls!","color":"white"}}]',
    ]
    f["new_best"] = [
        f"scoreboard players operation @s {NS}_best = @s {NS}_time",
        f"scoreboard players operation @s {NS}_board = @s {NS}_time",
        f"scoreboard players operation @s {NS}_board *= #-1 {NS}_c",
        f'$scoreboard players display numberformat @s {NS}_board fixed {{"text":"$(m):$(pad)$(s).$(t)","color":"yellow"}}',
        'tellraw @s {"text":"New personal best!","color":"gold","bold":true}',
    ]
    f["load"].insert(1, f"scoreboard players set #-1 {NS}_c -1")
    f["trophy"] = [
        f"tag @s add {NS}_trophy",
        'give @s nether_star[custom_name={text:"Parkour Champion",color:"gold",italic:false},'
        'lore=[{text:"Finished Parkour Through the Worlds",color:"gray",italic:false}],enchantment_glint_override=true]',
        'tellraw @s {"text":"You earned the Parkour Champion trophy!","color":"gold"}',
    ]
    fw = ('{LifeTime:%d,FireworksItem:{id:"minecraft:firework_rocket",count:1,components:{"minecraft:fireworks":'
          '{flight_duration:1,explosions:[{shape:"%s",colors:[I;%d,%d],has_twinkle:1b,has_trail:1b}]}}}}')
    f["fireworks"] = [
        "summon firework_rocket ~2 ~1 ~2 " + fw % (20, "large_ball", 16766720, 16711680),
        "summon firework_rocket ~-2 ~1 ~2 " + fw % (25, "star", 65280, 255),
        "summon firework_rocket ~2 ~1 ~-2 " + fw % (30, "burst", 16777215, 16753920),
        "summon firework_rocket ~-2 ~1 ~-2 " + fw % (22, "large_ball", 11141290, 65535),
    ]
    return f


def build():
    c = build_course()
    out = ROOT / "release" / f"parkour-through-the-worlds-datapack-{VERSION}.zip"
    out.parent.mkdir(exist_ok=True)
    funcs = functions(c)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("pack.mcmeta", json.dumps({"pack": {
            "description": f"Parkour Through the Worlds v{VERSION}",
            "min_format": DATA_FORMAT,
            "max_format": 1000,
        }}, indent=2))
        z.writestr("data/minecraft/tags/function/load.json", json.dumps({"values": [f"{NS}:load"]}))
        z.writestr("data/minecraft/tags/function/tick.json", json.dumps({"values": [f"{NS}:tick"]}))
        for name, lines in funcs.items():
            z.writestr(f"data/{NS}/function/{name}.mcfunction", "\n".join(lines) + "\n")
    # Path for the bot test (relative to the origin marker's block).
    (ROOT / "src" / "path.json").write_text(json.dumps({
        "nodes": c.nodes,
        "markers": [{"kind": k, "id": i, "pos": [x, y, z], "floor": fl} for k, i, x, y, z, _, fl in c.markers],
    }))
    jumps = sum(len(z["jumps"]) for z in ZONES)
    print(f"wrote {out.relative_to(ROOT)}: {len(c.blocks)} blocks, {jumps} jumps, {len(ZONES)} zones")


if __name__ == "__main__":
    build()
