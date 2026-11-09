package mods.hypertnt;

import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.component.DataComponents;
import net.minecraft.core.registries.Registries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.Tag;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.component.CustomData;
import net.minecraft.world.item.context.UseOnContext;
import net.minecraft.world.level.Level;

/** Links to Hyper TNT blocks (right-click them) and sets them all off (right-click the air). */
public class DetonatorItem extends Item {
	public DetonatorItem(Item.Properties properties) {
		super(properties);
	}

	@Override
	public InteractionResult useOn(UseOnContext context) {
		Level level = context.getLevel();
		BlockPos pos = context.getClickedPos();
		if (!level.getBlockState(pos).is(HyperTnt.HYPER_TNT_BLOCK)) {
			return InteractionResult.PASS;
		}
		if (level.isClientSide() || context.getPlayer() == null) {
			return InteractionResult.SUCCESS;
		}
		ItemStack stack = context.getItemInHand();
		String dim = level.dimension().identifier().toString();
		boolean[] linked = {false};
		int[] count = {0};
		CustomData.update(DataComponents.CUSTOM_DATA, stack, tag -> {
			ListTag links = tag.getListOrEmpty("links");
			ListTag kept = new ListTag();
			boolean found = false;
			for (Tag t : links) {
				CompoundTag c = (CompoundTag) t;
				if (c.getStringOr("dim", "").equals(dim) && c.getIntOr("x", 0) == pos.getX() && c.getIntOr("y", 0) == pos.getY() && c.getIntOr("z", 0) == pos.getZ()) {
					found = true;
				} else {
					kept.add(c);
				}
			}
			if (!found) {
				CompoundTag c = new CompoundTag();
				c.putString("dim", dim);
				c.putInt("x", pos.getX());
				c.putInt("y", pos.getY());
				c.putInt("z", pos.getZ());
				kept.add(c);
			}
			linked[0] = !found;
			count[0] = kept.size();
			tag.put("links", kept);
		});
		Player player = context.getPlayer();
		player.sendOverlayMessage(Component.literal((linked[0] ? "Linked" : "Unlinked") + " Hyper TNT: " + count[0] + " charge"
				+ (count[0] == 1 ? "" : "s") + " linked").withStyle(linked[0] ? ChatFormatting.GREEN : ChatFormatting.YELLOW));
		level.playSound(null, pos, SoundEvents.NOTE_BLOCK_PLING.value(), SoundSource.PLAYERS, 1F, linked[0] ? 2F : 1F);
		return InteractionResult.SUCCESS;
	}

	@Override
	public InteractionResult use(Level level, Player player, InteractionHand hand) {
		ItemStack stack = player.getItemInHand(hand);
		if (level.isClientSide() || !(player instanceof ServerPlayer sp)) {
			return InteractionResult.SUCCESS;
		}
		CustomData data = stack.getOrDefault(DataComponents.CUSTOM_DATA, CustomData.EMPTY);
		ListTag links = data.copyTag().getListOrEmpty("links");
		if (links.isEmpty()) {
			player.sendOverlayMessage(Component.literal("No Hyper TNT linked. Right-click a Hyper TNT block first.").withStyle(ChatFormatting.YELLOW));
			return InteractionResult.FAIL;
		}
		int fired = 0;
		for (Tag t : links) {
			CompoundTag c = (CompoundTag) t;
			Identifier dimId = Identifier.tryParse(c.getStringOr("dim", ""));
			ServerLevel target = dimId == null ? null : sp.level().getServer().getLevel(ResourceKey.create(Registries.DIMENSION, dimId));
			if (target == null) continue;
			BlockPos pos = new BlockPos(c.getIntOr("x", 0), c.getIntOr("y", 0), c.getIntOr("z", 0));
			if (Strike.start(target, pos)) fired++;
		}
		CustomData.update(DataComponents.CUSTOM_DATA, stack, tag -> tag.remove("links"));
		player.sendOverlayMessage(Component.literal(fired == 0 ? "No linked Hyper TNT is left." : "Detonating " + fired + " Hyper TNT!")
				.withStyle(fired == 0 ? ChatFormatting.YELLOW : ChatFormatting.RED));
		level.playSound(null, player.blockPosition(), SoundEvents.LEVER_CLICK, SoundSource.PLAYERS, 1F, 1.5F);
		return fired == 0 ? InteractionResult.FAIL : InteractionResult.SUCCESS;
	}
}
