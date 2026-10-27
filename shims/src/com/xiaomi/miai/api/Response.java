/* SPDX-License-Identifier: Apache-2.0 */
package com.xiaomi.miai.api;

import com.xiaomi.common.Optional;

/**
 * App-local stand-in for Xiaomi's com.xiaomi.miai.api.Response.
 *
 * Always carries the unavailable status and empty data. The app checks
 * getStatus().getCode() before reading data, so this is the truthful failure
 * path rather than a fake success.
 */
public class Response {
    private final Status status;

    public Response() {
        this(new Status());
    }

    public Response(Status status) {
        this.status = status == null ? new Status() : status;
    }

    public Status getStatus() {
        return status;
    }

    public Optional<Object> getData() {
        return Optional.empty();
    }
}
