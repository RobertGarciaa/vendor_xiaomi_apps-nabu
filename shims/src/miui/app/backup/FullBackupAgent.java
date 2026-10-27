/* SPDX-License-Identifier: Apache-2.0 */
package miui.app.backup;

import android.app.backup.BackupAgentHelper;
import android.net.Uri;

/**
 * App-local stand-in for MIUI's miui.app.backup.FullBackupAgent.
 *
 * NoteBackupAgent extends this class. MIUI's full-backup framework does not
 * exist on PixelOS, so the port replaces the manifest backup agent with AOSP's
 * mechanism instead of pretending MIUI backup works. The class still has to be
 * loadable, and addAttachedFile()/onRestoreEnd() must keep the exact signatures
 * NoteBackupAgent calls. onRestoreEnd returns 0, the AOSP success code.
 */
public class FullBackupAgent extends BackupAgentHelper {
    public FullBackupAgent() {
        super();
    }

    public void addAttachedFile(String path) {
        // MIUI-only attachment list; AOSP backup handles files through its own
        // full-backup include/exclude rules.
    }

    public void addAttachedFile(Uri uri, String path) {
        // See addAttachedFile(String).
    }

    public int onRestoreEnd(BackupMeta meta) {
        return 0;
    }
}
