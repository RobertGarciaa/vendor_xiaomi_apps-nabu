/* SPDX-License-Identifier: Apache-2.0 */
package com.xiaomi.settingsdk.backup.data;

/**
 * App-local stand-in for Xiaomi's com.xiaomi.settingsdk.backup.data.SettingItem.
 *
 * Only exists so DataPackage can carry typed values. The MIUI cloud backup
 * service is disabled in the manifest, so nothing serializes these on device.
 */
public class SettingItem {
    private final String value;

    public SettingItem(String value) {
        this.value = value;
    }

    public Object getValue() {
        return value;
    }

    @Override
    public String toString() {
        return value == null ? "" : value;
    }
}
