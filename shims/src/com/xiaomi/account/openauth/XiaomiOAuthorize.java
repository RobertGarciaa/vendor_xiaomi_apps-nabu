/* SPDX-License-Identifier: Apache-2.0 */
package com.xiaomi.account.openauth;

import android.app.Activity;

/**
 * App-local stand-in for Xiaomi's XiaomiOAuthorize builder.
 *
 * The fluent setters exist only so the stock call chain links. startGetOAuthCode()
 * returns a future that always fails with XMAuthericationException, which is the
 * exception OAuthCapabilityImpl already catches. No login is faked and no token
 * is produced.
 */
public class XiaomiOAuthorize {
    public XiaomiOAuthorize() {
    }

    public XiaomiOAuthorize setAppId(long appId) {
        return this;
    }

    public XiaomiOAuthorize setDeviceID(String deviceId) {
        return this;
    }

    public XiaomiOAuthorize setNoMiui(boolean noMiui) {
        return this;
    }

    public XiaomiOAuthorize setPlatform(int platform) {
        return this;
    }

    public XiaomiOAuthorize setRedirectUrl(String redirectUrl) {
        return this;
    }

    public XiaomiOAuthorize setScope(int[] scope) {
        return this;
    }

    public XiaomiOAuthorize setSkipConfirm(boolean skipConfirm) {
        return this;
    }

    public XiaomiOAuthorize setState(String state) {
        return this;
    }

    public XiaomiOAuthFuture<XiaomiOAuthResults> startGetOAuthCode(Activity activity) {
        return () -> {
            throw new XMAuthericationException(
                    "Xiaomi account service is not available on this ROM");
        };
    }
}
