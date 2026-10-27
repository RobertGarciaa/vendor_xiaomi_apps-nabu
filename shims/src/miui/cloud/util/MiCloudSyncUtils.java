/* SPDX-License-Identifier: Apache-2.0 */
package miui.cloud.util;

import android.accounts.Account;
import android.content.ContentResolver;
import android.content.Context;
import java.util.HashMap;

/**
 * App-local stand-ins for MIUI's miui.cloud.util helpers.
 *
 * These track Xiaomi cloud sync bookkeeping. No cloud service exists on PixelOS,
 * so nothing is recorded, no sync is started, and the reported state is empty.
 * In particular setMiCloudSync does not claim success.
 */
public final class MiCloudSyncUtils {
    private MiCloudSyncUtils() {
    }

    public static boolean getAutoSyncForSim(ContentResolver resolver, int slotId,
            Account account, String authority) {
        return false;
    }

    public static boolean needActivate(String packageName) {
        return false;
    }

    public static void setAutoSyncForSim(ContentResolver resolver, int slotId,
            Account account, String authority, boolean enabled) {
        android.util.Log.i("NabuApps",
                "Xiaomi cloud sync is unavailable; ignoring auto-sync request");
    }
}
