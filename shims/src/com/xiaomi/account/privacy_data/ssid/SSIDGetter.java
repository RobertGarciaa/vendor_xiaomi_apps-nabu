/* SPDX-License-Identifier: Apache-2.0 */
package com.xiaomi.account.privacy_data.ssid;

/**
 * App-local stand-in for Xiaomi's privacy_data SSIDGetter.
 *
 * Returns null because the Xiaomi account SDK is absent and this port uploads
 * nothing. No device identifier is read, stored or invented.
 */
public class SSIDGetter {
    public SSIDGetter() {
    }

    public String get() {
        return null;
    }
}
