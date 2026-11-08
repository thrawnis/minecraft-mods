package io.github.thrawnis.hypertnt;

import java.util.List;

import net.fabricmc.api.ModInitializer;
import net.fabricmc.fabric.api.creativetab.v1.CreativeModeTabEvents;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerTickEvents;
import net.minecraft.core.Registry;
import net.minecraft.core.component.DataComponents;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.CreativeModeTabs;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.component.ItemLore;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.material.MapColor;
import net.minecraft.ChatFormatting;

public class HyperTnt implements ModInitializer {
	public static final String MOD_ID = "hypertnt";
	/** Tag on the TNT a strike drops, so their explosions don't drop items. */
	public static final String STRIKE_TAG = "hypertnt_strike";

	public static Block HYPER_TNT_BLOCK;
	public static Item HYPER_TNT_ITEM;
	public static Item DETONATOR;

	@Override
	public void onInitialize() {
		ResourceKey<Block> blockKey = ResourceKey.create(Registries.BLOCK, id("hyper_tnt"));
		// Only the Detonator sets it off: not flammable, not redstone, and blast-proof like obsidian.
		HYPER_TNT_BLOCK = Blocks.register(blockKey, Block::new, BlockBehaviour.Properties.of()
				.mapColor(MapColor.COLOR_PURPLE).strength(2.0F, 1200.0F).sound(SoundType.GRASS));
		HYPER_TNT_ITEM = Registry.register(BuiltInRegistries.ITEM, id("hyper_tnt"),
				new BlockItem(HYPER_TNT_BLOCK, new Item.Properties().setId(ResourceKey.create(Registries.ITEM, id("hyper_tnt")))
						.useBlockDescriptionPrefix()
						.component(DataComponents.LORE, new ItemLore(List.of(
								Component.literal("As powerful as 2,500 TNT").withStyle(ChatFormatting.GOLD),
								Component.literal("Only a Detonator can set it off").withStyle(ChatFormatting.GRAY))))));
		DETONATOR = Registry.register(BuiltInRegistries.ITEM, id("detonator"),
				new DetonatorItem(new Item.Properties().setId(ResourceKey.create(Registries.ITEM, id("detonator"))).stacksTo(1)
						.component(DataComponents.LORE, new ItemLore(List.of(
								Component.literal("Right-click Hyper TNT: link / unlink").withStyle(ChatFormatting.GRAY),
								Component.literal("Right-click the air: detonate all linked").withStyle(ChatFormatting.RED))))));

		CreativeModeTabEvents.modifyOutputEvent(CreativeModeTabs.REDSTONE_BLOCKS).register(out -> {
			out.accept(HYPER_TNT_ITEM);
			out.accept(DETONATOR);
		});
		CreativeModeTabEvents.modifyOutputEvent(CreativeModeTabs.COMBAT).register(out -> {
			out.accept(HYPER_TNT_ITEM);
			out.accept(DETONATOR);
		});

		ServerTickEvents.END_SERVER_TICK.register(Strike::tickAll);
	}

	public static Identifier id(String path) {
		return Identifier.fromNamespaceAndPath(MOD_ID, path);
	}
}
