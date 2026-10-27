/* SPDX-License-Identifier: Apache-2.0 */
package miui.content.res;

/** App-local stand-in for MIUI's miui.content.res.ThemeNativeUtils. */
public final class ThemeNativeUtils {
    private ThemeNativeUtils() {
    }

    /** No MIUI theme context exists, so there is nothing to re-permission. */
    public static boolean updateFilePermissionWithThemeContext(String path) {
        return false;
    }
}
