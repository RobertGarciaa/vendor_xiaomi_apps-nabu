/* SPDX-License-Identifier: Apache-2.0 */
package com.xiaomi.account.openauth;

/**
 * App-local stand-in for Xiaomi's XMAuthericationException.
 *
 * OAuthCapabilityImpl catches this specific type, so the shim must throw it
 * rather than a generic RuntimeException. Authentication genuinely cannot be
 * performed without the Xiaomi account service.
 */
public class XMAuthericationException extends Exception {
    private static final long serialVersionUID = 1L;

    public XMAuthericationException() {
        super();
    }

    public XMAuthericationException(String message) {
        super(message);
    }

    public XMAuthericationException(String message, Throwable cause) {
        super(message, cause);
    }

    public XMAuthericationException(Throwable cause) {
        super(cause);
    }
}
