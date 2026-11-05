# LA & NYC World

A real-size (1 block = 1 metre) Minecraft world with three areas built from OpenStreetMap data, each about 3.2 km × 3.2 km (~10 km²):

| Area | Covers roughly | Station spot |
|---|---|---|
| **Hollywood** | Hollywood Blvd from La Brea to Vine, Sunset Blvd, and the hills to the north | Hollywood Blvd & Highland Ave |
| **Downtown LA** | Bunker Hill, Financial District, Pershing Square, Grand Park, Civic Center | Grand Park |
| **Times Square** | Midtown Manhattan from about 34th St (Empire State Building) to Central Park South | Times Square plaza |

Each area has a small **teleport station** with three buttons (Hollywood, Downtown LA, Times Square). Press one to jump to that area's station.

You build the world on your own computer with [Arnis](https://github.com/louis-e/arnis), a free open-source tool, then add this repo's teleport datapack.

## Compatibility

| | |
|---|---|
| **Type** | World (generated on your computer) + datapack |
| **Minecraft version** | Java Edition 26.1 (the datapack was tested in 26.1) |
| **Generator** | Arnis 3.4.0 or newer |
| **Datapack version** | 1.0.0 |
| **Mode** | Creative (sightseeing) |

## Dependencies

- [Arnis](https://github.com/louis-e/arnis/releases), required, to generate the world. Download it **only** from its GitHub Releases page or arnismc.com; Arnis warns that copies elsewhere may be malicious.
- An internet connection while generating (Arnis downloads the map data).

## What to expect

- **Streets, building shapes and heights, parks, water and terrain** are in the right places at real size.
- **Buildings are simple blocks.** You won't see detailed fronts, Times Square's screens or famous logos.
- **Hollywood and Downtown LA are at their real distance apart** (about 9 km), because Arnis puts every area of one world on a single map. Times Square is about **4 million blocks east**. Don't try walking there; use the station.
- **Times Square is about 9% stretched** sideways. A flat map can't be exactly right on both coasts at once, so the LA areas are true size and NYC is slightly larger.
- **Size:** expect a few GB of disk space and a long generation time, possibly an hour or more depending on your computer. Opening the world can also take a while. A lower render distance helps.

## Installation

### Step 1: Download Arnis

Get the latest release for your system from https://github.com/louis-e/arnis/releases and unzip it.

- **Windows:** if SmartScreen warns, click **More info → Run anyway**. If it doesn't start, install the Microsoft WebView2 runtime ("Evergreen Bootstrapper").
- **macOS:** the app isn't notarized. Open it once, then go to **System Settings → Privacy & Security → Open Anyway**.
- **Linux:** install `webkit2gtk-4.1` with your package manager, or use the AppImage.

### Step 2: Generate the three areas, in this order

**Close Minecraft first.** Arnis can't write to a world that's open.

Open a terminal (Windows: **Command Prompt**) in the folder where you unzipped Arnis, and run the three commands below **in this order**. Hollywood must be first, because the first area fixes the world's map, and the teleport stations depend on it. **Don't change the numbers**, or the stations will end up in the wrong place.

Replace `arnis` with the name of the program you downloaded (on Windows it's something like `arnis-windows.exe`), and use the saves folder for your system:

- **Windows:** `%APPDATA%\.minecraft\saves`
- **macOS:** `~/Library/Application Support/minecraft/saves`
- **Linux:** `~/.minecraft/saves`

```text
arnis --one-world --world-name="LA and NYC" --output-dir="SAVES_FOLDER" --bbox="34.0856,-118.3524,34.1144,-118.3176" --spawn-lat 34.10166 --spawn-lng -118.33869

arnis --one-world --world-name="LA and NYC" --output-dir="SAVES_FOLDER" --bbox="34.0356,-118.2723,34.0644,-118.2377"

arnis --one-world --world-name="LA and NYC" --output-dir="SAVES_FOLDER" --bbox="40.7436,-74.0045,40.7724,-73.9665"
```

For example, on Windows the first one would start like:
`arnis-windows.exe --one-world --world-name="LA and NYC" --output-dir="%APPDATA%\.minecraft\saves" --bbox=...`

When all three are done, you'll have a world folder called **LA and NYC** in your saves folder.

### Step 3: Add the teleport stations

Copy `release/la-nyc-teleport-1.0.0.zip` (don't unzip it) into the world's `datapacks` folder:
`<saves folder>/LA and NYC/datapacks/`

### Step 4: Play

Open Minecraft **26.1**, go to **Singleplayer**, and open **LA and NYC**. If it warns that the world was made with an older version, click to continue (consider making a backup first, as it suggests).

A few seconds after it loads, chat says **"LA & NYC teleport stations are ready."** You start in Hollywood, at the station on Hollywood Blvd. Press a button to teleport.

## Special instructions

- **If a station lands somewhere odd**, like on a roof or a tree: stand where you'd like it and type `/function lanyc:move/hollywood` (or `move/downtown`, `move/times_square`). The station is rebuilt at your feet, and that becomes the teleport destination. This needs cheats on, which Arnis worlds have by default.
- **Teleport without a station:** `/function lanyc:go/hollywood`, `/function lanyc:go/downtown`, `/function lanyc:go/times_square`.
- **Station coordinates**, if you'd rather use `/tp`:

  | Station | X | Z |
  |---|---|---|
  | Hollywood | -340 | -185 |
  | Downtown LA | 8194 | 4891 |
  | Times Square | 4083529 | -772936 |

- **Opening the world in a newer version** (26.2, 26.3) should also work. The datapack may need its version range updated, but it allows newer versions.
- **Adding more places later:** run Arnis again with the same `--one-world --world-name="LA and NYC"` and a new `--bbox`. New areas join the same world at their real positions.

## How it works

Arnis's One World mode puts every area into one map frame centred on the first area generated. `src/generate.py` uses the same formulas as Arnis (`src/projection/web_mercator.rs`) to work out exactly which blocks the three station spots land on, and bakes those into the datapack. When the world first loads, the datapack keeps those three chunks loaded, finds the ground at each spot (ignoring leaves), and builds a station there. Each button is wired to a command block that teleports you to another station.

The datapack was tested in a real 26.1 game:
- added to a world as a `.zip`
- stations built at the exact computed blocks on first load
- a real button press teleporting from Hollywood to Times Square
- the move command working

The world generation itself wasn't run here, because the map-data servers aren't reachable from the build environment.

## Building from source

```bash
cd world-downtown
python3 src/generate.py
```

This rebuilds the datapack zip in `release/` and prints the Arnis commands and station coordinates. To change areas or station spots, edit `AREAS` and `STATIONS` at the top. If you change the first area, every station coordinate changes, so regenerate the world from scratch.

## Changelog

- **1.0.0**: First release. Three areas (Hollywood, Downtown LA, Times Square), teleport stations with buttons.
