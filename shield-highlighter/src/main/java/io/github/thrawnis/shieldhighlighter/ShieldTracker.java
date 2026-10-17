package io.github.thrawnis.shieldhighlighter;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

import org.jspecify.annotations.Nullable;

import net.minecraft.client.Minecraft;
import net.minecraft.core.Holder;
import net.minecraft.core.component.DataComponents;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.util.ARGB;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.component.BlocksAttacks;
import net.minecraft.world.item.component.Weapon;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;

/**
 * Works out, on the client only, whether other players' shields are usable or disabled.
 *
 * The game only tells a shield's owner how long it's disabled. Everyone else hears the shield's
 * "disabled" sound at the owner's position, so that is what we listen for. The timer is exact when
 * we disabled it ourselves (we know our weapon); otherwise it assumes an axe (5 seconds).
 */
public final class ShieldTracker {
	public enum Status { NONE, READY, DISABLED }

	/** Outline colours (opaque RGB). */
	public static final int OUTLINE_READY = ARGB.opaque(0x00FF00);    // bright green
	public static final int OUTLINE_DISABLED = ARGB.opaque(0x8B0000); // dark red
	/** Colours multiplied onto the shield itself. */
	public static final int TINT_READY = 0xFF66FF66;
	public static final int TINT_DISABLED = 0xFFB02020;
	/** Full brightness, so the green shield stands out even in the dark. */
	public static final int FULL_BRIGHT = 0xF000F0;

	private static final float DEFAULT_DISABLE_SECONDS = 5.0F; // vanilla axes
	private static final double SOUND_MATCH_DISTANCE = 2.0;
	private static final int OWN_HIT_WINDOW_TICKS = 3;

	private static final Map<UUID, Long> disabledUntil = new HashMap<>();
	private static final Map<UUID, Long> ownHitTick = new HashMap<>();
	private static final Map<UUID, Float> ownHitSeconds = new HashMap<>();
	private static long now;

	private ShieldTracker() {
	}

	public static void tick(boolean inWorld) {
		if (!inWorld) {
			return;
		}
		now++;
		disabledUntil.values().removeIf(until -> until <= now);
	}

	public static void reset() {
		disabledUntil.clear();
		ownHitTick.clear();
		ownHitSeconds.clear();
	}

	/** We hit someone: remember how long our weapon would disable their shield. */
	public static void onLocalAttack(Entity target, ItemStack weaponItem) {
		Weapon weapon = weaponItem.get(DataComponents.WEAPON);
		ownHitTick.put(target.getUUID(), now);
		ownHitSeconds.put(target.getUUID(), weapon != null ? weapon.disableBlockingForSeconds() : 0.0F);
	}

	/** A sound played somewhere; if it's a shield being disabled, start that player's timer. */
	public static void onSound(double x, double y, double z, Holder<SoundEvent> sound) {
		Minecraft mc = Minecraft.getInstance();
		if (mc.level == null) {
			return;
		}
		Player best = null;
		BlocksAttacks bestShield = null;
		double bestDist = SOUND_MATCH_DISTANCE * SOUND_MATCH_DISTANCE;
		for (Player player : mc.level.players()) {
			if (player == mc.player) {
				continue;
			}
			BlocksAttacks shield = shieldOf(player);
			if (shield == null || shield.disableSound().isEmpty() || !sameSound(shield.disableSound().get(), sound)) {
				continue;
			}
			double dist = player.distanceToSqr(x, y, z);
			if (dist <= bestDist) {
				best = player;
				bestShield = shield;
				bestDist = dist;
			}
		}
		if (best == null) {
			return;
		}
		UUID id = best.getUUID();
		float seconds = DEFAULT_DISABLE_SECONDS;
		Long hit = ownHitTick.get(id);
		if (hit != null && now - hit <= OWN_HIT_WINDOW_TICKS && ownHitSeconds.getOrDefault(id, 0.0F) > 0.0F) {
			seconds = ownHitSeconds.get(id);
		}
		// Same rounding as the game uses.
		int ticks = Math.round(seconds * bestShield.disableCooldownScale() * 20.0F);
		if (ticks > 0) {
			disabledUntil.put(id, now + ticks);
		}
	}

	public static Status status(@Nullable Entity entity) {
		Minecraft mc = Minecraft.getInstance();
		if (!(entity instanceof Player player) || player == mc.player || player.isSpectator() || shieldOf(player) == null) {
			return Status.NONE;
		}
		return disabledUntil.containsKey(player.getUUID()) ? Status.DISABLED : Status.READY;
	}

	/** Outline colour for this entity, or 0 for none. Only when you can actually see them. */
	public static int outlineColor(Entity entity) {
		Status status = status(entity);
		if (status == Status.NONE || !visible(entity)) {
			return 0;
		}
		return status == Status.READY ? OUTLINE_READY : OUTLINE_DISABLED;
	}

	/** Tint for a shield held by this entity, or 0 for none. */
	public static int tint(@Nullable Entity owner) {
		return switch (status(owner)) {
			case READY -> TINT_READY;
			case DISABLED -> TINT_DISABLED;
			case NONE -> 0;
		};
	}

	private static @Nullable BlocksAttacks shieldOf(Player player) {
		BlocksAttacks main = player.getMainHandItem().get(DataComponents.BLOCKS_ATTACKS);
		return main != null ? main : player.getOffhandItem().get(DataComponents.BLOCKS_ATTACKS);
	}

	private static boolean sameSound(Holder<SoundEvent> a, Holder<SoundEvent> b) {
		return a.value().location().equals(b.value().location());
	}

	/** True if a straight line from your eyes reaches the entity's head, middle or feet without hitting blocks. */
	private static boolean visible(Entity entity) {
		Minecraft mc = Minecraft.getInstance();
		Entity viewer = mc.getCameraEntity() != null ? mc.getCameraEntity() : mc.player;
		Vec3 from = viewer.getEyePosition();
		Vec3 feet = entity.position().add(0, 0.1, 0);
		Vec3[] points = {entity.getEyePosition(), entity.getBoundingBox().getCenter(), feet};
		for (Vec3 to : points) {
			HitResult hit = mc.level.clip(new ClipContext(from, to, ClipContext.Block.VISUAL, ClipContext.Fluid.NONE, mc.player));
			if (hit.getType() == HitResult.Type.MISS) {
				return true;
			}
		}
		return false;
	}
}
