/* SPDX-License-Identifier: Apache-2.0 */
package com.xiaomi.settingsdk.backup;

/**
 * App-local stand-in for Xiaomi's com.xiaomi.settingsdk.backup.CloudBackupServiceBase.
 *
 * NoteSettingsBackupService extends this class. The port disables that service
 * in the manifest because no Xiaomi cloud backup service exists on PixelOS.
 */
public class CloudBackupServiceBase {
    public CloudBackupServiceBase() {
    }

    public ICloudBackup getBackupImpl() {
        return null;
    }
}
