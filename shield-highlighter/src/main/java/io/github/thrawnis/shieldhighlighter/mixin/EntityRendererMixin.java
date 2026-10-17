package io.github.thrawnis.shieldhighlighter.mixin;

import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

import io.github.thrawnis.shieldhighlighter.ShieldTracker;
import net.minecraft.client.renderer.entity.EntityRenderer;
import net.minecraft.client.renderer.entity.state.EntityRenderState;
import net.minecraft.world.entity.Entity;

@Mixin(EntityRenderer.class)
public abstract class EntityRendererMixin {
	// Green / dark red outline around opponents holding a shield (uses the game's Glowing outline).
	@Inject(method = "extractRenderState", at = @At("TAIL"))
	private void shieldhighlighter$outline(Entity entity, EntityRenderState state, float partialTicks, CallbackInfo ci) {
		int color = ShieldTracker.outlineColor(entity);
		if (color != 0) {
			state.outlineColor = color;
		}
	}
}
