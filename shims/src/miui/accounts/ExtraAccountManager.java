/* SPDX-License-Identifier: Apache-2.0 */
package miui.accounts;

import android.accounts.Account;
import android.content.Context;

/**
 * App-local stand-in for MIUI's miui.accounts.ExtraAccountManager.
 *
 * PixelOS does not ship the Xiaomi account service. Returning null is the
 * truthful answer and every caller in the ported apps null-checks it before use.
 * No account is fabricated and no offline success is reported.
 */
public final class ExtraAccountManager {
    private ExtraAccountManager() {
    }

    public static Account getXiaomiAccount(Context context) {
        return null;
    }
}
