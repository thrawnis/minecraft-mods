package mods.hypertnt.mixin;

import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

import mods.hypertnt.HyperTnt;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.level.Explosion;
import net.minecraft.world.level.block.Block;

@Mixin(Block.class)
public abstract class BlockMixin {
	// Blocks destroyed by a Hyper TNT strike drop nothing (thousands of item drops would lag the game).
	@Inject(method = "dropFromExplosion", at = @At("HEAD"), cancellable = true)
	private void hypertnt$noDrops(Explosion explosion, CallbackInfoReturnable<Boolean> cir) {
		Entity source = explosion.getDirectSourceEntity();
		if (source != null && source.entityTags().contains(HyperTnt.STRIKE_TAG)) {
			cir.setReturnValue(false);
		}
	}
}
