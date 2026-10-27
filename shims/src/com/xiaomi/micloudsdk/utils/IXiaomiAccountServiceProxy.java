/* SPDX-License-Identifier: Apache-2.0 */
package com.xiaomi.micloudsdk.utils;

import android.accounts.Account;
import android.os.IBinder;

/**
 * App-local stand-in for Xiaomi's IXiaomiAccountServiceProxy.
 *
 * Returns the encrypted Xiaomi user id through the account service. That service
 * is not present, so the method reports null (unavailable) instead of returning
 * a raw or invented identifier.
 */
public final class IXiaomiAccountServiceProxy {
    private IXiaomiAccountServiceProxy() {
    }

    public static String getEncryptedUserId(IBinder service, Account account) {
        return null;
    }
}
