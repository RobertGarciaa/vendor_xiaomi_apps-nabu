/* SPDX-License-Identifier: Apache-2.0 */
package miui.os;

/**
 * App-local stand-in for MIUI's miui.os.Build.
 *
 * The stock class ships in miui-framework.jar, which is not present on PixelOS.
 * This copy only implements the fields and methods the ported apps reference.
 *
 * IS_TABLET is derived from the real system property, never hard-coded. The
 * phone-targeted renoir port forced it to false to disable tablet layouts;
 * nabu is a tablet (ro.build.characteristics=tablet) so the pad UI must stay on.
 */
public final class Build {
    private Build() {
    }

    public static final String DEVICE = isNabu() ? "nabu" : android.os.Build.DEVICE;
    public static final String TAGS = android.os.Build.TAGS;

    /** ro.build.characteristics contains "tablet" on nabu. */
    public static final boolean IS_TABLET = isTablet();

    /** This port serves a global build; keep MIUI's global branches enabled. */
    public static final boolean IS_GLOBAL_BUILD = true;
    public static final boolean IS_INTERNATIONAL_BUILD = true;

    /** Release-channel flags. The ROM is a user build, so these are stable. */
    public static final boolean IS_STABLE_VERSION = true;
    public static final boolean IS_DEVELOPMENT_VERSION = false;
    public static final boolean IS_ALPHA_BUILD = false;

    /**
     * MIUI region code used by cloud/telephony branches. Derived from the real
     * locale region, not from a baked-in MIUI ROM country.
     */
    public static String getRegion() {
        String region = android.os.SystemProperties.get("ro.miui.region", "");
        if (!region.isEmpty()) {
            return region;
        }
        String country = java.util.Locale.getDefault().getCountry();
        return country == null ? "" : country;
    }

    private static boolean isTablet() {
        String characteristics = android.os.SystemProperties.get(
                "ro.build.characteristics", "");
        return characteristics.contains("tablet");
    }

    private static boolean isNabu() {
        return "nabu".equals(android.os.Build.DEVICE);
    }
}
