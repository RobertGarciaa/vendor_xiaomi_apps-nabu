/* SPDX-License-Identifier: Apache-2.0 */
package miui.cloud.util;

import android.accounts.Account;
import android.content.Context;
import java.util.HashMap;

/**
 * App-local stand-in for MIUI's miui.cloud.util.SyncStateChangedHelper.
 *
 * Reports "nothing synced" state and refuses to pretend a sync switch was
 * applied. The Notes UI hides the cloud section when the account is absent.
 */
public final class SyncStateChangedHelper {
    private SyncStateChangedHelper() {
    }

    public static void clearAllSyncChangedLog(Context context) {
    }

    public static HashMap<String, Object> getCurrentSyncSettingState(Context context) {
        return new HashMap<>();
    }

    public static void setMiCloudSync(Context context, Account account, String authority,
            String packageName, boolean enabled) {
        android.util.Log.i("NabuApps",
                "Xiaomi cloud sync is unavailable; ignoring sync switch");
    }

    public static void setSyncChanged(Context context, String authority,
            String packageName, boolean changed) {
    }
}
