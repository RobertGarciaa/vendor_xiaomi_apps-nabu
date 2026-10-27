/* SPDX-License-Identifier: Apache-2.0 */
package com.xiaomi.account.openauth;

/**
 * App-local stand-in for Xiaomi's XiaomiOAuthFuture.
 *
 * Only getResult() is referenced. The shim implementation always throws because
 * no OAuth request can ever start without the Xiaomi account service.
 */
public interface XiaomiOAuthFuture<V> {
    V getResult() throws java.io.IOException, XMAuthericationException,
            java.util.concurrent.ExecutionException,
            java.util.concurrent.TimeoutException;
}
