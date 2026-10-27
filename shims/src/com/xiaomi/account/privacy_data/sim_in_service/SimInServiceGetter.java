/* SPDX-License-Identifier: Apache-2.0 */
package com.xiaomi.account.privacy_data.sim_in_service;

/**
 * App-local stand-in for Xiaomi's privacy_data SimInServiceGetter.
 *
 * Returns null because the Xiaomi account SDK is absent and this port uploads
 * nothing. No device identifier is read, stored or invented.
 */
public class SimInServiceGetter {
    public SimInServiceGetter() {
    }

    public String get() {
        return null;
    }
}
