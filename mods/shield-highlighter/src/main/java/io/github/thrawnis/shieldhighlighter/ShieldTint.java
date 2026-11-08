package io.github.thrawnis.shieldhighlighter;

/** Carries a shield tint from the moment an item is prepared for drawing to when it's drawn. */
public interface ShieldTint {
	int shieldhighlighter$getTint();

	void shieldhighlighter$setTint(int tint);

	/** Tint of the item currently being drawn (render thread only); 0 = none. */
	final class Current {
		public static int tint;

		private Current() {
		}
	}
}
