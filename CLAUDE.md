# Repo conventions

- Minecraft Java Edition mods, resource (texture) packs and worlds/maps, one folder per project (kebab-case name), grouped by type: `mods/<name>/`, `texture-packs/<name>/`, `worlds/<name>/`. Start from `_template/`.
- Every project folder MUST have a `README.md` with compatibility table, dependencies, **Installation** (self-contained, step by step, including mod-loader install if needed) and **Usage** (controls/commands, how to try it, how to turn it off) sections, and a "Special instructions" section (state "None — drop-in only" if there are none).
- Ship ready-to-use files in `<project>/release/` so the user can drop them straight in:
  - Mods: `<name>-<version>.jar` → `.minecraft/mods`
  - Resource packs: `<name>[-<variant>]-<version>.zip` → `.minecraft/resourcepacks`
  - Keep only the current version there.
- Keep source/build inputs inside the project folder: a self-contained Gradle project (with wrapper) for mods; for resource packs, the pack sources or the script that generates them.
- Don't commit Mojang's copyrighted assets; use original artwork.
- Ask the user rather than assume when requirements are unclear (loader, Minecraft version, approach, etc.).
- When adding or updating a project, update the **Mods & packs** table in the root `README.md`.
- Keep the owner's personal info out of everything committed (code, tests, metadata, READMEs, release files): no names, usernames, emails or domains. Use neutral package names (`mods.<modid>`), leave `authors`/`contact` out of `fabric.mod.json`, and refer to "this repository's Releases page" instead of a URL with the username.
