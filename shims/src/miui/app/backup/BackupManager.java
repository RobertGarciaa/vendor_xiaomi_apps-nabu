/* SPDX-License-Identifier: Apache-2.0 */
package miui.app.backup;

import android.content.Context;

/**
 * App-local stand-in for MIUI's miui.app.backup.BackupManager.
 *
 * MIUI's local backup service does not exist on PixelOS. The returned manager
 * only records the "please kill me" flag locally; it never claims a backup ran.
 */
public final class BackupManager {
    private static volatile boolean needBeKilled;

    private BackupManager() {
    }

    public static BackupManager getBackupManager(Context context) {
        return new BackupManager();
    }

    public void setIsNeedBeKilled(boolean value) {
        needBeKilled = value;
    }

    public boolean isNeedBeKilled() {
        return needBeKilled;
    }
}
