/* SPDX-License-Identifier: Apache-2.0 */
package com.xiaomi.account.privacy_data.miui_device_id;

/**
 * App-local stand-in for Xiaomi's privacy_data MiuiDeviceIdGetter.
 *
 * Returns null because the Xiaomi account SDK is absent and this port uploads
 * nothing. No device identifier is read, stored or invented.
 */
public class MiuiDeviceIdGetter {
    public MiuiDeviceIdGetter() {
    }

    public String get() {
        return null;
    }
}
