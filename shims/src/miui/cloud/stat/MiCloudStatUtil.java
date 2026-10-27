/* SPDX-License-Identifier: Apache-2.0 */
package miui.cloud.stat;

import android.content.Context;

/**
 * App-local stand-in for MIUI's miui.cloud.stat.MiCloudStatUtil.
 *
 * Opening the Xiaomi cloud app is impossible on PixelOS because that app is not
 * shipped. The method therefore does nothing; the caller's surrounding UI is
 * what opens, and the ported settings screens hide the cloud entry separately.
 */
public final class MiCloudStatUtil {
    private MiCloudStatUtil() {
    }

    public static void startMiCloudMainActivity(Context context) {
        android.util.Log.i("NabuApps",
                "Xiaomi cloud app is not installed; ignoring cloud jump");
    }
}
