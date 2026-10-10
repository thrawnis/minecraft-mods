package io.github.thrawnis.foreverflying.test;

import io.github.thrawnis.foreverflying.client.ForeverFlyingClient;
import net.fabricmc.fabric.api.client.gametest.v1.context.ClientGameTestContext;
import net.fabricmc.fabric.api.client.gametest.v1.context.TestServerContext;
import net.minecraft.client.player.LocalPlayer;
import net.minecraft.server.level.ServerPlayer;

/** The in-game checks, shared by every Minecraft version (world setup differs per version). */
@SuppressWarnings("UnstableApiUsage")
final class ForeverFlyingChecks {
	private ForeverFlyingChecks() {
	}

	static void check(ClientGameTestContext context, TestServerContext server, String name) {
		server.runCommand("gamerule spawn_monsters false");
		server.runCommand("time set day");
		server.runCommand("gamemode survival @a");
		context.waitFor(mc -> mc.player.onGround(), 200);
		context.waitTicks(10);

		// 1. Flight allowed in survival (client and server agree).
		assertTrue(context.computeOnClient(mc -> mc.player.getAbilities().mayfly), name + ": client may fly in survival");
		assertTrue(server.computeOnServer(s -> player(s).getAbilities().mayfly), name + ": server lets player fly in survival");

		// 2. Double-tap jump starts flying, like creative.
		context.getInput().holdKeyFor(o -> o.keyJump, 1);
		context.waitTick();
		context.getInput().holdKeyFor(o -> o.keyJump, 1);
		context.waitTicks(5);
		assertTrue(context.computeOnClient(mc -> mc.player.getAbilities().flying), name + ": double-tap jump starts flying");
		context.getInput().holdKeyFor(o -> o.keyJump, 10);  // rise a bit
		double groundY = Math.floor(context.computeOnClient(mc -> mc.player.getY())) - 2;

		// 3. Hovering for a long time does not get us kicked (server checks after 80 ticks).
		context.waitTicks(100);
		assertTrue(context.computeOnClient(mc -> mc.player != null && mc.getConnection() != null), name + ": not kicked for flying");

		// 4. Toggle pass-through (V) and sink into the ground.
		context.getInput().pressKey(ForeverFlyingClient.noclipKey);
		context.waitTicks(2);
		context.getInput().holdKeyFor(o -> o.keyShift, 40);
		context.waitTicks(10);
		double clientY = context.computeOnClient(mc -> mc.player.getY());
		double serverY = server.computeOnServer(s -> player(s).getY());
		assertTrue(clientY < groundY - 3, name + ": passed through the ground (y=" + clientY + ", ground=" + groundY + ")");
		assertTrue(Math.abs(clientY - serverY) < 0.5, name + ": server accepted the position (client y=" + clientY + ", server y=" + serverY + ")");
		context.takeScreenshot("foreverflying-" + name + "-inside-ground");

		// 5. Turn pass-through off while inside the ground: no suffocation damage.
		context.getInput().pressKey(ForeverFlyingClient.noclipKey);
		context.waitTicks(60);
		float health = server.computeOnServer(s -> player(s).getHealth());
		assertTrue(health >= 20F, name + ": no suffocation damage (health=" + health + ")");

		// 6. Hold Left Alt + scroll up changes fly speed, not the hotbar slot.
		server.runCommand("tp @a ~ 120 ~");
		context.waitTicks(10);
		int slot = context.computeOnClient(mc -> mc.player.getInventory().getSelectedSlot());
		float before = context.computeOnClient(mc -> mc.player.getAbilities().getFlyingSpeed());
		context.getInput().holdKey(ForeverFlyingClient.speedModifierKey);
		for (int i = 0; i < 4; i++) {
			context.getInput().scroll(1);
			context.waitTick();
		}
		context.getInput().releaseKey(ForeverFlyingClient.speedModifierKey);
		context.waitTicks(2);
		float speed = context.computeOnClient(mc -> mc.player.getAbilities().getFlyingSpeed());
		// 4 scroll steps = +1x (+0.05), capped at 4x (0.2)
		float expected = Math.min(before + 0.05F, 0.2F);
		assertTrue(Math.abs(speed - expected) < 1e-4, name + ": fly speed went up (" + before + " -> " + speed + ")");
		assertTrue(context.computeOnClient(mc -> mc.player.getInventory().getSelectedSlot()) == slot, name + ": hotbar slot unchanged");
		context.takeScreenshot("foreverflying-" + name + "-speed");

		// 7. Stop flying high up and fall: no fall damage.
		context.runOnClient(mc -> {
			LocalPlayer p = mc.player;
			p.getAbilities().flying = false;
			p.onUpdateAbilities();
		});
		context.waitFor(mc -> mc.player.onGround(), 400);
		context.waitTicks(10);
		health = server.computeOnServer(s -> player(s).getHealth());
		assertTrue(health >= 20F, name + ": no fall damage (health=" + health + ")");

		// 8. Switching game modes keeps flight available.
		server.runCommand("gamemode adventure @a");
		context.waitTicks(5);
		server.runCommand("gamemode survival @a");
		context.waitTicks(5);
		assertTrue(context.computeOnClient(mc -> mc.player.getAbilities().mayfly), name + ": may fly after game mode change");
	}

	private static ServerPlayer player(net.minecraft.server.MinecraftServer server) {
		return server.getPlayerList().getPlayers().getFirst();
	}

	private static void assertTrue(boolean condition, String what) {
		if (!condition) {
			throw new AssertionError("FAILED: " + what);
		}
		System.out.println("[foreverflying-test] PASS: " + what);
	}
}
