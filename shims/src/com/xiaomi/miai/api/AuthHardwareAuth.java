/* SPDX-License-Identifier: Apache-2.0 */
package com.xiaomi.miai.api;

/**
 * App-local stand-ins for Xiaomi's hardware-auth value types.
 *
 * Used by the miai authentication handshake. No miai service or hardware token
 * backend exists on PixelOS, so the carriers are empty. No token is invented.
 */
public final class AuthHardwareAuth {
    private AuthHardwareAuth() {
    }

    /** Server nonce for a hardware-auth handshake. */
    public static class NonceResponse {
        public NonceResponse() {
        }

        public String getNonce() {
            return null;
        }

        public String getNonceCert() {
            return null;
        }
    }

    /** Hardware token issued after a successful handshake. */
    public static class HardwareTokenResponse {
        public HardwareTokenResponse() {
        }

        public String getToken() {
            return null;
        }

        public long getExpiredInMillis() {
            return 0L;
        }
    }
}
