# Shield Highlighter

Shows at a glance whether an opponent's shield can block right now:

- **Bright green**: they're holding a shield and it works. They get a green outline, and the shield itself is tinted green.
- **Dark red**: their shield has been disabled (stunned), for example by an axe hit. They get a dark red outline and a red-tinted shield until it works again.

Highlights only show for players you can actually see. There's no outline through walls.

## Compatibility

| | |
|---|---|
| **Type** | Mod |
| **Minecraft version** | Java Edition 26.1.x, 26.2, 26.3 (one jar per version) |
| **Mod loader** | Fabric Loader 0.19.5 or newer |
| **Java version** | 25 (bundled with the Minecraft launcher) |
| **Mod version** | 1.0.0 |
| **Side** | Client only. Install it in your own game; servers don't need it. |

## Dependencies

- [Fabric Loader](https://fabricmc.net/use/installer/), required.
- [Fabric API](https://modrinth.com/mod/fabric-api), required. Download the version that matches your Minecraft version.

## Installation

Three steps: install Fabric once, add the two mod files, then start the game with the Fabric profile. If you already installed Fabric for another mod (like Forever Flying), skip Step 1.

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

1. **Download Fabric API** (needed by almost every Fabric mod) from https://modrinth.com/mod/fabric-api: open the **Versions** tab and download the file for your Minecraft version. If it's already in your `mods` folder, you don't need another copy.
2. **Pick the Shield Highlighter jar for your Minecraft version** from `release/`:

   | Minecraft version | File |
   |---|---|
   | 26.1, 26.1.1, 26.1.2 | `shield-highlighter-1.0.0+mc26.1.jar` |
   | 26.2 | `shield-highlighter-1.0.0+mc26.2.jar` |
   | 26.3 | `shield-highlighter-1.0.0+mc26.3.jar` |

3. **Put both jars** (Fabric API and Shield Highlighter) into your `mods` folder. Don't unzip them. Create the folder if it doesn't exist:
   - **Windows:** press **Win + R**, type `%APPDATA%\.minecraft\mods`, press Enter.
   - **macOS:** in Finder, **Go → Go to Folder…**, type `~/Library/Application Support/minecraft/mods`.
   - **Linux:** `~/.minecraft/mods`

### Step 3: Play

Start the launcher, select the **fabric-loader** profile, click **Play**. Servers don't need the mod, so you can join any server as usual.

### Troubleshooting

- **The game says a mod needs a different Minecraft version, or "Incompatible mods found":** the Shield Highlighter or Fabric API jar doesn't match your Minecraft version. Download the matching ones and remove the others from `mods`.
- **"requires fabric-api":** Fabric API is missing from `mods`.
- **No fabric-loader profile in the launcher:** run the Fabric installer again and make sure **Create profile** is ticked and the launcher was closed while installing.

## Usage

There's nothing to press: the mod works whenever you're near other players.

| You see | It means |
|---|---|
| Bright green outline and green shield | They hold a shield that can block right now. Hitting them will be blocked if they raise it. |
| Dark red outline and red shield | Their shield is disabled (e.g. you or someone else hit it with an axe). Attack now: they can't block until it turns green again. |
| No highlight | They aren't holding a shield, or you can't see them (they're behind blocks). |

**Typical PvP use:** when an opponent turns green and raises their shield, hit it with an **axe** to disable it. They turn dark red; switch to your sword and attack until they turn green again (about 5 seconds with a normal axe).

**Try it out:** you need another player, for example a friend on a LAN world (**Esc → Open to LAN**) or any server. Give them a shield and hit it with an axe.

**Turn it off / remove it:** pick your normal (not fabric-loader) profile in the launcher, or delete the Shield Highlighter jar from your `mods` folder.

## Special instructions

- **How the disabled timer works:** Minecraft only tells a shield's owner how long it's disabled. Everyone else just hears the shield-break sound. This mod listens for that sound:
  - **You disabled it** (you hit them and their shield broke): the timer is exact, based on your weapon.
  - **Someone else disabled it:** the mod assumes a normal axe hit, which is 5 seconds. On servers where weapons have custom disable times, red may end a little early or late.
- **Always on.** There's no toggle key. Remove the jar to turn it off.
- **Only other players** are highlighted, never you and never mobs.
- **Outline style:** it uses Minecraft's Glowing outline. If an opponent is only partly behind a block, you may see the outline of the hidden part too.
- **Patterned shields:** the tint colours the shield's wood. Banner patterns on a shield keep their own colours, but the outline still shows the status.
- **Server rules:** some PvP servers don't allow client mods that show extra information. Check a server's rules before using it there.

## Building from source

Needs Java 25 (e.g. [Temurin 25](https://adoptium.net/)). The Gradle wrapper downloads everything else.

```bash
cd mods/shield-highlighter
./gradlew build -Pmc=26.1     # or 26.2 / 26.3
# output: build/libs/shield-highlighter-<version>+mc<mc>.jar  → copy to release/
```

Automated in-game tests (start a real client and world):

```bash
./gradlew runClientGameTest -Pmc=26.1               # needs a display
xvfb-run -a ./gradlew runClientGameTest -Pmc=26.1   # Linux without a display
```

Only one client can run in a test, so the "opponent" is a player created on the client side, and its shield is disabled by playing the shield's real disable sound at its position. This is the same path a server's sound takes.

**Project layout:** the mod's code is the same for every supported Minecraft version (`src/`). Only the test entry point differs (`versioned/`). To add a version, add it to `targets` in `build.gradle`, build, and run the tests.

## Changelog

- **1.0.0**: First release. Green/dark-red outline and shield tint, no through-wall highlighting, exact timer for shields you disable yourself. Builds for 26.1.x, 26.2 and 26.3.
