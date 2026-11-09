package io.github.thrawnis.shieldhighlighter.mixin;

import org.jspecify.annotations.Nullable;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

import io.github.thrawnis.shieldhighlighter.ShieldTint;
import io.github.thrawnis.shieldhighlighter.ShieldTracker;
import net.minecraft.client.renderer.item.ItemModelResolver;
import net.minecraft.client.renderer.item.ItemStackRenderState;
import net.minecraft.world.entity.ItemOwner;
import net.minecraft.world.item.ItemDisplayContext;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;

@Mixin(ItemModelResolver.class)
public abstract class ItemModelResolverMixin {
	// Remember who is holding the item, as a tint, for when it gets drawn.
	@Inject(method = "appendItemLayers", at = @At("RETURN"))
	private void shieldhighlighter$rememberOwner(ItemStackRenderState output, ItemStack item, ItemDisplayContext displayContext,
			@Nullable Level level, @Nullable ItemOwner owner, int seed, CallbackInfo ci) {
		((ShieldTint) output).shieldhighlighter$setTint(owner != null ? ShieldTracker.tint(owner.asLivingEntity()) : 0);
	}
}
