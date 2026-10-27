/* SPDX-License-Identifier: Apache-2.0 */
package miui.cloud.telephony;

/**
 * App-local stand-in for MIUI's miui.cloud.telephony.TelephonyManager.
 *
 * nabu is Wi-Fi only. A phone count of 0 states that truthfully and keeps the
 * SIM-related cloud sync settings disabled.
 */
public final class TelephonyManager {
    private static final TelephonyManager INSTANCE = new TelephonyManager();

    private TelephonyManager() {
    }

    public static TelephonyManager getDefault() {
        return INSTANCE;
    }

    public int getPhoneCount() {
        return 0;
    }
}
