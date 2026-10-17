package io.github.thrawnis.shieldhighlighter.mixin;

import org.jspecify.annotations.Nullable;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

import io.github.thrawnis.shieldhighlighter.ShieldTracker;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.core.Holder;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.Entity;

@Mixin(ClientLevel.class)
public abstract class ClientLevelMixin {
	// Sounds from the server arrive here; a shield's "disabled" sound starts that player's timer.
	@Inject(method = "playSeededSound(Lnet/minecraft/world/entity/Entity;DDDLnet/minecraft/core/Holder;Lnet/minecraft/sounds/SoundSource;FFJ)V", at = @At("HEAD"))
	private void shieldhighlighter$onSound(@Nullable Entity except, double x, double y, double z, Holder<SoundEvent> sound,
			SoundSource source, float volume, float pitch, long seed, CallbackInfo ci) {
		ShieldTracker.onSound(x, y, z, sound);
	}
}
