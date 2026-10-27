/* SPDX-License-Identifier: Apache-2.0 */
package com.xiaomi.account.privacy_data.mobile_data_enable;

/**
 * App-local stand-in for Xiaomi's privacy_data MobileDataEnableGetter.
 *
 * Returns null because the Xiaomi account SDK is absent and this port uploads
 * nothing. No device identifier is read, stored or invented.
 */
public class MobileDataEnableGetter {
    public MobileDataEnableGetter() {
    }

    public String get() {
        return null;
    }
}
