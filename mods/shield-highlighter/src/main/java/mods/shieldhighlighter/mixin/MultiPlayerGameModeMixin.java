package io.github.thrawnis.shieldhighlighter.mixin;

import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

import io.github.thrawnis.shieldhighlighter.ShieldTracker;
import net.minecraft.client.multiplayer.MultiPlayerGameMode;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.player.Player;

@Mixin(MultiPlayerGameMode.class)
public abstract class MultiPlayerGameModeMixin {
	// When you hit someone, remember your weapon so a shield you disable gets an exact timer.
	@Inject(method = "attack", at = @At("HEAD"))
	private void shieldhighlighter$onAttack(Player player, Entity target, CallbackInfo ci) {
		ShieldTracker.onLocalAttack(target, player.getMainHandItem());
	}
}
