/* SPDX-License-Identifier: Apache-2.0 */
package com.xiaomi.account.openauth;

/**
 * App-local stand-in for Xiaomi's XiaomiOAuthResults.
 *
 * Only getCode() is read, and only after a successful OAuth future. Since the
 * shim never produces a result this object is never constructed by the app; a
 * null code states that no authorization code exists.
 */
public class XiaomiOAuthResults {
    private final String code;

    public XiaomiOAuthResults() {
        this(null);
    }

    public XiaomiOAuthResults(String code) {
        this.code = code;
    }

    public String getCode() {
        return code;
    }

    public String getAccessToken() {
        return null;
    }

    public String getState() {
        return null;
    }

    public boolean hasError() {
        return true;
    }
}
