# Arnis patches

The automatic world builds (`.github/workflows/build-world.yml`) download Arnis at the version in `ARNIS_REF` and apply every `*.patch` in this folder before compiling it. Worlds you generate yourself with an official Arnis release don't include these changes.

## walk-in-buildings.patch

Makes the empty buildings explorable (Arnis's furnished interiors stay off):

- **Open doorways.** Every entrance Arnis would put a door in (street entrances, garage and shed doors) becomes an open gap two blocks tall. The doorstep, steps and canopy outside stay. Doors mapped as separate points in OpenStreetMap no longer get a door leaf either, so they can't close the gap again.
- **Ladders between floors.** Each empty building with more than one storey gets one ladder from the ground floor up through every floor slab to the top floor. It goes against an outside wall, away from the doorways, and the wall column behind it is made solid so the ladder always has something to hang on.
- **Tests.** Arnis's own tests that looked for door blocks now look for the open gap, and a new test checks the ladder (`storeys_are_reached_by_one_ladder_against_a_solid_wall`). The whole Arnis test suite passes with the patch.

To update it after changing Arnis's code in a local clone of the same version: `git diff > walk-in-buildings.patch`, then check it with `git apply --check` on a fresh clone.
