package mods.hypertnt.test;

import mods.hypertnt.HyperTnt;
import mods.hypertnt.Strike;
import net.fabricmc.fabric.api.client.gametest.v1.context.ClientGameTestContext;
import net.fabricmc.fabric.api.client.gametest.v1.context.TestServerContext;
import net.minecraft.core.BlockPos;
import net.minecraft.core.component.DataComponents;
import net.minecraft.server.MinecraftServer;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.item.component.CustomData;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;

@SuppressWarnings("UnstableApiUsage")
final class HyperTntChecks {
	static final BlockPos C = new BlockPos(300, -30, 0);   // Hyper TNT sits on top of a stone slab

	private HyperTntChecks() {
	}

	static void run(ClientGameTestContext context, TestServerContext server) {
		server.runCommand("gamerule spawn_monsters false");
		server.runCommand("gamerule advance_time false");
		server.runCommand("time set day");
		server.runCommand("gamemode creative @a");
		server.runCommand("forceload add 230 -70 370 70");
		context.waitTicks(60);
		// 110 x 110 x 30 slab of stone to blow a crater in
		for (int y = -60; y < -30; y += 2) {
			server.runCommand("fill 245 " + y + " -55 355 " + (y + 1) + " 55 stone");
		}
		server.runCommand("setblock 300 -30 0 hypertnt:hyper_tnt");
		server.runCommand("setblock 320 -30 0 hypertnt:hyper_tnt");  // NOT linked: must survive
		context.waitTicks(5);

		// 1. Fire, redstone and a normal TNT blast don't set it off.
		server.runCommand("setblock 301 -30 0 redstone_block");
		server.runCommand("setblock 300 -29 0 fire");
		server.runCommand("setblock 299 -30 0 tnt");
		server.runCommand("summon tnt 299 -29 0 {fuse:1}");
		context.waitTicks(80);
		check(block(server, C).equals("hypertnt:hyper_tnt"), "fire, redstone and a TNT blast don't set it off (it's still there)");
		server.runCommand("setblock 301 -30 0 stone");

		// 2. Link with the Detonator: stand next to it, look at it, right-click.
		server.runCommand("item replace entity @p weapon.mainhand with hypertnt:detonator");
		server.runCommand("tp @p 300.5 -29 3.5 180 0");
		context.waitTicks(20);
		context.runOnClient(mc -> {
			Vec3 eye = mc.player.getEyePosition();
			double dx = 300.5 - eye.x, dy = -29.5 - eye.y, dz = 0.5 - eye.z;
			float yaw = (float) (Math.toDegrees(Math.atan2(dz, dx)) - 90.0);
			float pitch = (float) -Math.toDegrees(Math.atan2(dy, Math.sqrt(dx * dx + dz * dz)));
			mc.player.setYRot(yaw); mc.player.yRotO = yaw; mc.player.setXRot(pitch); mc.player.xRotO = pitch;
		});
		context.waitTicks(3);
		context.getInput().pressKey(o -> o.keyUse);
		context.waitTicks(5);
		int links = server.computeOnServer(s -> s.getPlayerList().getPlayers().get(0).getMainHandItem()
				.getOrDefault(DataComponents.CUSTOM_DATA, CustomData.EMPTY).copyTag().getListOrEmpty("links").size());
		check(links == 1, "right-clicking Hyper TNT with the Detonator links it (" + links + " linked)");

		// 3. Step back, look up at the sky and detonate.
		server.runCommand("tp @p 300.5 15 125 180 30");
		context.runOnClient(mc -> { mc.player.getAbilities().flying = true; mc.player.onUpdateAbilities(); });
		context.waitTicks(60);
		int before = Strike.droppedTotal;
		long stoneBefore = countStone(server);
		context.runOnClient(mc -> { mc.player.setXRot(-60); mc.player.xRotO = -60; });
		context.waitTicks(2);
		context.getInput().pressKey(o -> o.keyUse);
		context.waitTick();
		check(Strike.activeCount() == 1, "right-clicking the air sets off the linked Hyper TNT");
		server.runCommand("gamemode spectator @p");
		server.runCommand("tp @p 300.5 0 95 180 25");
		long total = 0, worst = 0;
		int n = 0;
		for (int t = 0; t < 260; t++) {
			context.waitTick();
			long[] times = server.computeOnServer(s -> s.getTickTimesNanos());
			int idx = server.computeOnServer(s -> s.getTickCount()) % times.length;
			long last = times[(idx - 1 + times.length) % times.length];
			total += last; worst = Math.max(worst, last); n++;
			if (t == 40) context.takeScreenshot("strike-raining");
			if (t == 90) context.takeScreenshot("strike-exploding");
		}
		System.out.printf("[hypertnt-test] during the strike: average tick %.1f ms, worst tick %.1f ms (a tick has 50 ms)%n", total / 1e6 / n, worst / 1e6);
		int dropped = Strike.droppedTotal - before;
		check(dropped == Strike.TOTAL_TNT, "dropped exactly " + Strike.TOTAL_TNT + " TNT (" + dropped + ")");
		check(Strike.activeCount() == 0, "strike finished");
		long stoneAfter = countStone(server);
		System.out.println("[hypertnt-test] stone blocks destroyed: " + (stoneBefore - stoneAfter));
		int[] depth = server.computeOnServer(s -> {
			int deepest = 0, centreDepth = 0;
			for (int x = 250; x <= 350; x++) for (int z = -50; z <= 50; z++) {
				int y = -31;
				while (y >= -60 && s.overworld().getBlockState(new BlockPos(x, y, z)).isAir()) y--;
				int d = -31 - y;
				deepest = Math.max(deepest, d);
				if (x == 300 && z == 0) centreDepth = d;
			}
			return new int[] {deepest, centreDepth};
		});
		System.out.println("[hypertnt-test] crater depth: deepest " + depth[0] + " blocks, at the centre " + depth[1]);
		check(stoneBefore - stoneAfter > 30_000, "made a big crater");
		int items = server.computeOnServer(s -> s.overworld().getEntitiesOfClass(ItemEntity.class, new AABB(220, -70, -80, 380, 60, 80)).size());
		check(items == 0, "no item drops (" + items + " items)");
		check(block(server, new BlockPos(320, -30, 0)).equals("hypertnt:hyper_tnt"), "an unlinked Hyper TNT nearby survives (blast-proof)");
		int forced = server.computeOnServer(s -> s.overworld().getForceLoadedChunks().size());
		System.out.println("[hypertnt-test] force-loaded chunks after (test's own forceload area): " + forced);
		server.runCommand("forceload remove all");
		context.waitTicks(5);
		check(server.computeOnServer(s -> s.overworld().getForceLoadedChunks().size()) == 0, "strike released its chunk loading");
		server.runCommand("tp @p 300.5 0 70 180 30");
		context.waitTicks(60);
		context.takeScreenshot("crater");
	}

	static String block(TestServerContext server, BlockPos p) {
		return server.computeOnServer(s -> net.minecraft.core.registries.BuiltInRegistries.BLOCK.getKey(s.overworld().getBlockState(p).getBlock()).toString());
	}

	static long countStone(TestServerContext server) {
		return server.computeOnServer(s -> {
			long c = 0;
			BlockPos.MutableBlockPos m = new BlockPos.MutableBlockPos();
			for (int x = 245; x <= 355; x++) for (int z = -55; z <= 55; z++) for (int y = -60; y < -30; y++) {
				if (s.overworld().getBlockState(m.set(x, y, z)).is(Blocks.STONE)) c++;
			}
			return c;
		});
	}

	static void check(boolean ok, String what) {
		if (!ok) throw new AssertionError("FAILED: " + what);
		System.out.println("[hypertnt-test] PASS: " + what);
	}
}
