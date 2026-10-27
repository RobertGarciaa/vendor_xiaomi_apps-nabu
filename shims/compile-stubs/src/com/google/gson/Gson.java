/* SPDX-License-Identifier: Apache-2.0
 *
 * Build-time-only declaration. Never shipped: the ported APK bundles the real
 * Gson (207 classes in its own DEX files), and the APK copy wins at runtime.
 */
package com.google.gson;

/** Build-time stub for the Gson that the ported app already bundles. */
public class Gson {
    public Gson() {
    }

    public String toJson(Object src) {
        throw new UnsupportedOperationException("host stub");
    }

    public <T> T fromJson(String json, Class<T> type) {
        throw new UnsupportedOperationException("host stub");
    }
}
