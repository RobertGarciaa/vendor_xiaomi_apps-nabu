/* SPDX-License-Identifier: Apache-2.0 */
package miui.securityspace;

import android.content.Context;
import android.content.pm.PackageManager;

/**
 * App-local stand-in for MIUI's miui.securityspace.CrossUserUtils.
 *
 * Only real Android permission state is reported; MIUI-specific cross-user
 * grants are not invented.
 */
public final class CrossUserUtils {
    private CrossUserUtils() {
    }

    public static int getCurrentUserId() {
        return android.app.ActivityManager.getCurrentUser();
    }

    public static boolean checkUidPermission(Context context, String permission) {
        return context != null
                && context.checkSelfPermission(permission)
                        == PackageManager.PERMISSION_GRANTED;
    }
}
