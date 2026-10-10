# Forever Flying

Fly in any game mode (survival, adventure, creative) and fly straight through blocks.

- **Fly anywhere:** double-tap **Jump** to start or stop flying, just like creative mode, in every game mode.
- **Pass through blocks:** press **V** to turn pass-through on or off. It only works while you're flying; when you land, blocks are solid again.
- **Fly speed:** hold **Left Alt** and **scroll** the mouse wheel while flying to change speed, from 0.25x to 4x in 0.25x steps. The speed resets when you close the game.
- **No fall damage** and **no suffocation damage.**

All keys can be changed in **Options → Controls → Key Binds → Forever Flying**.

## Compatibility

| | |
|---|---|
| **Type** | Mod |
| **Minecraft version** | Java Edition 26.1.x, 26.2, 26.3 (one jar per version) |
| **Mod loader** | Fabric Loader 0.19.5 or newer |
| **Java version** | 25 (bundled with the Minecraft launcher) |
| **Mod version** | 1.0.0 |
| **Side** | Both: install it in your game; on a multiplayer server it must also be on the server |

## Dependencies

- [Fabric Loader](https://fabricmc.net/use/installer/), required.
- [Fabric API](https://modrinth.com/mod/fabric-api), required. Download the version that matches your Minecraft version.

## Installation

Three steps: install Fabric once, add the two mod files, then start the game with the Fabric profile.

### Step 1: Install Fabric (one-time)

Fabric is a free mod loader. It adds a separate **fabric-loader** profile to the Minecraft launcher, and your normal (unmodded) profile keeps working as before.

1. **Run Minecraft once without mods** for the version you want (for example 26.1), then close it. This makes sure the game and your `.minecraft` folder exist.
2. **Download the Fabric installer** from https://fabricmc.net/use/installer/
   - **Windows:** click **Download for Windows** (an `.exe`).
   - **macOS / Linux:** click **Download universal JAR** (a `.jar`). You need Java to open it; if double-clicking does nothing, install Java 25 from https://adoptium.net/ and try again, or run `java -jar fabric-installer-*.jar` in a terminal.
3. **Run the installer** and on the **Client** tab:
   - **Minecraft Version:** choose the version you play (e.g. 26.1).
   - **Loader Version:** leave it on the newest.
   - **Launcher Location:** leave the default.
   - Keep **Create profile** ticked.
   - Click **Install**, wait for "Successfully installed", then close the installer.
4. **Open the Minecraft launcher.** Next to the **Play** button, pick the new **fabric-loader-26.1** profile (the number matches your version). If you don't see it, look under **Installations** and make sure it's enabled.
5. Click **Play** once to check it starts, then close the game. This also creates the `mods` folder.

### Step 2: Add the mod files

1. **Download Fabric API** (needed by almost every Fabric mod) from https://modrinth.com/mod/fabric-api: open the **Versions** tab and download the file for your Minecraft version.
2. **Pick the Forever Flying jar for your Minecraft version** from `release/`:

   | Minecraft version | File |
   |---|---|
   | 26.1, 26.1.1, 26.1.2 | `forever-flying-1.0.0+mc26.1.jar` |
   | 26.2 | `forever-flying-1.0.0+mc26.2.jar` |
   | 26.3 | `forever-flying-1.0.0+mc26.3.jar` |

3. **Put both jars** (Fabric API and Forever Flying) into your `mods` folder. Don't unzip them. Create the folder if it doesn't exist:
   - **Windows:** press **Win + R**, type `%APPDATA%\.minecraft\mods`, press Enter.
   - **macOS:** in Finder, **Go → Go to Folder…**, type `~/Library/Application Support/minecraft/mods`.
   - **Linux:** `~/.minecraft/mods`

### Step 3: Play

Start the launcher, select the **fabric-loader** profile, click **Play**. To check it worked: on the title screen click **Options → Controls → Key Binds** and scroll to the **Forever Flying** section.

To play without mods again, just pick your normal profile in the launcher.

### Your server (only if you want it in multiplayer)

The server needs Fabric and the same two jars.

1. Go to https://fabricmc.net/use/server/, choose your server's **Minecraft version**, leave the loader and installer versions on the newest, and click the **Executable Server (.jar)** download button.
2. Put that jar in an empty folder for the server (or your existing server folder; back up its world first) and start it once:
   ```bash
   java -Xmx2G -jar fabric-server-mc.<version>-loader.<...>.jar nogui
   ```
   It downloads the game, then stops and asks you to accept the EULA: open `eula.txt`, change `eula=false` to `eula=true`, save.
3. Put **Fabric API** and the matching **Forever Flying** jar into the server's `mods` folder.
4. Start the server again with the same command.

### Troubleshooting

- **The game says a mod needs a different Minecraft version, or "Incompatible mods found":** the Forever Flying or Fabric API jar doesn't match your Minecraft version. Download the matching ones and remove the others from `mods`.
- **"requires fabric-api":** Fabric API is missing from `mods`.
- **No fabric-loader profile in the launcher:** run the Fabric installer again and make sure **Create profile** is ticked and the launcher was closed while installing.

## Special instructions

- **Who can use it:** in singleplayer, it just works. On a server, every player who has Forever Flying installed in their own game can fly and pass through blocks. Players without the mod play normally.
- **Servers without the mod:** flying and pass-through don't work there (pressing V shows "Forever Flying isn't installed on this server"). Using this on servers you don't run is usually against their rules.
- **Removing the mod:** players keep the "allowed to fly" setting in their save until their game mode changes. Switch game modes once (e.g. `/gamemode survival`) to clear it.
- **The void still kills you.** Pass-through also goes through bedrock, so don't sink below the bottom of the world.
- **New Minecraft versions** usually need a rebuilt jar. See *Building from source*.

## Building from source

Needs Java 25 (e.g. [Temurin 25](https://adoptium.net/)). The Gradle wrapper downloads everything else.

```bash
cd forever-flying
./gradlew build -Pmc=26.1     # or 26.2 / 26.3
# output: build/libs/forever-flying-<version>+mc<mc>.jar  → copy to release/
```

Run the automated in-game tests (they start a real client, a singleplayer world and a dedicated server):

```bash
./gradlew runClientGameTest -Pmc=26.1           # needs a display
xvfb-run -a ./gradlew runClientGameTest -Pmc=26.1   # Linux without a display
```

On a Linux machine without a graphics card, 26.3 needs Mesa's software Vulkan driver (`mesa-vulkan-drivers`) because its new renderer can't open an OpenGL window under Xvfb.

**Project layout:** shared code is in `src/`. The few pieces that differ between Minecraft versions are in `versioned/mc26.1/` and `versioned/mc26.2+/`. To add a new Minecraft version, add it to `targets` in `build.gradle` (with its Fabric API version from https://fabricmc.net/develop), build it, and run the tests.

## Changelog

- **1.0.0**: First release. Flight in any game mode, pass through blocks (V), Alt+scroll fly speed, no fall or suffocation damage. Builds for 26.1.x, 26.2 and 26.3.
