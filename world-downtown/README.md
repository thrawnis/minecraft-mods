# LA & NYC World

A real-size (1 block = 1 metre) Minecraft world with seven areas built from OpenStreetMap data, plus a datapack that adds teleport stations, a map menu, tour signs and night lights.

| Area | Covers roughly | Size |
|---|---|---|
| **Hollywood** | Hollywood Blvd from La Brea to Vine, Sunset Blvd, the Hollywood Bowl | ~10 km² |
| **Downtown LA** | Bunker Hill, Financial District, Grand Park, Civic Center, Crypto.com Arena | ~10 km² |
| **Griffith Park & Hollywood Sign** | Griffith Observatory, Mount Lee and the Hollywood Sign | ~10 km² |
| **LAX** | The central terminals, Theme Building and both runway pairs | ~10 km² |
| **Times Square & Midtown** | 34th St (Empire State Building) up to Central Park South | ~10 km² |
| **Central Park** | From the park's south end to about 110th St, with the Met and the Guggenheim | ~10 km² |
| **Statue of Liberty & Ellis Island** | Both islands and the harbour around them | ~2.5 km² |

You build the world on your own computer with [Arnis](https://github.com/louis-e/arnis), a free open-source tool, then add this repo's datapack.

## Features

- **Ten teleport stations:** Hollywood, Hollywood Sign, Griffith Observatory, Downtown LA, LAX Terminals, LAX Theme Building, Times Square, Empire State roof, Central Park and Statue of Liberty. Each has one button.
- **Map menu:** the station button opens a pop-up menu listing every station. Click one and you're there, with no confirmation screen. You can also open the menu anywhere with `/function lanyc:menu`.
- **Tour signs:** 34 signs at landmarks, each with the name and a short fact (e.g. *TCL Chinese Theatre / Opened 1927 / Star handprints*). The text glows, so you can read them at night.
- **Night lights:** as you explore, lamp posts are added along the sidewalks of main roads, about one per 16 blocks. They switch on at night and off in the day. Side streets don't get them, and neither do spots where Arnis already put a lamp.
- **Building interiors and extra signage:** Arnis's `--interior` (rooms inside buildings) and `--signage full` (more street and shop signs) are included in the generation commands below.

## Compatibility

| | |
|---|---|
| **Type** | World (generated on your computer) + datapack |
| **Minecraft version** | Java Edition 26.1 (the datapack was tested in 26.1) |
| **Generator** | Arnis 3.4.0 or newer |
| **Datapack version** | 2.0.0 |
| **Mode** | Creative (sightseeing) |

## Dependencies

- [Arnis](https://github.com/louis-e/arnis/releases), required, to generate the world. Download it **only** from its GitHub Releases page or arnismc.com; Arnis warns that copies elsewhere may be malicious.
- An internet connection while generating (Arnis downloads the map data).

## What to expect

- **Streets, building shapes and heights, parks, water and terrain** are in the right places at real size.
- **Buildings are simple blocks.** With `--interior` they have basic rooms inside, but there are no detailed fronts, Times Square screens or logos.
- **The LA areas are at their real distances apart**, about 3–20 km. The New York areas are about **4 million blocks east**. Use the stations to get there.
- **New York is about 9% stretched** sideways. A flat map can't be exactly right on both coasts at once, so LA is true size and NYC is slightly larger.
- **Size:** expect many GB of disk space and several hours of generation for all seven areas, depending on your computer. Opening the world can also take a while. A lower render distance helps.

## Installation

### Step 1: Download Arnis

Get the latest release for your system from https://github.com/louis-e/arnis/releases and unzip it.

- **Windows:** if SmartScreen warns, click **More info → Run anyway**. If it doesn't start, install the Microsoft WebView2 runtime ("Evergreen Bootstrapper").
- **macOS:** the app isn't notarized. Open it once, then go to **System Settings → Privacy & Security → Open Anyway**.
- **Linux:** install `webkit2gtk-4.1` with your package manager, or use the AppImage.

### Step 2: Generate the seven areas, in this order

**Close Minecraft first.** Arnis can't write to a world that's open.

Open a terminal (Windows: **Command Prompt**) in the folder where you unzipped Arnis, and run the commands below **in this order**. Hollywood must be first, because the first area fixes the world's map and the stations depend on it. **Don't change the numbers**, or stations and signs will end up in the wrong place.

Replace `arnis` with the name of the program you downloaded (on Windows it's something like `arnis-windows.exe`), and replace `SAVES_FOLDER` with the saves folder for your system:

- **Windows:** `%APPDATA%\.minecraft\saves`
- **macOS:** `~/Library/Application Support/minecraft/saves`
- **Linux:** `~/.minecraft/saves`

```text
arnis --one-world --world-name="LA and NYC" --interior --signage full --output-dir="SAVES_FOLDER" --bbox="34.0856,-118.3524,34.1144,-118.3176" --spawn-lat 34.10166 --spawn-lng -118.33869

arnis --one-world --world-name="LA and NYC" --interior --signage full --output-dir="SAVES_FOLDER" --bbox="34.0356,-118.2723,34.0644,-118.2377"

arnis --one-world --world-name="LA and NYC" --interior --signage full --output-dir="SAVES_FOLDER" --bbox="34.116,-118.3284,34.1448,-118.2936"

arnis --one-world --world-name="LA and NYC" --interior --signage full --output-dir="SAVES_FOLDER" --bbox="33.9281,-118.4223,33.9569,-118.3877"

arnis --one-world --world-name="LA and NYC" --interior --signage full --output-dir="SAVES_FOLDER" --bbox="40.7436,-74.0045,40.7724,-73.9665"

arnis --one-world --world-name="LA and NYC" --interior --signage full --output-dir="SAVES_FOLDER" --bbox="40.7726,-73.9844,40.8014,-73.9464"

arnis --one-world --world-name="LA and NYC" --interior --signage full --output-dir="SAVES_FOLDER" --bbox="40.686,-74.05,40.703,-74.034"
```

The lines are: Hollywood, Downtown LA, Griffith Park & Hollywood Sign, LAX, Times Square & Midtown, Central Park, Statue of Liberty & Ellis Island.

For example, on Windows the first one would start like:
`arnis-windows.exe --one-world --world-name="LA and NYC" --interior --signage full --output-dir="%APPDATA%\.minecraft\saves" --bbox=...`

**Already generated the first three areas with version 1.0.0?** You don't have to start again. Just run the Griffith, LAX, Central Park and Statue of Liberty commands, which add to the same world. Those first three areas won't have interiors or the extra signage unless you regenerate them.

### Step 3: Add the datapack

Copy `release/la-nyc-teleport-2.0.0.zip` (don't unzip it) into the world's `datapacks` folder:
`<saves folder>/LA and NYC/datapacks/`

If you used version 1.0.0 before, **delete `la-nyc-teleport-1.0.0.zip`** from that folder first. Version 2.0.0 builds new stations, but the old three-button stations stay where they are; you can break them in creative.

### Step 4: Play

Open Minecraft **26.1**, go to **Singleplayer**, and open **LA and NYC**. If it warns that the world was made with an older version, click to continue (consider making a backup first, as it suggests).

A few seconds after it loads, chat says **"LA & NYC: stations and tour signs are ready."** You start in Hollywood, by the station on Hollywood Blvd. Press its button to open the map menu.

## Usage

You start in **Hollywood**, next to the station on Hollywood Blvd, in creative mode. Double-tap **Space** to fly.

**Travel between places:**
1. Walk up to a station: a small stone wall with two glowing lanterns and a sign saying **Station**.
2. Press the **button** on the wall (right-click it). A **map menu** pops up with all ten destinations.
3. Click where you want to go. You arrive in front of that place's station.
4. Click **Close**, or press **Esc**, to close the menu without going anywhere.

Without walking to a station, type `/function lanyc:menu` to open the same menu anywhere, or `/function lanyc:go/<station>` to go straight there (for example `/function lanyc:go/empire_state`).

| Station | What's there |
|---|---|
| Hollywood | Hollywood Blvd & Highland: TCL Chinese Theatre, Dolby Theatre, Walk of Fame |
| Hollywood Sign | The hillside below the sign |
| Griffith Observatory | The lawn in front of the observatory |
| Downtown LA | Grand Park, near City Hall and the Walt Disney Concert Hall |
| LAX Terminals | Tom Bradley International Terminal |
| LAX Theme Building | Next to the Theme Building |
| Times Square | The Times Square plaza |
| Empire State roof | On top of the Empire State Building |
| Central Park | Bethesda Terrace and Fountain |
| Statue of Liberty | Liberty Island |

**Sightseeing:**
- **Tour signs** stand at landmarks: look for a sign on a stone post with a name and a short fact. Their text glows at night.
- **Night lights:** type `/time set night` to see the lamp posts along the main roads light up (`/time set day` to go back). Lamps are added to new streets as you fly around them.
- **Make a station yours:** if a station is in an awkward spot, stand where you want it and type `/function lanyc:move/<station>`.

## Special instructions

- **If a station lands somewhere odd**, like on a hillside or in a corner: stand where you'd like it and type `/function lanyc:move/<station>`. The station is rebuilt at your feet, and that becomes the teleport destination. Arnis worlds have cheats on by default, so this works without extra setup. Station names:
  `hollywood`, `hollywood_sign`, `griffith`, `downtown`, `lax`, `theme_building`, `times_square`, `empire_state`, `central_park`, `liberty`.
- **Teleport without the menu:** `/function lanyc:go/<station>`, for example `/function lanyc:go/liberty`.
- **Where things are placed:** stations and signs look for solid ground within 24 blocks of the landmark, avoiding roofs and wall tops. The **Empire State roof** station is placed on top of the building on purpose.
- **Night lights take a moment.** Lamps are added to the area around you as you explore: about 5 × 5 chunks, a couple of chunks every half second. Fly a little slower to watch them appear.
- **Opening the world in a newer version** (26.2, 26.3) should also work. The datapack allows newer versions, but it was only tested in 26.1.
- **Adding more places later:** run Arnis again with the same `--one-world --world-name="LA and NYC"` and a new `--bbox`. New areas join the same world at their real positions.

## How it works

Arnis's One World mode puts every area into one map frame, centred on the first area generated. `src/generate.py` uses the same formulas as Arnis (`src/projection/web_mercator.rs`) to work out which blocks each station and sign lands on, and bakes those into the datapack.

When the world first loads, the datapack:
1. temporarily loads those chunks;
2. spirals outward from each spot to the nearest solid ground;
3. builds the station or sign there, one per tick;
4. releases the chunks.

**Map menu:** the menu is a Minecraft dialog with one button per station. Each button runs `/trigger lanyc_go`, a command every player may use, so the game doesn't ask "Confirm Command Execution" each time; the datapack then does the teleport.

**Night lights:** as you move, the datapack checks each new chunk near you once. It looks for a sidewalk block (smooth stone or grey concrete) with an asphalt road (Arnis's road blocks) running at least about 9 blocks wide beside it. If it finds one, it adds a lamp post: a redstone lamp topped with an inverted daylight sensor, so it lights up at night.

## Testing

The datapack was tested in a real 26.1 game, installed into a world as a `.zip`:
- all ten stations and the tour signs were built on first load, at the computed blocks, and the temporary chunk loading was released afterwards
- a sign aimed at a fake building landed on the ground outside it, not on its roof or wall
- pressing a station button opened the map menu, and a real mouse click on **Times Square** teleported there straight away; an earlier version showed a confirmation screen first, so the menu was changed to avoid it
- on a test street, lamps appeared along a 13-block-wide road and none along a 5-block-wide side street; they were on at midnight and off at noon

The world generation itself wasn't run here, because OpenStreetMap's servers refuse connections from the build environment. So the landmark coordinates are my own, the street-detection rules come from Arnis's source code, and neither has been checked against a real generated world.

## Building from source

```bash
cd world-downtown
python3 src/generate.py
```

This rebuilds the datapack zip in `release/` and prints the Arnis commands and station coordinates. To change areas, stations or signs, edit `AREAS`, `STATIONS` and `SIGNS` at the top. If you change the first area, every coordinate changes, so regenerate the world from scratch.

## Changelog

- **2.0.0**:
  - Added Griffith Park & Hollywood Sign, LAX, Central Park, and Statue of Liberty & Ellis Island.
  - Ten stations, each with one button that opens a map menu.
  - 34 tour signs.
  - Night lights along main roads.
  - Arnis commands now include `--interior` and `--signage full`.
  - Stations and signs search for solid ground nearby.
- **1.0.0**: First release. Three areas (Hollywood, Downtown LA, Times Square), teleport stations with buttons.
