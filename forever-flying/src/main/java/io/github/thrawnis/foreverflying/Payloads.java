package io.github.thrawnis.foreverflying;

import io.netty.buffer.ByteBuf;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.network.protocol.common.custom.CustomPacketPayload;
import net.minecraft.resources.Identifier;

public final class Payloads {
	private Payloads() {
	}

	/** Never actually sent: a client that can receive it has the mod installed. */
	public record Hello() implements CustomPacketPayload {
		public static final CustomPacketPayload.Type<Hello> TYPE =
				new CustomPacketPayload.Type<>(Identifier.fromNamespaceAndPath(ForeverFlying.MOD_ID, "hello"));
		public static final StreamCodec<ByteBuf, Hello> CODEC = StreamCodec.unit(new Hello());

		@Override
		public Type<Hello> type() {
			return TYPE;
		}
	}

	/** Client tells the server it turned pass-through-blocks on or off. */
	public record SetNoclip(boolean enabled) implements CustomPacketPayload {
		public static final CustomPacketPayload.Type<SetNoclip> TYPE =
				new CustomPacketPayload.Type<>(Identifier.fromNamespaceAndPath(ForeverFlying.MOD_ID, "set_noclip"));
		public static final StreamCodec<ByteBuf, SetNoclip> CODEC =
				ByteBufCodecs.BOOL.map(SetNoclip::new, SetNoclip::enabled);

		@Override
		public Type<SetNoclip> type() {
			return TYPE;
		}
	}
}
