/* SPDX-License-Identifier: Apache-2.0 */
package miui.cloud.os;

/** App-local stand-in for MIUI's miui.cloud.os.SystemProperties. */
public final class SystemProperties {
    private SystemProperties() {
    }

    public static String get(String key) {
        return android.os.SystemProperties.get(key);
    }

    public static String get(String key, String fallback) {
        return android.os.SystemProperties.get(key, fallback);
    }

    public static int getInt(String key, int fallback) {
        return android.os.SystemProperties.getInt(key, fallback);
    }

    public static long getLong(String key, long fallback) {
        return android.os.SystemProperties.getLong(key, fallback);
    }

    public static boolean getBoolean(String key, boolean fallback) {
        return android.os.SystemProperties.getBoolean(key, fallback);
    }
}
