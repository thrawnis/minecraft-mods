package io.github.thrawnis.shieldhighlighter;

import net.fabricmc.api.ClientModInitializer;
import net.fabricmc.fabric.api.client.event.lifecycle.v1.ClientTickEvents;
import net.fabricmc.fabric.api.client.networking.v1.ClientPlayConnectionEvents;

public class ShieldHighlighter implements ClientModInitializer {
	@Override
	public void onInitializeClient() {
		ClientTickEvents.END_CLIENT_TICK.register(client -> ShieldTracker.tick(client.level != null));
		ClientPlayConnectionEvents.DISCONNECT.register((handler, client) -> ShieldTracker.reset());
	}
}
