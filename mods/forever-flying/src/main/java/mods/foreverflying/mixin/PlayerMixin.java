package io.github.thrawnis.foreverflying.mixin;

import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

import io.github.thrawnis.foreverflying.ForeverFlying;
import net.minecraft.world.entity.player.Player;

@Mixin(Player.class)
public abstract class PlayerMixin {
	// Player.tick() resets noPhysics to isSpectator() every tick; turn it back on while passing through blocks.
	@Inject(method = "tick", at = @At(value = "FIELD", target = "Lnet/minecraft/world/entity/player/Player;noPhysics:Z", shift = At.Shift.AFTER))
	private void foreverflying$noclip(CallbackInfo ci) {
		Player self = (Player) (Object) this;
		if (ForeverFlying.isNoclip(self)) {
			self.noPhysics = true;
		}
	}
}
