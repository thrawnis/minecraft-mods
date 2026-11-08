# LN

A real-size Minecraft world of **Laguna Niguel, California** ("LN"). It's built from OpenStreetMap data with [Arnis](https://github.com/louis-e/arnis), plus a datapack for teleport stations, a map menu and tour signs.

**Features:**
- **4 teleport stations**, each with one button that opens a **map menu** of every station. Click one and you're there.
- **Tour signs:** 4 signs: City Hall, Regional Park, the Ziggurat and the Metrolink station.
- **Building interiors** and extra street and shop signs, from Arnis's `--interior` and `--signage full` options.
- **Normal Minecraft height** (`--vanilla-height`), so it runs much lighter than the LA & NYC world.

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

- **Area:** all of Laguna Niguel, about 7 km × 9.5 km.
- **Real size:** 1 block = 1 metre. Streets, building shapes and heights, parks, water and terrain are in the right places.
- **Buildings are simple blocks**, with basic rooms inside. There are no detailed fronts or logos.
- **Size:** this covers the whole city, so it's big: expect several GB of disk space and a long generation time.

## Installation

### Step 1: Download Arnis

Get the latest release for your system from https://github.com/louis-e/arnis/releases and unzip it.

- **Windows:** if SmartScreen warns, click **More info → Run anyway**. If it doesn't start, install the Microsoft WebView2 runtime ("Evergreen Bootstrapper").
- **macOS:** the app isn't notarized. Open it once, then go to **System Settings → Privacy & Security → Open Anyway**.
- **Linux:** install `webkit2gtk-4.1` with your package manager, or use the AppImage.

### Step 2: Generate the world

**Close Minecraft first.** Open a terminal (Windows: **Command Prompt**) in the folder where you unzipped Arnis and run this command. **Don't change the numbers**, or the stations and signs end up in the wrong place.

Replace `arnis` with the name of the program you downloaded (on Windows it's something like `arnis-windows.exe`). Replace `SAVES_FOLDER` with your saves folder:
- **Windows:** `%APPDATA%\.minecraft\saves`
- **macOS:** `~/Library/Application Support/minecraft/saves`
- **Linux:** `~/.minecraft/saves`

```text
arnis --bbox="33.48,-117.74,33.565,-117.665" --projection web_mercator --vanilla-height --interior --signage full --spawn-lat 33.523 --spawn-lng -117.7042 --output-dir="SAVES_FOLDER"
```

For example, on Windows:
`arnis-windows.exe --bbox="33.48,-117.74,33.565,-117.665" ... --output-dir="%APPDATA%\.minecraft\saves"`

It takes a long time, possibly an hour or more. When it's done, there's a new world folder called **Arnis World 1** (or 2, 3…) in your saves folder.

### Step 3: Name it and convert it (one time)

Arnis saves worlds in an older Minecraft format. Converting it once, before playing, avoids heavy lag and freezes.

1. Open Minecraft **26.1** and click **Singleplayer**.
2. Click the new **Arnis World** once to select it (don't open it), then click **Edit**.
3. Change **World Name** to **LN**.
4. Click **Optimize World**, leave **Erase Cached Data** unticked, and click **Create Backup and Optimize**. Wait for it to finish.

### Step 4: Add the datapack

1. Close Minecraft.
2. Copy `release/ln-datapack-1.0.0.zip` (don't unzip it) into the world's `datapacks` folder: `<saves folder>/Arnis World N/datapacks/`

### Step 5: Play

Open **LN** from **Singleplayer**. A few seconds after it loads, chat says **"LN: stations and tour signs are ready."** You start next to the first station.

## Usage

**Travel around:**
1. Walk up to a station: a small stone wall with two glowing lanterns and a sign saying **Station**.
2. Press the **button** on the wall (right-click it). A **map menu** pops up with every station.
3. Click where you want to go. You arrive in front of that station. Click **Close** or press **Esc** to cancel.

You can also open the menu anywhere with `/function ln:menu`, or go straight to a station with `/function ln:go/<station>`.

| Station | Name for commands |
|---|---|
| City Hall & Library | `city_hall` |
| Regional Park | `regional_park` |
| The Ziggurat | `ziggurat` |
| Metrolink station | `metrolink` |

**Sightseeing:**
- **Tour signs** stand at landmarks: a sign on a stone post with a name and a short fact. Their text glows at night.
- **Fly** by double-tapping **Space**. You're in creative mode.

**Move a station:** if one is in an awkward spot, stand where you want it and type `/function ln:move/<station>`. It's rebuilt at your feet and becomes that station's teleport point.

**Turn it off:** delete the datapack zip from the world's `datapacks` folder. The stations and signs already built stay; you can break them in creative.

## If it runs slowly

- **Did you do Step 3 (Optimize World)?** It's the most important step.
- **Give Minecraft more memory.** In the launcher, go to **Installations**, then **… → Edit → More options**. In **JVM arguments**, change `-Xmx2G` to `-Xmx6G` (with 16 GB of RAM).
- **Lower the view distance:** **Options → Video Settings**, Render Distance **8**, Simulation Distance **5**.
- **Use your graphics card:** press **F3** and check that the **Display** line names your graphics card, not built-in graphics.
- **Teleport rather than fly far and fast.**

## Special instructions

- **Station and sign positions** come from my own coordinates. Each one looks for solid ground within 24 blocks, avoiding roofs, but some may land a little off; use the move command above.
- **The box around the city is a rectangle**, so it includes edges of neighbouring cities (Aliso Viejo, Mission Viejo, Dana Point and Laguna Beach).
- **Newer Minecraft versions:** the datapack allows newer versions, but it was only tested in 26.1.

## How it works

With `--projection web_mercator`, Arnis centres the world on the area using a Web Mercator map frame. `src/generate.py` uses the same formulas as Arnis (`src/projection/web_mercator.rs`) to work out which block each station and sign lands on, and bakes those into the datapack.

When the world first loads, the datapack:
1. temporarily loads those chunks;
2. finds solid ground near each spot;
3. builds the stations and signs;
4. releases the chunks.

The map menu is a Minecraft dialog. Its buttons run `/trigger ln_go`, which every player may use, so there's no "Confirm Command Execution" screen.

## Testing

The datapack was tested in a real 26.1 game, added to a world as a `.zip`:
- every station and tour sign was built on first load, and the temporary chunk loading was released afterwards
- pressing a station button opened the map menu
- the menu's teleport (the same `/trigger` its buttons run) took the player to the last station in the list

The world generation itself wasn't run here, because OpenStreetMap's servers refuse connections from the build environment.

## Building from source

```bash
cd ln
python3 src/generate.py
```

This rebuilds the datapack zip in `release/` and prints the Arnis command and station coordinates. Stations and signs are listed at the top of the script.

## Changelog

- **1.0.0**: First release.
