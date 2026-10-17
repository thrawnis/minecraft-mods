# Minecraft Mods

A collection of Minecraft **Java Edition** mods and resource (texture) packs. Each one lives in its own top-level folder.

## Repository layout

```
minecraft-mods/
├── README.md              ← this file (index of all mods)
├── _template/             ← copy this to start a new mod folder
│   └── README.md
└── <mod-name>/            ← one folder per mod (kebab-case)
    ├── README.md          ← required: install notes, versions, dependencies
    ├── release/           ← ready-to-use file(s) — drop straight into Minecraft
    │   └── <mod-name>-<version>.jar   (mod → mods folder)
    │       <pack-name>-<version>.zip  (resource pack → resourcepacks folder)
    └── src/ …             ← source code / build files
```

## Installing a resource pack

1. Copy the `.zip` from the pack's `release/` folder (don't unzip it) into your `resourcepacks` folder
   (same locations as below, with `resourcepacks` instead of `mods`).
2. In game: **Options → Resource Packs**, move it to **Selected**, click **Done**.

## Installing a mod

1. Install the mod loader the mod requires (Fabric, Forge, or NeoForge) for the matching Minecraft version.
   Each mod's README has step-by-step loader install instructions (for Fabric, see
   [Forever Flying's guide](forever-flying/README.md#step-1-install-fabric-one-time)).
2. Copy the `.jar` from the mod's `release/` folder into your `mods` folder:
   - **Windows:** `%APPDATA%\.minecraft\mods`
   - **macOS:** `~/Library/Application Support/minecraft/mods`
   - **Linux:** `~/.minecraft/mods`
3. Install any additional dependencies listed in the mod's README (e.g. Fabric API).
4. Launch Minecraft using the loader's profile.

If a mod needs anything beyond "drop the jar in", its README has a **Special instructions** section.

## Mods & packs

| Name | Type | Description | Minecraft | Loader | Folder |
|------|------|-------------|-----------|--------|--------|
| Low Fire Texture Pack | Resource pack | Lowers the on-screen fire when you're burning (3 heights × orange/blue/green/purple) | 26.1+ | None | [`low-fire-texture-pack/`](low-fire-texture-pack/) |
| Low Shield Texture Pack | Resource pack | Smaller, lower shield when carrying and blocking (3 sizes) | 26.1+ | None | [`low-shield-texture-pack/`](low-shield-texture-pack/) |
| Forever Flying | Mod | Fly in any game mode, pass through blocks (V), Alt+scroll fly speed, no fall/suffocation damage | 26.1, 26.2, 26.3 | Fabric | [`forever-flying/`](forever-flying/) |
| Rainbow Cobwebs | Resource pack | 70%-solid see-through cobwebs that fade blue/red/yellow/green, mixed per web | 26.1+ | None | [`rainbow-cobwebs/`](rainbow-cobwebs/) |
| Shield Highlighter | Mod | Opponents' shields glow bright green when usable, dark red while disabled (not through walls) | 26.1, 26.2, 26.3 | Fabric | [`shield-highlighter/`](shield-highlighter/) |

## Adding a new mod

1. Copy `_template/` to a new folder named after the mod in kebab-case (e.g. `better-torches/`).
2. Fill in the README — especially Minecraft version, loader, dependencies, and any special instructions.
3. Put the built jar (mods) or zip (resource packs) in `release/` and remove older versions.
4. Add a row to the **Mods & packs** table above.
