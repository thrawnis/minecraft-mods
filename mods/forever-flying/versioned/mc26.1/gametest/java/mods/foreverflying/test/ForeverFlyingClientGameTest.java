package io.github.thrawnis.foreverflying.test;

import net.fabricmc.fabric.api.client.gametest.v1.FabricClientGameTest;
import net.fabricmc.fabric.api.client.gametest.v1.context.ClientGameTestContext;
import net.fabricmc.fabric.api.client.gametest.v1.context.TestDedicatedServerContext;
import net.fabricmc.fabric.api.client.gametest.v1.context.TestServerConnection;
import net.fabricmc.fabric.api.client.gametest.v1.context.TestSingleplayerContext;

/** End-to-end checks in a singleplayer world and on a dedicated server. */
@SuppressWarnings("UnstableApiUsage")
public class ForeverFlyingClientGameTest implements FabricClientGameTest {
	@Override
	public void runTest(ClientGameTestContext context) {
		try (TestSingleplayerContext sp = context.worldBuilder().create()) {
			sp.getClientLevel().waitForChunksRender();
			ForeverFlyingChecks.check(context, sp.getServer(), "singleplayer");
		}

		try (TestDedicatedServerContext server = context.worldBuilder().createServer()) {
			try (TestServerConnection connection = server.connect()) {
				connection.getClientLevel().waitForChunksRender();
				ForeverFlyingChecks.check(context, server, "server");
			}
		}
	}
}
