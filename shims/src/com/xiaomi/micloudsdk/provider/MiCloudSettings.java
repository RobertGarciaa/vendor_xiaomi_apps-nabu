/* SPDX-License-Identifier: Apache-2.0 */
package com.xiaomi.micloudsdk.provider;

import android.content.ContentResolver;

/**
 * App-local stand-in for Xiaomi's com.xiaomi.micloudsdk.provider.MiCloudSettings.
 *
 * MIUI stores cloud switches in its own settings provider. PixelOS has no such
 * provider, so reads return the caller's default and writes are ignored. The
 * cloud settings UI is hidden by the port, so a write should never happen; if it
 * does, silently storing it locally would misrepresent the system state.
 */
public final class MiCloudSettings {
    private MiCloudSettings() {
    }

    public static int getInt(ContentResolver resolver, String key, int fallback) {
        return fallback;
    }

    public static boolean putInt(ContentResolver resolver, String key, int value) {
        android.util.Log.i("NabuApps",
                "MIUI cloud settings provider is absent; ignoring write of " + key);
        return false;
    }
}
