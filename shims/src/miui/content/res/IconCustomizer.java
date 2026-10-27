/* SPDX-License-Identifier: Apache-2.0 */
package miui.content.res;

import android.content.pm.PackageItemInfo;
import android.graphics.drawable.Drawable;

/**
 * App-local stand-in for MIUI's miui.content.res.IconCustomizer.
 *
 * MIUI overlays icons from a theme package. PixelOS ships no MIUI theme store,
 * so the helpers return null. Callers already null-check the result and fall
 * back to the platform icon; nothing is fabricated.
 */
public final class IconCustomizer {
    private IconCustomizer() {
    }

    public static String getAnimatingIconRelativePath(PackageItemInfo info,
            String packageName, String className) {
        return null;
    }

    public static String getFancyIconRelativePath(PackageItemInfo info,
            String packageName, String className) {
        return null;
    }

    public static String getMamlAdaptiveIconRelativePath(PackageItemInfo info,
            String packageName, String className) {
        return null;
    }

    public static boolean isModIconEnabledForPackageName(String packageName) {
        return false;
    }

    public static Drawable getIcon(PackageItemInfo info, String packageName,
            String className) {
        return null;
    }
}
