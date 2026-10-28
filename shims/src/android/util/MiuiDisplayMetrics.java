/* SPDX-License-Identifier: Apache-2.0 */
package android.util;
/** Real framework density, used by the app's bundled MAML resource manager. */
public final class MiuiDisplayMetrics {
    private MiuiDisplayMetrics() {}
    public static final int DENSITY_DEVICE =
            android.content.res.Resources.getSystem().getDisplayMetrics().densityDpi;
}
