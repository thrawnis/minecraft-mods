package io.github.thrawnis.shieldhighlighter.test;

import java.util.UUID;

import com.mojang.authlib.GameProfile;

import io.github.thrawnis.shieldhighlighter.ShieldTracker;
import io.github.thrawnis.shieldhighlighter.ShieldTracker.Status;
import net.fabricmc.fabric.api.client.gametest.v1.context.ClientGameTestContext;
import net.fabricmc.fabric.api.client.gametest.v1.context.TestServerContext;
import net.minecraft.client.Minecraft;
import net.minecraft.client.player.RemotePlayer;
import net.minecraft.core.component.DataComponents;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.component.BlocksAttacks;

/**
 * In-game checks. Only one game client can run here, so the "opponent" is a player added on the
 * client side; its shield is disabled by playing the shield's real "disabled" sound at its position,
 * the same way a server's sound packet arrives.
 */
@SuppressWarnings("UnstableApiUsage")
final class ShieldHighlighterChecks {
	private static RemotePlayer opponent;

	private ShieldHighlighterChecks() {
	}

	static void run(ClientGameTestContext context, TestServerContext server) {
		server.runCommand("gamerule spawn_monsters false");
		server.runCommand("time set day");
		server.runCommand("gamerule advance_time false");
		server.runCommand("gamemode creative @a");
		server.runCommand("fill ~-4 ~ ~1 ~4 ~3 ~8 air");
		server.runCommand("fill ~-4 ~-1 ~1 ~4 ~-1 ~8 stone");
		server.runCommand("tp @a ~ ~ ~ 0 0");
		context.waitTicks(20);

		context.runOnClient(mc -> {
			opponent = new RemotePlayer(mc.level, new GameProfile(UUID.randomUUID(), "Opponent"));
			opponent.setId(-424242);
			opponent.setPos(mc.player.getX(), mc.player.getY(), mc.player.getZ() + 3.5);
			opponent.setYRot(180);
			opponent.setYHeadRot(180);
			opponent.yBodyRot = 180;
			opponent.setItemSlot(EquipmentSlot.MAINHAND, new ItemStack(Items.IRON_SWORD));
			mc.level.addEntity(opponent);
		});
		context.waitTicks(5);

		// 1. No shield: no highlight.
		check(context, Status.NONE, "no shield -> no highlight");

		// 2. Shield in off hand, in view: green.
		context.runOnClient(mc -> opponent.setItemSlot(EquipmentSlot.OFFHAND, new ItemStack(Items.SHIELD)));
		context.waitTicks(5);
		check(context, Status.READY, "shield held -> ready (green)");
		assertTrue(context.computeOnClient(mc -> ShieldTracker.outlineColor(opponent)) == ShieldTracker.OUTLINE_READY, "green outline when visible");
		context.takeScreenshot("shield-ready");

		// 3. Behind a wall: shield still tracked, but no outline through blocks.
		server.runCommand("fill ~-2 ~ ~2 ~2 ~2 ~2 stone");
		context.waitTicks(5);
		assertTrue(context.computeOnClient(mc -> ShieldTracker.outlineColor(opponent)) == 0, "no outline through walls");
		context.takeScreenshot("shield-behind-wall");
		server.runCommand("fill ~-2 ~ ~2 ~2 ~2 ~2 air");
		context.waitTicks(5);

		// 4. Someone else disables it: assumed axe time, 5 s = 100 ticks.
		disableSound(context);
		check(context, Status.DISABLED, "disable sound -> disabled (red)");
		assertTrue(context.computeOnClient(mc -> ShieldTracker.outlineColor(opponent)) == ShieldTracker.OUTLINE_DISABLED, "dark red outline");
		context.takeScreenshot("shield-disabled");
		context.waitTicks(95);
		check(context, Status.DISABLED, "still disabled after 95 ticks");
		context.waitTicks(10);
		check(context, Status.READY, "ready again after 5 seconds");

		// 5. We disable it with a weapon that disables for 2 s: exact timer (40 ticks).
		server.runCommand("item replace entity @a weapon.mainhand with iron_axe[weapon={disable_blocking_for_seconds:2}]");
		context.waitTicks(5);
		context.runOnClient(mc -> mc.gameMode.attack(mc.player, opponent));
		disableSound(context);
		check(context, Status.DISABLED, "own hit -> disabled");
		context.waitTicks(36);
		check(context, Status.DISABLED, "still disabled after 36 ticks");
		context.waitTicks(8);
		check(context, Status.READY, "ready again after our 2 seconds");

		// 6. Unrelated sounds don't count.
		context.runOnClient(mc -> mc.level.playSeededSound(null, opponent.getX(), opponent.getY(), opponent.getZ(),
				net.minecraft.sounds.SoundEvents.ANVIL_LAND, net.minecraft.sounds.SoundSource.PLAYERS, 1F, 1F, 0L));
		context.waitTick();
		check(context, Status.READY, "other sounds ignored");

		// 7. Ourselves: never highlighted.
		assertTrue(context.computeOnClient(mc -> ShieldTracker.status(mc.player)) == Status.NONE, "you are never highlighted");

		context.runOnClient(mc -> opponent.discard());
	}

	private static void disableSound(ClientGameTestContext context) {
		context.runOnClient(mc -> {
			BlocksAttacks shield = opponent.getOffhandItem().get(DataComponents.BLOCKS_ATTACKS);
			mc.level.playSeededSound(null, opponent.getX(), opponent.getY(), opponent.getZ(), shield.disableSound().orElseThrow(),
					net.minecraft.sounds.SoundSource.PLAYERS, 0.8F, 1F, 0L);
		});
		context.waitTick();
	}

	private static void check(ClientGameTestContext context, Status expected, String what) {
		Status actual = context.computeOnClient(mc -> ShieldTracker.status(opponent));
		assertTrue(actual == expected, what + " (got " + actual + ")");
	}

	static void assertTrue(boolean condition, String what) {
		if (!condition) {
			throw new AssertionError("FAILED: " + what);
		}
		System.out.println("[shieldhighlighter-test] PASS: " + what);
	}
}
