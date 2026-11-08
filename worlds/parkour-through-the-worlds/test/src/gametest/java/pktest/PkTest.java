package pktest;

import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;

import net.fabricmc.fabric.api.client.gametest.v1.FabricClientGameTest;
import net.fabricmc.fabric.api.client.gametest.v1.context.ClientGameTestContext;
import net.fabricmc.fabric.api.client.gametest.v1.context.TestServerContext;
import net.fabricmc.fabric.api.client.gametest.v1.context.TestSingleplayerContext;
import net.fabricmc.fabric.api.client.gametest.v1.world.TestWorldSave;
import net.minecraft.core.BlockPos;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.Marker;
import net.minecraft.world.phys.Vec3;

/** Plays the whole course with only movement keys (forward, sprint, jump) and mouse-look. */
@SuppressWarnings("UnstableApiUsage")
public class PkTest implements FabricClientGameTest {
	record Node(List<BlockPos> blocks, BlockPos entry, String kind) {}

	@Override
	public void runTest(ClientGameTestContext context) {
		if (System.getProperty("pktest.verifyworld", "").length() > 0) {
			verifyWorld(context);
			return;
		}
		if (System.getProperty("pktest.makeworld", "").length() > 0) {
			makeWorld(context);
			return;
		}
		TestWorldSave save;
		try (TestSingleplayerContext sp = context.worldBuilder().create()) {
			sp.getClientLevel().waitForChunksRender();
			save = sp.getWorldSave();
		}
		JsonObject path;
		try {
			Path dps = save.getSaveDirectory().resolve("datapacks");
			Files.createDirectories(dps);
			Files.copy(Path.of(System.getProperty("pktest.zip")), dps.resolve("ptw.zip"));
			path = JsonParser.parseString(Files.readString(Path.of(System.getProperty("pktest.path")))).getAsJsonObject();
		} catch (Exception e) {
			throw new RuntimeException(e);
		}
		try (TestSingleplayerContext sp = save.open()) {
			sp.getClientLevel().waitForChunksRender();
			TestServerContext server = sp.getServer();
			server.runCommand("gamerule fall_damage false");
			server.runCommand("gamerule advance_time false");
			server.runCommand("time set day");
			server.runCommand("gamemode adventure @a");
			server.runCommand("execute as @p at @p run function ptw:build");
			context.waitFor(mc -> mc.player.getY() > 150, 400);
			context.waitTicks(40);
			sp.getClientLevel().waitForChunksRender();
			BlockPos origin = server.computeOnServer(s -> {
				Marker m = (Marker) s.overworld().getEntities(EntityType.MARKER, e -> e.entityTags().contains("ptw_origin")).get(0);
				return m.blockPosition();
			});
			System.out.println("[pktest] origin " + origin);
			check(context.computeOnClient(mc -> mc.player.getInventory().getItem(7).getHoverName().getString()).equals("Back to checkpoint"), "got the Back to checkpoint item");
			check(context.computeOnClient(mc -> mc.player.getInventory().getItem(8).getHoverName().getString()).equals("Restart course"), "got the Restart course item");
			context.takeScreenshot("lobby");
			server.runCommand("execute as @p run data get entity @s Inventory[{Slot:8b}]");
			server.runCommand("execute as @p run say test predicate");
			server.runCommand("execute as @p if items entity @s hotbar.8 carrot_on_a_stick[custom_data={ptw:\"restart\"}] run say MATCH exact");
			server.runCommand("execute as @p if items entity @s hotbar.8 carrot_on_a_stick run say MATCH any");

			List<Node> nodes = new ArrayList<>();
			for (JsonElement el : path.getAsJsonArray("nodes")) {
				JsonObject o = el.getAsJsonObject();
				List<BlockPos> bs = new ArrayList<>();
				for (JsonElement b : o.getAsJsonArray("blocks")) bs.add(pos(origin, b.getAsJsonArray()));
				nodes.add(new Node(bs, pos(origin, o.getAsJsonArray("entry")), o.get("kind").getAsString()));
			}

			var in = context.getInput();
			if (Boolean.getBoolean("pktest.quick")) {
				server.runCommand("execute at @e[type=marker,scores={ptw_id=1},limit=1] run tp @p ~ ~ ~");
				context.waitTicks(10);
				context.waitTicks(5);
				for (int k = 0; k < 3; k++) System.out.println("[pktest] q: cp=" + score(server, "ptw_cp") + " run=" + score(server, "ptw_run") + " use=" + score(server, "ptw_use"));
				in.pressKey(o -> o.keyHotbarSlots[8]);
				context.waitTicks(5);
				in.pressKey(o -> o.keyUse);
				for (int k = 0; k < 4; k++) {
					context.waitTick();
					System.out.println("[pktest] q after use: cp=" + score(server, "ptw_cp") + " run=" + score(server, "ptw_run") + " use=" + score(server, "ptw_use")
							+ " pos=" + context.computeOnClient(mc -> mc.player.blockPosition()));
				}
				return;
			}
			List<String> failures = new ArrayList<>();
			int cpShots = 0;
			for (int i = 1; i < nodes.size(); i++) {
				Node target = nodes.get(i);
				// ladder/vine bases: aim straight for the top of the wall and climb
				if (target.kind().startsWith("ladder") || target.kind().startsWith("vine")) continue;
				Set<BlockPos> goal = new HashSet<>(target.blocks());
				boolean ok = false;
				Node from = nodes.get(i - 1);
				if (from.kind().startsWith("ladder") || from.kind().startsWith("vine")) from = nodes.get(i - 2);
				BlockPos fb = from.blocks().get(from.blocks().size() - 1);
				double dist = Math.hypot(target.entry().getX() - fb.getX(), target.entry().getZ() - fb.getZ());
				boolean sprint = dist > 2.6 || target.entry().getY() > fb.getY() || target.kind().startsWith("pad") || target.kind().startsWith("ice");
				if (!sprint) {
					// short jump next: slow down first, like a player tapping back after a long landing
					in.releaseKey(o -> o.keyUp);
					in.releaseKey(o -> o.keySprint);
					BlockPos tgt = target.entry();
					for (int b = 0; b < 2 && context.computeOnClient(mc -> {
						var v = mc.player.getDeltaMovement();
						double dx = tgt.getX() + 0.5 - mc.player.getX(), dz = tgt.getZ() + 0.5 - mc.player.getZ(), len = Math.hypot(dx, dz);
						return (v.x * dx + v.z * dz) / len > 0.12; // still moving towards the next block
					}); b++) {
						in.holdKey(o -> o.keyDown);
						context.waitTick();
					}
					in.releaseKey(o -> o.keyDown);
				}
				in.holdKey(o -> o.keyUp);
				if (sprint) in.holdKey(o -> o.keySprint); else in.releaseKey(o -> o.keySprint);
				double[] takeoff = null, low = null;
				for (int t = 0; t < 160 && !ok; t++) {
					Vec3 aim = Vec3.atBottomCenterOf(target.entry()).add(0, 1, 0);
					int act = context.computeOnClient(mc -> {
						var p = mc.player;
						double dx = aim.x - p.getX(), dz = aim.z - p.getZ();
						float yaw = (float) (Math.toDegrees(Math.atan2(dz, dx)) - 90.0);
						p.setYRot(yaw); p.yRotO = yaw; p.setXRot(0); p.xRotO = 0;
						if (!p.onGround()) {
							// in the air: stop pushing forward once over the target, like tapping back
							return Math.hypot(dx, dz) < 0.45 && p.getY() > aim.y - 0.5 ? 2 : 0;
						}
						Vec3 v = p.getDeltaMovement();
						Vec3 next = p.position().add(v.x * 1.0, 0, v.z * 1.0);
						BlockPos under = BlockPos.containing(next.x, p.getY() - 0.2, next.z);
						return mc.level.getBlockState(under).getCollisionShape(mc.level, under).isEmpty() ? 1 : 0;
					});
					if (act == 1) {
						takeoff = context.computeOnClient(mc -> new double[] {mc.player.getX(), mc.player.getY(), mc.player.getZ()});
						in.holdKey(o -> o.keyJump);
						context.waitTick();
						in.releaseKey(o -> o.keyJump);
					} else if (act == 2) {
						in.releaseKey(o -> o.keyUp);
						in.holdKey(o -> o.keyDown);
						context.waitTick();
						in.releaseKey(o -> o.keyDown);
					} else {
						in.holdKey(o -> o.keyUp);
						context.waitTick();
					}
					double[] now = context.computeOnClient(mc -> new double[] {mc.player.getX(), mc.player.getY(), mc.player.getZ(), mc.player.onGround() ? 1 : 0});
					if (takeoff != null && low == null && now[3] == 1 && Math.abs(now[1] - takeoff[1]) < 3) low = now;
					ok = context.computeOnClient(mc -> {
						var p = mc.player;
						if (!p.onGround()) return false;
						for (BlockPos b : goal) {
							if (Math.abs(p.getX() - (b.getX() + 0.5)) < 0.85 && Math.abs(p.getZ() - (b.getZ() + 0.5)) < 0.85
									&& p.getY() >= b.getY() + 0.8 && p.getY() <= b.getY() + 1.6) return true;
						}
						return false;
					});
				}
				if (!ok) {
					String msg = "jump " + i + " (" + target.kind() + ") from " + rel(origin, from.blocks().get(from.blocks().size() - 1))
							+ " to " + rel(origin, target.entry());
					BlockPos o0 = origin;
					java.util.function.Function<double[], String> rp = a -> a == null ? "-" : String.format("(%.2f,%.2f,%.2f)", a[0] - o0.getX(), a[1] - o0.getY(), a[2] - o0.getZ());
					msg += " sprint=" + sprint + " takeoff=" + rp.apply(takeoff) + " firstLanding=" + rp.apply(low);
					failures.add(msg);
					System.out.println("[pktest] FAIL " + msg);
					in.releaseKey(o -> o.keyUp);
					in.releaseKey(o -> o.keySprint);
					BlockPos e = target.entry();
					server.runCommand("tp @p " + (e.getX() + 0.5) + " " + (e.getY() + 1) + " " + (e.getZ() + 0.5));
					context.waitTicks(10);
				}
				if (target.kind().equals("cp")) {
					in.releaseKey(o -> o.keyUp);
					in.releaseKey(o -> o.keySprint);
					context.waitTicks(15);
					int cp = server.computeOnServer(s -> s.getScoreboard().getOrCreatePlayerScore(s.getPlayerList().getPlayers().get(0),
							s.getScoreboard().getObjective("ptw_cp")).get());
					String near = server.computeOnServer(s2 -> {
						var p = s2.getPlayerList().getPlayers().get(0);
						StringBuilder sb = new StringBuilder(" player at " + p.blockPosition() + ";");
						for (var m : s2.overworld().getEntities(EntityType.MARKER, e -> e.entityTags().contains("ptw_cp")))
							if (m.distanceTo(p) < 12) {
								var sc = s2.getScoreboard();
								var idObj = sc.getObjective("ptw_id");
								var hasId = sc.getPlayerScoreInfo(m, idObj);
								sb.append(" marker ").append(m.entityTags()).append(" d=").append(String.format("%.1f", m.distanceTo(p)))
										.append(" id=").append(hasId == null ? "none" : hasId.value());
							}
						return sb.toString();
					});
					System.out.println("[pktest] reached checkpoint, score ptw_cp=" + cp + " floor=" + score(server, "ptw_floor") + near);
					server.runCommand("execute as @p at @p run data get entity @e[type=marker,tag=ptw_cp,sort=nearest,limit=1] data");
					context.takeScreenshot("cp" + (++cpShots));
				}
			}
			in.releaseKey(o -> o.keyUp);
			in.releaseKey(o -> o.keySprint);
			context.waitTicks(20);
			System.out.println("[pktest] bot finished with " + failures.size() + " failed jumps of " + (nodes.size() - 1));
			int run = score(server, "ptw_run"), time = score(server, "ptw_time"), best = score(server, "ptw_best"), board = score(server, "ptw_board");
			System.out.println("[pktest] run=" + run + " time=" + time + " best=" + best + " board=" + board + " falls=" + score(server, "ptw_falls"));
			check(run == 0 && time > 0 && best == time && board == -time, "finish stopped the timer and set the best time");
			check(context.computeOnClient(mc -> mc.player.getInventory().contains(s -> s.getHoverName().getString().equals("Parkour Champion"))), "got the trophy");
			context.takeScreenshot("finish");

			// Fall: step off the finish pad edge downward -> back to the last checkpoint
			int cpBefore = score(server, "ptw_cp");
			server.runCommand("execute as @p at @p run tp @p ~ ~-40 ~");
			context.waitTicks(10);
			boolean back = server.computeOnServer(s -> {
				var p = s.getPlayerList().getPlayers().get(0);
				return s.overworld().getEntities(EntityType.MARKER, m -> m.entityTags().contains("ptw_cp") && m.position().distanceTo(p.position()) < 1.0).size() == 1;
			});
			check(back, "falling sends you back to your checkpoint (" + cpBefore + ")");

			// Restart item: select slot 9 and use it
			in.pressKey(o -> o.keyHotbarSlots[8]);
			context.waitTicks(5);
			System.out.println("[pktest] holding " + context.computeOnClient(mc -> mc.player.getMainHandItem().getHoverName().getString())
					+ " (server: " + server.computeOnServer(s2 -> s2.getPlayerList().getPlayers().get(0).getMainHandItem().getHoverName().getString()) + ")");
			in.pressKey(o -> o.keyUse);
			context.waitTicks(10);
			System.out.println("[pktest] use stat: " + server.computeOnServer(s2 -> s2.getPlayerList().getPlayers().get(0).getStats()
					.getValue(net.minecraft.stats.Stats.ITEM_USED.get(net.minecraft.world.item.Items.CARROT_ON_A_STICK))));
			System.out.println("[pktest] after use: ptw_use=" + score(server, "ptw_use") + " cp=" + score(server, "ptw_cp") + " time=" + score(server, "ptw_time"));
			check(score(server, "ptw_cp") == 0 && score(server, "ptw_time") == 0, "Restart item takes you back to the start");
			context.takeScreenshot("leaderboard");
			check(failures.isEmpty(), "every jump made by the bot: " + failures);
		}
	}

	/** Builds the ready-made world: course at the spawn, adventure mode, friendly settings. */
	static void makeWorld(ClientGameTestContext context) {
		TestWorldSave save;
		try (TestSingleplayerContext sp = context.worldBuilder().adjustSettings(s -> s.setName("Parkour Through the Worlds")).create()) {
			sp.getClientLevel().waitForChunksRender();
			save = sp.getWorldSave();
		}
		try {
			Path dps = save.getSaveDirectory().resolve("datapacks");
			Files.createDirectories(dps);
			Files.copy(Path.of(System.getProperty("pktest.zip")), dps.resolve("parkour-through-the-worlds-datapack.zip"));
		} catch (Exception e) {
			throw new RuntimeException(e);
		}
		try (TestSingleplayerContext sp = save.open()) {
			sp.getClientLevel().waitForChunksRender();
			TestServerContext server = sp.getServer();
			for (String c : new String[] {"gamerule fall_damage false", "gamerule keep_inventory true", "gamerule spawn_mobs false",
					"gamerule spawn_monsters false", "gamerule spawn_phantoms false", "gamerule spawn_patrols false",
					"gamerule spawn_wandering_traders false", "gamerule advance_time false", "gamerule advance_weather false",
					"time set day", "weather clear", "difficulty peaceful", "defaultgamemode adventure", "gamemode adventure @a"}) {
				server.runCommand(c);
			}
			server.runCommand("execute as @p at @p run function ptw:build");
			context.waitFor(mc -> mc.player.getY() > 150, 400);
			context.waitTicks(60);
			server.runCommand("execute as @p at @p run setworldspawn ~ ~ ~ -90");
			sp.getClientLevel().waitForChunksRender();
			context.takeScreenshot("world-spawn");
			System.out.println("[pktest] world built at " + context.computeOnClient(mc -> mc.player.blockPosition()));
		}
		try {
			Path out = Path.of(System.getProperty("pktest.makeworld"));
			Files.createDirectories(out.getParent());
			try (var zip = new java.util.zip.ZipOutputStream(Files.newOutputStream(out)); var walk = Files.walk(save.getSaveDirectory())) {
				for (Path f : (Iterable<Path>) walk::iterator) {
					if (Files.isDirectory(f) || f.getFileName().toString().equals("session.lock")) continue;
					String name = "Parkour Through the Worlds/" + save.getSaveDirectory().relativize(f).toString().replace('\\', '/');
					zip.putNextEntry(new java.util.zip.ZipEntry(name));
					Files.copy(f, zip);
					zip.closeEntry();
				}
			}
			System.out.println("[pktest] wrote " + out);
		} catch (Exception e) {
			throw new RuntimeException(e);
		}
	}

	/** Opens the released world zip like a player would and checks it starts at the course. */
	static void verifyWorld(ClientGameTestContext context) {
		TestWorldSave save;
		try (TestSingleplayerContext sp = context.worldBuilder().create()) {
			save = sp.getWorldSave();
		}
		try {
			Path dir = save.getSaveDirectory();
			try (var walk = Files.walk(dir)) {
				walk.sorted(java.util.Comparator.reverseOrder()).filter(f -> !f.equals(dir)).forEach(f -> f.toFile().delete());
			}
			try (var zin = new java.util.zip.ZipInputStream(Files.newInputStream(Path.of(System.getProperty("pktest.verifyworld"))))) {
				for (var e = zin.getNextEntry(); e != null; e = zin.getNextEntry()) {
					Path f = dir.resolve(e.getName().substring(e.getName().indexOf('/') + 1));
					Files.createDirectories(f.getParent());
					Files.copy(zin, f);
				}
			}
		} catch (Exception e) {
			throw new RuntimeException(e);
		}
		try (TestSingleplayerContext sp = save.open()) {
			sp.getClientLevel().waitForChunksRender();
			context.waitTicks(40);
			TestServerContext server = sp.getServer();
			check(context.computeOnClient(mc -> mc.player.getY() > 199), "you start up at the course (y=" + context.computeOnClient(mc -> mc.player.getY()) + ")");
			check(context.computeOnClient(mc -> mc.gameMode.getPlayerMode().getName()).equals("adventure"), "adventure mode");
			check(context.computeOnClient(mc -> mc.player.getInventory().getItem(8).getHoverName().getString()).equals("Restart course"), "items in the hotbar");
			check(server.computeOnServer(s -> s.getCommandStorage().get(net.minecraft.resources.Identifier.fromNamespaceAndPath("ptw", "state")).contains("built")), "course is built and the datapack is active");
			// walk off the start: the timer starts
			context.getInput().holdKeyFor(o -> o.keyUp, 40);
			context.waitTicks(20);
			System.out.println("[pktest] after walking off: run=" + score(server, "ptw_run") + " time=" + score(server, "ptw_time") + " falls=" + score(server, "ptw_falls") + " cp=" + score(server, "ptw_cp"));
			context.takeScreenshot("verify-world");
		}
	}

	static BlockPos pos(BlockPos origin, JsonArray a) {
		return origin.offset(a.get(0).getAsInt(), a.get(1).getAsInt(), a.get(2).getAsInt());
	}

	static String rel(BlockPos origin, BlockPos b) {
		return "[" + (b.getX() - origin.getX()) + "," + (b.getY() - origin.getY()) + "," + (b.getZ() - origin.getZ()) + "]";
	}

	static int score(TestServerContext server, String obj) {
		return server.computeOnServer(s -> s.getScoreboard().getOrCreatePlayerScore(s.getPlayerList().getPlayers().get(0),
				s.getScoreboard().getObjective(obj)).get());
	}

	static void check(boolean ok, String what) {
		if (!ok) throw new AssertionError("FAILED: " + what);
		System.out.println("[pktest] PASS: " + what);
	}
}
