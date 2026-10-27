/* SPDX-License-Identifier: Apache-2.0 */
package miui.content.res;

/**
 * App-local stand-in for MIUI's miui.content.res.ThemeResources.
 *
 * getSystem() must never return null: ConfigFile and FancyIconResourceLoader
 * dereference it without a null check. It returns an empty system-theme object
 * so icon lookups simply miss and the app falls back to its own resources.
 */
public final class ThemeResources {
    /** Kept for source compatibility; no MIUI theme package exists on PixelOS. */
    public static final String THEME_MAGIC_PATH = "/data/system/theme";

    private static final ThemeResourcesSystem SYSTEM = new ThemeResourcesSystem();

    private ThemeResources() {
    }

    public static ThemeResourcesSystem getSystem() {
        return SYSTEM;
    }
}
