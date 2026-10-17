package io.github.thrawnis.shieldhighlighter.mixin;

import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

import io.github.thrawnis.shieldhighlighter.ShieldTint;
import net.minecraft.client.renderer.item.ItemStackRenderState;

@Mixin(ItemStackRenderState.class)
public abstract class ItemStackRenderStateMixin implements ShieldTint {
	@Unique
	private int shieldhighlighter$tint;

	@Override
	public int shieldhighlighter$getTint() {
		return this.shieldhighlighter$tint;
	}

	@Override
	public void shieldhighlighter$setTint(int tint) {
		this.shieldhighlighter$tint = tint;
	}

	@Inject(method = "clear", at = @At("HEAD"))
	private void shieldhighlighter$clear(CallbackInfo ci) {
		this.shieldhighlighter$tint = 0;
	}

	@Inject(method = "submit", at = @At("HEAD"))
	private void shieldhighlighter$beginSubmit(CallbackInfo ci) {
		ShieldTint.Current.tint = this.shieldhighlighter$tint;
	}

	@Inject(method = "submit", at = @At("RETURN"))
	private void shieldhighlighter$endSubmit(CallbackInfo ci) {
		ShieldTint.Current.tint = 0;
	}
}
