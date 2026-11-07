# Parkour Through the Worlds

A sky-high parkour course through eight themed zones that get harder as you go:

| Zone | Theme | What's new |
|---|---|---|
| 1 | Plains | Easy 1–2 block gaps and small step-ups |
| 2 | Jungle | Sprint jumps and a vine climb |
| 3 | Desert | Sandstone pillars, longer gaps, a wall-post landing |
| 4 | Ocean | Sea lanterns, a ladder climb, 4-block drops |
| 5 | Ice | Slippery packed ice and blue-ice runways for long jumps |
| 6 | Nether | Soul sand slows you down; fence-post landings |
| 7 | Deep Dark | Sculk and deepslate, longer jumps, a ladder |
| 8 | The End | End rods to land on, long sprint jumps, the finish |

About 100 jumps and 7 checkpoints. Expect 10–20 minutes, depending on how often you fall.

**Features:**
- **Checkpoints:** a pad at the end of each zone. Fall and you're put back on your last checkpoint, not the start.
- **Timer and fall counter:** shown above your hotbar while you run. The timer starts when you leave the start platform.
- **Best times leaderboard:** shown on the right of the screen, with everyone's best time, fastest first.
- **Finish rewards:** fireworks, a "Finished!" title, and a **Parkour Champion** trophy the first time you finish.
- **Two hotbar items:** **Back to checkpoint** and **Restart course**.
- **Friends:** works for several players at once, on a LAN world or a server. Everyone has their own timer and checkpoint.

## Compatibility

| | |
|---|---|
| **Type** | Map: a ready-made world, plus a datapack to add the course to any world |
| **Minecraft version** | Java Edition 26.1 (tested in 26.1) |
| **Mod loader** | None needed |
| **Version** | 1.0.0 |
| **Players** | 1 or more (singleplayer, LAN or server) |

## Dependencies

_None._

## Installation

There are two ways to get it. Use **one**.

### Option A: Ready-made world (recommended)

1. Download `release/parkour-through-the-worlds-world-1.0.0.zip`.
2. **Unzip it.** You get a folder called **Parkour Through the Worlds**.
3. Move that folder into your Minecraft `saves` folder:
   - **Windows:** press **Win + R**, type `%APPDATA%\.minecraft\saves`, press Enter.
   - **macOS:** in Finder, **Go → Go to Folder…**, type `~/Library/Application Support/minecraft/saves`.
   - **Linux:** `~/.minecraft/saves`
4. Start Minecraft **26.1**, click **Singleplayer**, and open **Parkour Through the Worlds**.

The world is already set up for parkour:
- adventure mode, so blocks can't be broken
- always daytime and clear weather
- no mobs
- no fall damage
- you keep your items when you die

### Option B: Datapack (add the course to any world)

1. **Make a backup** of the world first. The course replaces whatever is in the sky where it's built.
2. With the world closed, copy `release/parkour-through-the-worlds-datapack-1.0.0.zip` (don't unzip it) into that world's `datapacks` folder:
   `<saves folder>/<your world>/datapacks/`
   (Saves folder: `%APPDATA%\.minecraft\saves` on Windows, `~/Library/Application Support/minecraft/saves` on macOS, `~/.minecraft/saves` on Linux.)
3. Open the world. Cheats must be on (the world was created with **Allow Commands**, or you used **Esc → Open to LAN → Allow Commands: ON**).
4. Stand where you want the course and type:
   ```
   /function ptw:build
   ```
   The course is built **at height 200, straight above you**. It covers an area of about 240 × 90 blocks, mostly to the east. You're teleported to the start.
5. Optional: switch to adventure mode with `/gamemode adventure`, so you can't break the course by accident.

Build the course only once per world. Running `/function ptw:build` again rebuilds it at your new position, but the old one stays where it was.

## Usage

**Starting a run:**
1. You start on a grey platform with a gold edge. Two items are in your hotbar: **Back to checkpoint** (slot 8, a compass) and **Restart course** (slot 9, a clock).
2. Run east (the way you're facing) and jump onto the first block. The timer starts as soon as you leave the platform.
3. Above your hotbar you'll see your **Time**, **Falls** and **Checkpoint** (for example 3/7).

**Playing:**
- **Checkpoints** are the larger square pads at the end of each zone, with an emerald block in the middle and a sign naming the next zone. Step on one to save your progress; a title shows which zone is next.
- **Fall** off the course and you're teleported back to your last checkpoint. The fall counter goes up, and the timer keeps running.
- **Climb** ladders and vines by walking into them.
- **Sprint** (double-tap **W**, or hold **Ctrl**) for the longer jumps, especially after the blue-ice runways in the Ice zone.

**Your items** (select the slot, then right-click):

| Item | What it does |
|---|---|
| **Back to checkpoint** | Teleports you to your last checkpoint (handy if you're stuck) |
| **Restart course** | Back to the start, with the timer and falls reset |

If you lose the items, use **Restart course** in chat instead: type `/trigger ptw_restart`, or `/trigger ptw_back` for back to checkpoint. These work without cheats, and restarting gives you the items again.

**Finishing:**
- The finish is a large **gold platform** with a diamond block in the middle, at the end of The End zone.
- Step on it to stop the timer. You get a title with your time, fireworks, and a chat message to everyone.
- If it's your fastest time, it goes on the **Best times** list on the right of the screen.
- Your first finish also earns the **Parkour Champion** trophy (a glowing nether star).
- To go again, use **Restart course**.

**Rules for the leaderboard:**
- Finishing in creative mode doesn't count. Play in adventure or survival.

## Special instructions

- **Multiplayer:** everyone joining the world or server gets their own timer, checkpoint and items, and all players share one leaderboard.
- **Datapack version, in a normal world:** the timer, checkpoints and falls only apply to players inside the course area. Players elsewhere in the world aren't affected.
- **Hide the leaderboard:** `/scoreboard objectives setdisplay sidebar` (needs cheats). Show it again with `/scoreboard objectives setdisplay sidebar ptw_board`.
- **Newer Minecraft versions:** the datapack allows newer versions, but it was only tested in 26.1.

## How it was tested

The course and datapack were tested in a real 26.1 game by a bot that played the whole course using only movement keys: forward, sprint, back and jump, plus turning to face the next block.
- **Every jump:** the bot made all of them in one run with 0 falls, in 1:28.2.
- **Unverifiable jumps removed:** while designing the course, jumps the bot couldn't reliably make (4-block flat gaps and 3-up-1 jumps, even with a run-up) were replaced, so every jump in the course has been made in-game.
- **Features checked in the same run:** the hotbar items, every checkpoint, falling back to a checkpoint, the timer, the finish (title, best time, leaderboard, trophy) and the Restart item.
- **The ready-made world zip:** opened again as a fresh world. It starts at the course in adventure mode with the items, and leaving the start platform starts the timer.

A human player isn't as precise as the bot, so expect some falls on the later zones; that's the point of the checkpoints.

## Building from source

Needs Python 3:

```bash
cd parkour-through-the-worlds
python3 src/generate.py
```

This rebuilds `release/parkour-through-the-worlds-datapack-1.0.0.zip` and `src/path.json`, the course path the bot follows. The zones and jumps are listed at the top of `src/generate.py`. Each jump is a `(forward, up, sideways, kind)` step from the block you're on.

**In-game tests** (needs Java 25; the first run downloads Minecraft):

```bash
cd parkour-through-the-worlds/test
./gradlew runClientGameTest                                                              # bot plays the course
./gradlew runClientGameTest -Pmakeworld=../release/parkour-through-the-worlds-world-1.0.0.zip    # rebuild the world zip
./gradlew runClientGameTest -Pverifyworld=../release/parkour-through-the-worlds-world-1.0.0.zip  # open it and check it
```

On Linux without a screen, put `xvfb-run -a` in front.

## Changelog

- **1.0.0**: First release. Eight zones, about 100 jumps, checkpoints, timer, fall counter, leaderboard, finish rewards, ready-made world and datapack.
