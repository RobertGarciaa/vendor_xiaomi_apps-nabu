/* SPDX-License-Identifier: Apache-2.0 */
package miui.util;

import android.content.Context;
import android.net.Uri;
import android.os.VibrationAttributes;
import android.os.Vibrator;

/**
 * App-local stand-in for MIUI's miui.util.HapticFeedbackUtil.
 *
 * nabu has a linear motor but PixelOS exposes no MIUI extended haptic effect
 * IDs. Every capability check reports false and every effect request is a
 * no-op, so the apps keep their own Android vibration code instead of claiming
 * MIUI haptics exist. The overload set matches every signature referenced by
 * the pinned Notes and Creation DEX files.
 */
public final class HapticFeedbackUtil {
    private final Vibrator vibrator;

    public HapticFeedbackUtil(Context context, boolean unused) {
        vibrator = context == null ? null
                : (Vibrator) context.getSystemService(Context.VIBRATOR_SERVICE);
    }

    public static boolean isSupportLinearMotorVibrate() {
        return false;
    }

    public static boolean isSupportLinearMotorVibrate(int effectId) {
        return false;
    }

    public boolean isSupportExtHapticFeedback(int effectId) {
        return false;
    }

    public boolean performExtHapticFeedback(int effectId) {
        return false;
    }

    public boolean performExtHapticFeedback(int effectId, double scale, String reason) {
        return false;
    }

    public boolean performExtHapticFeedback(int effectId, int strength) {
        return false;
    }

    public boolean performExtHapticFeedback(int effectId, int strength, boolean ignore) {
        return false;
    }

    public boolean performExtHapticFeedback(int effectId, boolean ignore) {
        return false;
    }

    public boolean performExtHapticFeedback(Uri effect) {
        return false;
    }

    public boolean performExtHapticFeedback(Uri effect, boolean ignore) {
        return false;
    }

    public boolean performExtHapticFeedback(VibrationAttributes attributes, int effectId) {
        return false;
    }

    public boolean performExtHapticFeedback(VibrationAttributes attributes, int effectId,
            boolean ignore) {
        return false;
    }

    public boolean performHapticFeedback(int effectId) {
        return false;
    }

    public boolean performHapticFeedback(int effectId, double scale, String reason) {
        return false;
    }

    public boolean performHapticFeedback(int effectId, boolean ignore) {
        return false;
    }

    public boolean performHapticFeedback(int effectId, boolean ignore, int strength) {
        return false;
    }

    public boolean performHapticFeedback(VibrationAttributes attributes, int effectId,
            double scale, String reason) {
        return false;
    }

    public boolean performHapticFeedback(VibrationAttributes attributes, int effectId,
            boolean ignore) {
        return false;
    }

    public boolean performHapticFeedback(VibrationAttributes attributes, int effectId,
            boolean ignore, int strength) {
        return false;
    }

    /** Existing callers rely on the platform vibrator, not MIUI effect IDs. */
    public void stop() {
        if (vibrator != null) {
            vibrator.cancel();
        }
    }

    public void release() {
        stop();
    }
}
