/* SPDX-License-Identifier: Apache-2.0 */
package miui.util;

import java.util.Collections;
import java.util.Map;
import org.xmlpull.v1.XmlPullParser;

/**
 * App-local stand-in for MIUI's miui.util.FeatureParser.
 *
 * The stock implementation reads /system/etc/device_features/<device>.xml. The
 * port carries the pinned nabu device_features file as an app asset, so device
 * capability answers still come from the real Pad 5 data instead of guesses.
 */
public final class FeatureParser {
    private static final Map<String, Boolean> VALUES = new java.util.HashMap<>();
    private static boolean loaded;

    private FeatureParser() {
    }

    public static synchronized boolean getBoolean(String key, boolean fallback) {
        ensureLoaded();
        Boolean value = VALUES.get(key);
        return value != null ? value : fallback;
    }

    public static int[] getIntArray(String key) {
        return null;
    }

    private static void ensureLoaded() {
        if (loaded) {
            return;
        }
        loaded = true;
        try (java.io.InputStream in =
                     miui.util.AppConstants.getCurrentApplication()
                             .getAssets().open("nabu_features.xml")) {
            XmlPullParser parser = android.util.Xml.newPullParser();
            parser.setInput(in, "UTF-8");
            int event = parser.getEventType();
            while (event != XmlPullParser.END_DOCUMENT) {
                if (event == XmlPullParser.START_TAG && "bool".equals(parser.getName())) {
                    String name = parser.getAttributeValue(null, "name");
                    String text = parser.nextText();
                    if (name != null) {
                        VALUES.put(name, Boolean.parseBoolean(text.trim()));
                    }
                }
                event = parser.next();
            }
        } catch (Exception e) {
            android.util.Log.w("NabuApps", "Cannot read packaged device features", e);
        }
    }

    static Map<String, Boolean> snapshot() {
        ensureLoaded();
        return Collections.unmodifiableMap(VALUES);
    }
}
