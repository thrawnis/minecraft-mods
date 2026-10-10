# Minecraft Mods

A collection of Minecraft **Java Edition** mods. Each mod lives in its own top-level folder.

## Repository layout

```
minecraft-mods/
├── README.md              ← this file (index of all mods)
├── _template/             ← copy this to start a new mod folder
│   └── README.md
└── <mod-name>/            ← one folder per mod (kebab-case)
    ├── README.md          ← required: install notes, versions, dependencies
    ├── release/           ← ready-to-use .jar — drop this into your mods folder
    │   └── <mod-name>-<version>.jar
    └── src/ …             ← source code / build files (Gradle project)
```

## Installing a mod

1. Install the mod loader the mod requires (Fabric, Forge, or NeoForge — see the mod's README)
   for the matching Minecraft version.
2. Copy the `.jar` from the mod's `release/` folder into your `mods` folder:
   - **Windows:** `%APPDATA%\.minecraft\mods`
   - **macOS:** `~/Library/Application Support/minecraft/mods`
   - **Linux:** `~/.minecraft/mods`
3. Install any additional dependencies listed in the mod's README (e.g. Fabric API).
4. Launch Minecraft using the loader's profile.

If a mod needs anything beyond "drop the jar in", its README has a **Special instructions** section.

## Mods

| Mod | Description | Minecraft | Loader | Folder |
|-----|-------------|-----------|--------|--------|
| _none yet_ | | | | |

## Adding a new mod

1. Copy `_template/` to a new folder named after the mod in kebab-case (e.g. `better-torches/`).
2. Fill in the README — especially Minecraft version, loader, dependencies, and any special instructions.
3. Put the built jar in `release/` (named `<mod-name>-<version>.jar`) and remove older versions.
4. Add a row to the **Mods** table above.
