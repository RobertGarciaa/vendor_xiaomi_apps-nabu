/* SPDX-License-Identifier: Apache-2.0 */
package com.xiaomi.settingsdk.backup;

/**
 * App-local stand-in for Xiaomi's com.xiaomi.settingsdk.backup.ICloudBackup.
 *
 * NoteSettingsBackupService returns this type from getBackupImpl(). The port
 * disables the MIUI cloud backup service in the manifest, so this interface
 * exists only to satisfy the verifier; it is never invoked.
 */
public interface ICloudBackup {
}
