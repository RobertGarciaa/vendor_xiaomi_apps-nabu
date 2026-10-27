/* SPDX-License-Identifier: Apache-2.0 */
package com.xiaomi.account.privacy_data.line_1_number;

/**
 * App-local stand-in for Xiaomi's privacy_data Line1NumberGetter.
 *
 * Returns null because the Xiaomi account SDK is absent and this port uploads
 * nothing. No device identifier is read, stored or invented.
 */
public class Line1NumberGetter {
    public Line1NumberGetter() {
    }

    public String get() {
        return null;
    }
}
