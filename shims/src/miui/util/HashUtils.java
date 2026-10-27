/* SPDX-License-Identifier: Apache-2.0 */
package miui.util;

/** App-local stand-in for MIUI's miui.util.HashUtils. */
public final class HashUtils {
    private HashUtils() {
    }

    /** MIUI's helper returns a hex digest of the given algorithm. */
    public static String getHash(String algorithm, String content) {
        if (algorithm == null || content == null) {
            return null;
        }
        try {
            java.security.MessageDigest digest =
                    java.security.MessageDigest.getInstance(algorithm);
            byte[] bytes = digest.digest(content.getBytes(java.nio.charset.StandardCharsets.UTF_8));
            StringBuilder sb = new StringBuilder(bytes.length * 2);
            for (byte b : bytes) {
                sb.append(Character.forDigit((b >> 4) & 0xf, 16));
                sb.append(Character.forDigit(b & 0xf, 16));
            }
            return sb.toString();
        } catch (java.security.NoSuchAlgorithmException e) {
            android.util.Log.w("NabuApps", "Unsupported hash algorithm: " + algorithm);
            return null;
        }
    }
}
