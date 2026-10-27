/* SPDX-License-Identifier: Apache-2.0 */
package com.xiaomi.settingsdk.backup.data;

import java.util.LinkedHashMap;
import java.util.Map;

/**
 * App-local stand-in for Xiaomi's com.xiaomi.settingsdk.backup.data.DataPackage.
 *
 * A plain key/value carrier. The MIUI cloud backup service is disabled in the
 * manifest, so this never leaves the process and no backup is reported.
 */
public class DataPackage {
    private final Map<String, SettingItem> values = new LinkedHashMap<>();

    public DataPackage() {
    }

    public void addKeyValue(String key, String value) {
        if (key != null) {
            values.put(key, new KeyStringSettingItem(value));
        }
    }

    public SettingItem get(String key) {
        return values.get(key);
    }

    public Map<String, SettingItem> asMap() {
        return java.util.Collections.unmodifiableMap(values);
    }
}
