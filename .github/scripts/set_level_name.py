"""Set the world name shown in Minecraft's Singleplayer list (level.dat Data.LevelName)."""
import sys

import nbtlib

path, name = sys.argv[1], sys.argv[2]
level = nbtlib.load(path)
level["Data"]["LevelName"] = nbtlib.String(name)
level.save()
print(f"LevelName set to {name!r}")
