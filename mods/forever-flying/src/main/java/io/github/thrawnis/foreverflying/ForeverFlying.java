package io.github.thrawnis.foreverflying;

import java.util.Set;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.function.Predicate;

import net.fabricmc.api.ModInitializer;
import net.fabricmc.fabric.api.entity.event.v1.ServerLivingEntityEvents;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerTickEvents;
import net.fabricmc.fabric.api.networking.v1.PayloadTypeRegistry;
import net.fabricmc.fabric.api.networking.v1.ServerPlayConnectionEvents;
import net.fabricmc.fabric.api.networking.v1.ServerPlayNetworking;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.damagesource.DamageTypes;
import net.minecraft.world.entity.player.Player;

/**
 * Server side (also runs inside singleplayer worlds): lets every player whose game has
 * this mod fly in any game mode, pass through blocks when they ask to, and never suffocate.
 */
public class ForeverFlying implements ModInitializer {
	public static final String MOD_ID = "foreverflying";

	/** Players (on this server) who currently have pass-through-blocks turned on. */
	private static final Set<UUID> NOCLIP = ConcurrentHashMap.newKeySet();

	/** Client-side answer for "is pass-through on for this player?"; set by the client entrypoint. */
	public static Predicate<Player> clientNoclip = player -> false;

	@Override
	public void onInitialize() {
		PayloadTypeRegistry.clientboundPlay().register(Payloads.Hello.TYPE, Payloads.Hello.CODEC);
		PayloadTypeRegistry.serverboundPlay().register(Payloads.SetNoclip.TYPE, Payloads.SetNoclip.CODEC);

		ServerPlayNetworking.registerGlobalReceiver(Payloads.SetNoclip.TYPE, (payload, context) -> {
			UUID id = context.player().getUUID();
			if (payload.enabled()) {
				NOCLIP.add(id);
			} else {
				NOCLIP.remove(id);
			}
		});
		ServerPlayConnectionEvents.DISCONNECT.register((handler, server) -> NOCLIP.remove(handler.getPlayer().getUUID()));

		// Game mode changes switch flight off again, so keep re-enabling it.
		ServerTickEvents.END_SERVER_TICK.register(server -> {
			for (ServerPlayer player : server.getPlayerList().getPlayers()) {
				if (hasMod(player) && !player.getAbilities().mayfly) {
					player.getAbilities().mayfly = true;
					player.onUpdateAbilities();
				}
			}
		});

		// No suffocation. (Fall damage is already skipped by vanilla for players who may fly.)
		ServerLivingEntityEvents.ALLOW_DAMAGE.register((entity, source, amount) ->
				!(entity instanceof ServerPlayer player && source.is(DamageTypes.IN_WALL) && hasMod(player)));
	}

	/** True when this player's game has Forever Flying installed. */
	public static boolean hasMod(ServerPlayer player) {
		return ServerPlayNetworking.canSend(player, Payloads.Hello.TYPE);
	}

	/** Whether this player should pass through blocks right now (only while flying). */
	public static boolean isNoclip(Player player) {
		if (!player.getAbilities().flying) {
			return false;
		}
		if (player.level().isClientSide()) {
			return clientNoclip.test(player);
		}
		return NOCLIP.contains(player.getUUID());
	}
}
