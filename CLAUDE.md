# Repo conventions

- Minecraft Java Edition mods, one top-level folder per mod (kebab-case name). Start from `_template/`.
- Every mod folder MUST have a `README.md` with compatibility table, dependencies, and a "Special instructions" section (state "None — drop-in only" if there are none).
- Ship a ready-to-use jar in `<mod>/release/<mod-name>-<version>.jar` so the user can drop it straight into `.minecraft/mods`. Keep only the current version there.
- Keep the source as a self-contained Gradle project inside the mod folder (include the Gradle wrapper).
- When adding or updating a mod, update the **Mods** table in the root `README.md`.
