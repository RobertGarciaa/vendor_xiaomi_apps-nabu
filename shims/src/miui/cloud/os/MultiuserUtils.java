/* SPDX-License-Identifier: Apache-2.0 */
package miui.cloud.os;

/** App-local stand-in for MIUI's miui.cloud.os.MultiuserUtils. */
public final class MultiuserUtils {
    private MultiuserUtils() {
    }

    public static int get_USER_OWNER() {
        return 0;
    }

    public static int myUserId() {
        return android.os.Process.myUserHandle().getIdentifier();
    }
}
