/* SPDX-License-Identifier: Apache-2.0 */
package miui.cloud.sync;

import android.content.Context;
import android.database.Cursor;
import android.net.Uri;

/**
 * App-local stand-in for MIUI's miui.cloud.sync.SyncInfoProviderBase.
 *
 * The ported Notes app has three classes (tx/a, tx/b, tx/c) that extend this
 * and call queryCount()/isDebug(). Without the Xiaomi cloud service there is no
 * sync database, so queryCount returns -1 (unknown) instead of a fake zero and
 * isDebug reports false. Callers treat every count as informational only.
 */
public class SyncInfoProviderBase {
    public SyncInfoProviderBase() {
    }

    /** Unknown count. A real zero would claim the user has no unsynced data. */
    public static final int UNKNOWN_COUNT = -1;

    public boolean isDebug() {
        return false;
    }

    public int queryCount(Context context, Uri uri, String selection,
            String[] selectionArgs) {
        if (context == null || uri == null) {
            return UNKNOWN_COUNT;
        }
        try (Cursor cursor = context.getContentResolver()
                .query(uri, null, selection, selectionArgs, null)) {
            if (cursor == null) {
                return UNKNOWN_COUNT;
            }
            return cursor.getCount();
        } catch (SecurityException | IllegalArgumentException e) {
            android.util.Log.i("NabuApps",
                    "No readable sync provider for " + uri + "; reporting unknown");
            return UNKNOWN_COUNT;
        }
    }
}
