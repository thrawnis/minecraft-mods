# Repo conventions

- Minecraft Java Edition mods and resource (texture) packs, one top-level folder per project (kebab-case name). Start from `_template/`.
- Every project folder MUST have a `README.md` with compatibility table, dependencies, and a "Special instructions" section (state "None — drop-in only" if there are none).
- Ship ready-to-use files in `<project>/release/` so the user can drop them straight in:
  - Mods: `<name>-<version>.jar` → `.minecraft/mods`
  - Resource packs: `<name>[-<variant>]-<version>.zip` → `.minecraft/resourcepacks`
  - Keep only the current version there.
- Keep source/build inputs inside the project folder: a self-contained Gradle project (with wrapper) for mods; for resource packs, the pack sources or the script that generates them.
- Don't commit Mojang's copyrighted assets; use original artwork.
- Ask the user rather than assume when requirements are unclear (loader, Minecraft version, approach, etc.).
- When adding or updating a project, update the **Mods & packs** table in the root `README.md`.
