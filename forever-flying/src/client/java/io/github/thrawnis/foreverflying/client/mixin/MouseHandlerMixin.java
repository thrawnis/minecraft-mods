package io.github.thrawnis.foreverflying.client.mixin;

import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

import io.github.thrawnis.foreverflying.client.ForeverFlyingClient;
import net.minecraft.client.MouseHandler;

@Mixin(MouseHandler.class)
public abstract class MouseHandlerMixin {
	// Reached only when scrolling in-game (no menu open). Holding the speed key while flying:
	// scroll changes fly speed instead of the hotbar slot.
	@Inject(method = "onScroll", cancellable = true, at = @At(value = "INVOKE",
			target = "Lnet/minecraft/client/ScrollWheelHandler;onMouseScroll(DD)Lorg/joml/Vector2i;"))
	private void foreverflying$scrollSpeed(long handle, double xoffset, double yoffset, CallbackInfo ci) {
		if (ForeverFlyingClient.onScroll(yoffset)) {
			ci.cancel();
		}
	}
}
