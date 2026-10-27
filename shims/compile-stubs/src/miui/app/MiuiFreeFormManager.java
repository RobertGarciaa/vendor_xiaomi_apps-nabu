/* SPDX-License-Identifier: Apache-2.0
 *
 * Build-time-only declarations for classes that live inside the ported APK.
 *
 * These files are NEVER shipped. They exist so the shim sources can be compiled
 * and checked on the host: javac must see the app-owned types that the MIUI
 * interface signatures mention. At runtime the APK's own copies are used, so a
 * duplicate would be a packaging error caught by verify-apps.py.
 */
package miui.app;

/** Build-time stub. The shipped class comes from the ported Notes APK. */
public class MiuiFreeFormManager {
    /** Build-time stub. The shipped class comes from the ported Notes APK. */
    public static class MiuiFreeFormStackInfo {
    }
}
