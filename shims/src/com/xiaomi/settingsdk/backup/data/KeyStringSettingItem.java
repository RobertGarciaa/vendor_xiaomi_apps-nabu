/* SPDX-License-Identifier: Apache-2.0 */
package com.xiaomi.settingsdk.backup.data;

/**
 * App-local stand-in for Xiaomi's KeyStringSettingItem.
 *
 * NoteSettingsBackupService extends this class. The service is disabled in the
 * manifest, so the object only needs a consistent value contract.
 */
public class KeyStringSettingItem extends SettingItem {
    public KeyStringSettingItem(String value) {
        super(value);
    }
}
