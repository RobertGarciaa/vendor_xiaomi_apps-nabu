/* SPDX-License-Identifier: Apache-2.0 */
package com.xiaomi.micloudsdk.sync.utils;

import android.content.Context;

/**
 * App-local stand-in for Xiaomi's SyncContentUtils.
 *
 * Tracks paused cloud sync authorities. With no Xiaomi cloud service the pause
 * state is irrelevant: nothing is paused, nothing is resumed and no sync result
 * is recorded. Returning "not paused" keeps local app behaviour unchanged.
 */
public final class SyncContentUtils {
    private SyncContentUtils() {
    }

    public static boolean isPauseExceptAuthority(Context context, String authority) {
        return false;
    }

    public static long loadResumeTime(Context context, String authority) {
        return 0L;
    }

    public static void recordSyncResult(Context context, String authority, int result) {
    }

    public static void deletePauseExceptAuthority(Context context) {
    }

    public static void insertPauseExceptAuthority(Context context, String authority) {
    }

    public static void savePauseTime(Context context, String authority, long time) {
    }
}
