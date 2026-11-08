package io.github.thrawnis.foreverflying.client;

import io.github.thrawnis.foreverflying.ForeverFlying;
import io.github.thrawnis.foreverflying.Payloads;
import net.fabricmc.api.ClientModInitializer;
import net.fabricmc.fabric.api.client.event.lifecycle.v1.ClientTickEvents;
import net.fabricmc.fabric.api.client.keymapping.v1.KeyMappingHelper;
import net.fabricmc.fabric.api.client.networking.v1.ClientPlayConnectionEvents;
import net.fabricmc.fabric.api.client.networking.v1.ClientPlayNetworking;
import com.mojang.blaze3d.platform.InputConstants;

import net.minecraft.client.KeyMapping;
import net.minecraft.client.Minecraft;
import net.minecraft.client.player.LocalPlayer;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;

public class ForeverFlyingClient implements ClientModInitializer {
	private static final float BASE_SPEED = 0.05F;  // vanilla creative flying speed
	private static final int MIN_STEP = 1;          // 0.25x
	private static final int MAX_STEP = 16;         // 4x (same top speed as spectator mode)

	private static final KeyMapping.Category CATEGORY =
			KeyMapping.Category.register(Identifier.fromNamespaceAndPath(ForeverFlying.MOD_ID, "main"));
	public static KeyMapping noclipKey;
	public static KeyMapping speedModifierKey;

	private static boolean noclip;
	private static int speedStep = 4;  // speed = speedStep * 0.25x

	@Override
	public void onInitializeClient() {
		noclipKey = KeyMappingHelper.registerKeyMapping(
				new KeyMapping("key.foreverflying.noclip", InputConstants.KEY_V, CATEGORY));
		speedModifierKey = KeyMappingHelper.registerKeyMapping(
				new KeyMapping("key.foreverflying.speed_modifier", InputConstants.KEY_LALT, CATEGORY));

		// Registering a receiver tells the server this client has the mod.
		ClientPlayNetworking.registerGlobalReceiver(Payloads.Hello.TYPE, (payload, context) -> {
		});
		ForeverFlying.clientNoclip = player -> noclip && player == Minecraft.getInstance().player;

		ClientPlayConnectionEvents.JOIN.register((handler, sender, client) -> noclip = false);
		ClientTickEvents.END_CLIENT_TICK.register(ForeverFlyingClient::tick);
	}

	/** True when the server (or singleplayer world) also runs Forever Flying. */
	private static boolean serverHasMod() {
		return ClientPlayNetworking.canSend(Payloads.SetNoclip.TYPE);
	}

	private static void tick(Minecraft client) {
		LocalPlayer player = client.player;
		if (player == null) {
			return;
		}
		while (noclipKey.consumeClick()) {
			if (!serverHasMod()) {
				player.sendOverlayMessage(Component.translatable("message.foreverflying.not_on_server"));
				continue;
			}
			noclip = !noclip;
			ClientPlayNetworking.send(new Payloads.SetNoclip(noclip));
			player.sendOverlayMessage(Component.translatable(
					noclip ? "message.foreverflying.noclip_on" : "message.foreverflying.noclip_off"));
		}
		// The server resends abilities (e.g. on game mode change), so keep our speed applied.
		if (serverHasMod() && !player.isSpectator()) {
			player.getAbilities().setFlyingSpeed(BASE_SPEED * speedStep / 4F);
		}
	}

	/** Called on mouse scroll; returns true if the scroll was used to change fly speed. */
	public static boolean onScroll(double amount) {
		LocalPlayer player = Minecraft.getInstance().player;
		if (player == null || amount == 0 || !speedModifierKey.isDown() || !player.getAbilities().flying
				|| player.isSpectator() || !serverHasMod()) {
			return false;
		}
		speedStep = Math.clamp(speedStep + (amount > 0 ? 1 : -1), MIN_STEP, MAX_STEP);
		player.sendOverlayMessage(Component.translatable("message.foreverflying.speed", String.valueOf(speedStep / 4F)));
		return true;
	}
}
