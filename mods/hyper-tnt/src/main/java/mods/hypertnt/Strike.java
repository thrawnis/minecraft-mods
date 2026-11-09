package mods.hypertnt;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.Iterator;
import java.util.List;
import java.util.Set;

import net.minecraft.core.BlockPos;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.item.PrimedTnt;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.phys.Vec3;

/**
 * An orbital-strike "nuke": 2,500 lit TNT drop from the sky in rings around the target,
 * from the centre outward, over about 5 seconds. Each drop point gets several TNT a moment
 * apart, so later ones fall into the hole the first one made and dig a deep crater.
 */
public final class Strike {
	public static final int TOTAL_TNT = 2500;
	public static final int RING_SPACING = 3;    // blocks between rings
	public static final int RINGS = 16;          // outer ring radius = 48 blocks
	public static final int CENTRE_TNT = 12;
	public static final int LAYERS = 4;          // TNT per drop point, arriving one after another
	public static final int LAYER_GAP = 8;       // ticks between them
	public static final int SPAWN_TICKS = 76;    // rings start over ~4 s; the last layers land ~1.5 s later
	public static final int DROP_HEIGHT = 40;    // blocks above the ground they fall from
	public static final int FUSE = 60;           // long enough to land before exploding
	private static final int FORCE_RADIUS_CHUNKS = 4;

	private static final List<Strike> ACTIVE = new ArrayList<>();

	/** Total TNT dropped by all strikes since the game started (used by the tests). */
	public static int droppedTotal;

	private final ServerLevel level;
	private final BlockPos centre;
	private final int[] ringCounts;
	private final Set<ChunkPos> forced = new HashSet<>();
	private int age;

	private final double[] ringOffsets = new double[RINGS + 1];

	private Strike(ServerLevel level, BlockPos centre) {
		this.level = level;
		this.centre = centre;
		this.ringCounts = ringCounts();
		for (int k = 0; k <= RINGS; k++) ringOffsets[k] = level.getRandom().nextDouble() * Math.PI * 2;
	}

	/** How many TNT each ring gets (ring 0 is the centre), adding up to exactly TOTAL_TNT; multiples of LAYERS. */
	static int[] ringCounts() {
		int[] counts = new int[RINGS + 1];
		counts[0] = CENTRE_TNT;
		double circumference = 0;
		for (int r = 1; r <= RINGS; r++) circumference += 2 * Math.PI * r * RING_SPACING;
		int points = (TOTAL_TNT - CENTRE_TNT) / LAYERS;
		int sum = CENTRE_TNT;
		for (int r = 1; r <= RINGS; r++) {
			counts[r] = (int) Math.round(2 * Math.PI * r * RING_SPACING / circumference * points) * LAYERS;
			sum += counts[r];
		}
		counts[RINGS] += TOTAL_TNT - sum;
		return counts;
	}

	/** Starts a strike on the Hyper TNT at pos. Returns false if there's no Hyper TNT there any more. */
	public static boolean start(ServerLevel level, BlockPos pos) {
		if (!level.getBlockState(pos).is(HyperTnt.HYPER_TNT_BLOCK)) {
			return false;
		}
		level.setBlock(pos, Blocks.AIR.defaultBlockState(), 3);
		Strike s = new Strike(level, pos);
		s.forceChunks(true);
		ACTIVE.add(s);
		level.playSound(null, pos, SoundEvents.WARDEN_SONIC_CHARGE, SoundSource.BLOCKS, 8F, 0.5F);
		return true;
	}

	public static void tickAll(MinecraftServer server) {
		for (Iterator<Strike> it = ACTIVE.iterator(); it.hasNext(); ) {
			Strike s = it.next();
			if (!s.tick()) {
				s.forceChunks(false);
				it.remove();
			}
		}
	}

	public static int activeCount() {
		return ACTIVE.size();
	}

	/** Returns false when finished. */
	private boolean tick() {
		// layer l of ring k is dropped at tick k * SPAWN_TICKS / RINGS + l * LAYER_GAP
		for (int k = 0; k <= RINGS; k++) {
			for (int l = 0; l < LAYERS; l++) {
				if (k * SPAWN_TICKS / RINGS + l * LAYER_GAP == age) dropRing(k, l);
			}
		}
		age++;
		return age < SPAWN_TICKS + LAYERS * LAYER_GAP + FUSE + 60;
	}

	/** Drops one layer of ring k: one TNT on each of the ring's drop points. */
	private void dropRing(int k, int layer) {
		int n = ringCounts[k] / LAYERS;
		double radius = k * RING_SPACING;
		double offset = ringOffsets[k];
		for (int i = 0; i < n; i++) {
			double a = offset + i * Math.PI * 2 / n;
			double r = k == 0 ? 1.0 : radius;
			double x = centre.getX() + 0.5 + Math.cos(a) * r;
			double z = centre.getZ() + 0.5 + Math.sin(a) * r;
			int ground = level.getHeight(Heightmap.Types.MOTION_BLOCKING, (int) Math.floor(x), (int) Math.floor(z));
			double y = Math.min(ground + DROP_HEIGHT, level.getMaxY() - 2);
			PrimedTnt tnt = new PrimedTnt(level, x, y, z, null);
			tnt.setDeltaMovement(Vec3.ZERO);
			tnt.setFuse(FUSE + level.getRandom().nextInt(10));
			tnt.addTag(HyperTnt.STRIKE_TAG);
			level.addFreshEntity(tnt);
			droppedTotal++;
		}
		if (layer == 0 && k % 4 == 0) {
			level.playSound(null, centre, SoundEvents.GENERIC_EXPLODE.value(), SoundSource.BLOCKS, 6F, 0.6F);
		}
	}

	/** Keep the strike area loaded so the TNT keeps falling and exploding even if nobody is near. */
	private void forceChunks(boolean on) {
		ChunkPos c = ChunkPos.containing(centre);
		if (on) {
			for (int dx = -FORCE_RADIUS_CHUNKS; dx <= FORCE_RADIUS_CHUNKS; dx++) {
				for (int dz = -FORCE_RADIUS_CHUNKS; dz <= FORCE_RADIUS_CHUNKS; dz++) {
					ChunkPos p = new ChunkPos(c.x() + dx, c.z() + dz);
					if (!level.getForceLoadedChunks().contains(p.pack())) {
						level.setChunkForced(p.x(), p.z(), true);
						forced.add(p);
					}
				}
			}
		} else {
			for (ChunkPos p : forced) level.setChunkForced(p.x(), p.z(), false);
			forced.clear();
		}
	}
}
