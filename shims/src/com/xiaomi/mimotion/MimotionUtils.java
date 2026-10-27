/* SPDX-License-Identifier: Apache-2.0 */
package com.xiaomi.mimotion;

/**
 * App-local stand-in for Xiaomi's com.xiaomi.mimotion.MimotionUtils.
 *
 * MiMotion is a Xiaomi refresh-rate enhancer that lives in MIUI services.
 * PixelOS uses its own display stack, so the feature is reported disabled and
 * enabling is a no-op. It never claims to have changed the refresh rate.
 */
public final class MimotionUtils {
    private MimotionUtils() {
    }

    private static volatile boolean enabled;

    public static boolean isEnabled() {
        return enabled;
    }

    public static void setEnable(boolean value) {
        enabled = value;
    }

    public static boolean setPreferredRefreshRate(Object target, int rate) {
        return false;
    }
}
