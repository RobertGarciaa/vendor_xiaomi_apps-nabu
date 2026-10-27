/* SPDX-License-Identifier: Apache-2.0 */
package miui.app.backup;

/**
 * App-local stand-in for MIUI's miui.app.backup.BackupMeta.
 *
 * NoteBackupAgent.onRestoreEnd(BackupMeta) receives this. MIUI metadata is not
 * produced by AOSP backup, so the object is an empty carrier. No restore result
 * is fabricated.
 */
public class BackupMeta {
    public BackupMeta() {
    }

    /** Empty metadata: nothing was recorded by a MIUI backup service. */
    public java.util.Map<String, String> getValues() {
        return java.util.Collections.emptyMap();
    }
}
