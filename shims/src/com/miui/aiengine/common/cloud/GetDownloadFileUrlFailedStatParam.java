/* SPDX-License-Identifier: Apache-2.0 */
package com.miui.aiengine.common.cloud;

/**
 * App-local stand-in for MIUI's aiengine cloud statistics parameter.
 *
 * Creation builds this object when a cloud AI download fails. There is no
 * aiengine cloud service on PixelOS, so the object only carries the fields for
 * local logging; nothing is uploaded.
 */
public final class GetDownloadFileUrlFailedStatParam {
    private final String url;
    private final int code;
    private final String message;
    private final String extra;

    private GetDownloadFileUrlFailedStatParam(String url, int code, String message,
            String extra) {
        this.url = url;
        this.code = code;
        this.message = message;
        this.extra = extra;
    }

    public static GetDownloadFileUrlFailedStatParam createGetDownloadFileUrlFailedStatParam(
            String url, int code, String message, String extra) {
        return new GetDownloadFileUrlFailedStatParam(url, code, message, extra);
    }

    public String getUrl() {
        return url;
    }

    public int getCode() {
        return code;
    }

    public String getMessage() {
        return message;
    }

    public String getExtra() {
        return extra;
    }

    @Override
    public String toString() {
        return "GetDownloadFileUrlFailedStatParam{url='" + url + "', code=" + code + "}";
    }
}
