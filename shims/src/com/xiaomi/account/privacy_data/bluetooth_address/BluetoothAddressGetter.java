/* SPDX-License-Identifier: Apache-2.0 */
package com.xiaomi.account.privacy_data.bluetooth_address;

/**
 * App-local stand-in for Xiaomi's privacy_data BluetoothAddressGetter.
 *
 * Returns null because the Xiaomi account SDK is absent and this port uploads
 * nothing. No device identifier is read, stored or invented.
 */
public class BluetoothAddressGetter {
    public BluetoothAddressGetter() {
    }

    public String get() {
        return null;
    }
}
