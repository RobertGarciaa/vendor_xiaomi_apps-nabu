/* SPDX-License-Identifier: Apache-2.0 */
package miui.cloud.sync;

import android.content.Context;

/**
 * App-local stand-in for MIUI's miui.cloud.sync.SyncInfoProvider interface.
 *
 * Sync statistics only exist when the Xiaomi cloud service is installed.
 * Callers cast the result of a provider lookup and null-check before use, so an
 * absent provider simply reports nothing.
 */
public interface SyncInfoProvider {
    int getSyncedCount(Context context);

    int getUnsyncedCount(Context context);

    int getWifiOnlyUnsyncedCount(Context context);

    int getUnSyncedSecretCount(Context context);
}
