/* SPDX-License-Identifier: Apache-2.0 */
package miui.cloud.util;

import android.content.Context;
import java.util.HashMap;

/** App-local stand-in for MIUI's miui.cloud.util.SyncAlertRecordHelper. */
public final class SyncAlertRecordHelper {
    private SyncAlertRecordHelper() {
    }

    public static void recordTime(Context context, String key) {
        recordTime(context, key, System.currentTimeMillis());
    }

    public static void recordTime(Context context, String key, long time) {
        // No cloud sync alerts exist, so no record is kept.
    }

    public static boolean within(long windowMs, Context context, String key) {
        return false;
    }
}
