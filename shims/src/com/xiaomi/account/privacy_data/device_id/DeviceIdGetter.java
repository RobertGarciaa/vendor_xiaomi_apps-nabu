/* SPDX-License-Identifier: Apache-2.0 */
package com.xiaomi.account.privacy_data.device_id;

/**
 * App-local stand-in for Xiaomi's privacy_data DeviceIdGetter.
 *
 * Returns null because the Xiaomi account SDK is absent and this port uploads
 * nothing. No device identifier is read, stored or invented.
 */
public class DeviceIdGetter {
    public DeviceIdGetter() {
    }

    public String get() {
        return null;
    }
}
