/* SPDX-License-Identifier: Apache-2.0 */
package android.provider;
import android.content.ContentResolver;
/** App-local compatibility for the MAML boolean setting reader. */
public final class MiuiSettings {
    private MiuiSettings() {}
    public static final class System {
        private System() {}
        public static boolean getBoolean(ContentResolver resolver, String name, boolean fallback) {
            return Settings.System.getInt(resolver, name, fallback ? 1 : 0) != 0;
        }
    }
}
