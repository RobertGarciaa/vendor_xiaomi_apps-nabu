/* SPDX-License-Identifier: Apache-2.0 */
package com.xiaomi.miai.api.common;

import com.google.gson.Gson;
import com.xiaomi.miai.api.Response;

/**
 * App-local stand-in for Xiaomi's com.xiaomi.miai.api.common.APIUtils.
 *
 * The app bundles its own Gson (207 classes inside its DEX files), so getGson()
 * returns a working instance of that same class rather than failing.
 *
 * Everything that needs the miai cloud service returns a failure Response or
 * null instead of fabricating a result. No AI feature is claimed to work.
 */
public final class APIUtils {
    private static final Gson GSON = new Gson();

    private APIUtils() {
    }

    public static Gson getGson() {
        return GSON;
    }

    public static String toJsonString(Object value) {
        return value == null ? null : GSON.toJson(value);
    }

    /** No reachable miai endpoint, so parsing a response cannot succeed. */
    public static Response getResponse(String json, Class<?> type) {
        android.util.Log.i("NabuApps", "Xiaomi miai is unavailable; ignoring response");
        return new Response();
    }

    /** No miai instruction payload exists. */
    public static Instruction readInstruction(String json) {
        return null;
    }

    public static Event buildEvent(EventPayload payload) {
        return new Event();
    }
}
