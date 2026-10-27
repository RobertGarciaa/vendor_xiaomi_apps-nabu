/* SPDX-License-Identifier: Apache-2.0 */
package com.xiaomi.miai.api;

/**
 * App-local stand-in for Xiaomi's com.xiaomi.miai.api.Status.
 *
 * miai is Xiaomi's cloud AI service. PixelOS does not ship the service or the
 * account binding it needs, so every response carries a non-zero failure code.
 * Failure is reported explicitly instead of being disguised as success.
 */
public class Status {
    /** Non-zero so callers take their existing failure path. */
    public static final int CODE_UNAVAILABLE = -1;
    public static final int CODE_OK = 200;

    private final int code;
    private final String message;
    private final String traceId;

    public Status() {
        this(CODE_UNAVAILABLE, "Xiaomi miai service is not available on this ROM", null);
    }

    public Status(int code, String message, String traceId) {
        this.code = code;
        this.message = message;
        this.traceId = traceId;
    }

    public int getCode() {
        return code;
    }

    public String getMessageOrEmpty() {
        return message == null ? "" : message;
    }

    public String getTraceIdOrEmpty() {
        return traceId == null ? "" : traceId;
    }
}
