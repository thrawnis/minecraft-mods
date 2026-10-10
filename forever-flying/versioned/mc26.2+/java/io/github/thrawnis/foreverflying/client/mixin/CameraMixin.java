package io.github.thrawnis.foreverflying.client.mixin;

import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;

import com.llamalad7.mixinextras.injector.ModifyExpressionValue;

import net.minecraft.client.Camera;
import net.minecraft.client.Minecraft;
import net.minecraft.client.player.LocalPlayer;

@Mixin(Camera.class)
public abstract class CameraMixin {
	// Render the world around you from inside blocks the same way spectator mode does.
	@ModifyExpressionValue(method = "extractRenderState", at = @At(value = "INVOKE",
			target = "Lnet/minecraft/client/player/LocalPlayer;isSpectator()Z"))
	private boolean foreverflying$insideBlocks(boolean spectator) {
		LocalPlayer player = Minecraft.getInstance().player;
		return spectator || player.noPhysics;
	}
}
