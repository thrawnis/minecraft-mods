package io.github.thrawnis.shieldhighlighter.mixin;

import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Constant;
import org.spongepowered.asm.mixin.injection.ModifyConstant;
import org.spongepowered.asm.mixin.injection.ModifyVariable;

import io.github.thrawnis.shieldhighlighter.ShieldTint;
import io.github.thrawnis.shieldhighlighter.ShieldTracker;
import net.minecraft.client.renderer.special.ShieldSpecialRenderer;

@Mixin(ShieldSpecialRenderer.class)
public abstract class ShieldSpecialRendererMixin {
	// The shield is drawn with colour -1 (white = no tint); swap in green or red.
	@ModifyConstant(method = "submit", constant = @Constant(intValue = -1))
	private int shieldhighlighter$tint(int color) {
		return ShieldTint.Current.tint != 0 ? ShieldTint.Current.tint : color;
	}

	// A usable (green) shield is drawn at full brightness so it stands out.
	@ModifyVariable(method = "submit", at = @At("HEAD"), argsOnly = true, ordinal = 0)
	private int shieldhighlighter$bright(int lightCoords) {
		return ShieldTint.Current.tint == ShieldTracker.TINT_READY ? ShieldTracker.FULL_BRIGHT : lightCoords;
	}
}
