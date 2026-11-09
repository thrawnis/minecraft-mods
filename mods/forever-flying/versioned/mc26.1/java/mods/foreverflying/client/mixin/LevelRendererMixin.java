package io.github.thrawnis.foreverflying.client.mixin;

import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.ModifyArg;

import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.LevelRenderer;

@Mixin(LevelRenderer.class)
public abstract class LevelRendererMixin {
	// Render the world around you from inside blocks the same way spectator mode does.
	@ModifyArg(method = "update", at = @At(value = "INVOKE",
			target = "Lnet/minecraft/client/renderer/LevelRenderer;cullTerrain(Lnet/minecraft/client/Camera;Lnet/minecraft/client/renderer/culling/Frustum;Z)V"),
			index = 2)
	private boolean foreverflying$insideBlocks(boolean spectator) {
		return spectator || Minecraft.getInstance().player.noPhysics;
	}
}
