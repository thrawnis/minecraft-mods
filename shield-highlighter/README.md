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

1. **Install Fabric** if you haven't already. Follow the step-by-step guide in [Forever Flying's README](../forever-flying/README.md#step-1-install-fabric-one-time).
2. **Download Fabric API** for your Minecraft version from https://modrinth.com/mod/fabric-api (**Versions** tab).
3. **Pick the Shield Highlighter jar** for your Minecraft version from `release/`:

   | Minecraft version | File |
   |---|---|
   | 26.1, 26.1.1, 26.1.2 | `shield-highlighter-1.0.0+mc26.1.jar` |
   | 26.2 | `shield-highlighter-1.0.0+mc26.2.jar` |
   | 26.3 | `shield-highlighter-1.0.0+mc26.3.jar` |

4. Put **both jars** into your `mods` folder (`%APPDATA%\.minecraft\mods` on Windows, `~/Library/Application Support/minecraft/mods` on macOS, `~/.minecraft/mods` on Linux).
5. Start Minecraft with the **fabric-loader** profile.

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
cd shield-highlighter
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
