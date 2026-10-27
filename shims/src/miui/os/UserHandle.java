/* SPDX-License-Identifier: Apache-2.0 */
package miui.os;

/** App-local stand-in for MIUI's miui.os.UserHandle. */
public final class UserHandle {
    private UserHandle() {
    }

    public static int myUserId() {
        return android.os.Process.myUserHandle().getIdentifier();
    }
}
