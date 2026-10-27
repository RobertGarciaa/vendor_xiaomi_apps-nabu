/* SPDX-License-Identifier: Apache-2.0 */
package miui.cloud.telephony;

/**
 * App-local stand-in for MIUI's miui.cloud.telephony.SubscriptionManager.
 *
 * nabu is a Wi-Fi-only tablet with no telephony stack. The default slot and
 * phone count are reported as 0/absent rather than inventing a SIM.
 */
public final class SubscriptionManager {
    private static final SubscriptionManager INSTANCE = new SubscriptionManager();

    private SubscriptionManager() {
    }

    public static SubscriptionManager getDefault() {
        return INSTANCE;
    }

    public int getDefaultSlotId() {
        return -1;
    }
}
