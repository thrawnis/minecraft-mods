# Low Shield Texture Pack

Makes the shield smaller on your screen, both while you're just holding it and when you raise it to block, and moves it lower so it covers less of your view in PvP. It also looks smaller in third-person (F5) view.

## Compatibility

| | |
|---|---|
| **Type** | Resource (texture) pack — no mod loader needed |
| **Minecraft version** | Java Edition 26.1 and newer |
| **Pack version** | 1.0.0 |
| **Side** | Client only — works on any server, nothing needed server-side |

## Dependencies

_None._

## Installation

1. Pick one size from `release/`:

   | File | Shield size | Moved lower (first person) |
   |---|---|---|
   | `low-shield-texture-pack-small-1.0.0.zip` | 75% | a little |
   | `low-shield-texture-pack-smaller-1.0.0.zip` | 55% | more |
   | `low-shield-texture-pack-smallest-1.0.0.zip` | 40% | most |

2. Drop the `.zip` (don't unzip it) into your `resourcepacks` folder:
   - **Windows:** `%APPDATA%\.minecraft\resourcepacks`
   - **macOS:** `~/Library/Application Support/minecraft/resourcepacks`
   - **Linux:** `~/.minecraft/resourcepacks`
3. In game: **Options → Resource Packs**, move the pack to the **Selected** column, then click **Done**.

## Special instructions

- **Use only one size at a time.** If more than one is selected, the one highest in the list wins.
- **Works with other packs** such as the Low Fire Texture Pack. It only changes the shield's size and position, not its texture, so banner patterns and shield texture packs still show.
- **Third person only changes for you.** Other players see a normal-size shield unless they use this pack too.
- **Size only, not hitbox.** Blocking works exactly the same; only how the shield is drawn changes.
- **Newer Minecraft versions:** the pack declares support for all future formats. If a future version ever shows it as "made for an older version", it will still load. Click through the warning.

## How it works

It replaces the shield's two item models (`models/item/shield.json` for carrying, `models/item/shield_blocking.json` for blocking) with copies whose first- and third-person display transforms are scaled down, and whose first-person position is lowered. Inventory, dropped-item, item-frame and shelf views are left at vanilla values.

## Building from source

Needs Python 3 and Pillow (`pip install pillow`):

```bash
cd low-shield-texture-pack
python3 src/generate.py
```

This rebuilds every `.zip` in `release/`. Sizes and how far each one is lowered are set in `VARIANTS` in `src/generate.py`. To release a new version, bump `VERSION` and delete the old zips.

## Changelog

- **1.0.0**: First release. Three sizes (75%, 55%, 40%), lowered in first person, smaller in third person.
