/* SPDX-License-Identifier: Apache-2.0 */
package miui.util;

import android.app.Application;
import android.app.ActivityManager;
import android.content.Context;
import android.content.pm.PackageInfo;
import android.content.pm.PackageManager;

/**
 * App-local stand-in for MIUI's miui.util.AppConstants.
 *
 * Android has no process-wide Application accessor, so the ported apps install
 * themselves here from Application.attachBaseContext/onCreate.
 */
public final class AppConstants {
    private static volatile Application application;

    private AppConstants() {
    }

    public static void setCurrentApplication(Application app) {
        application = app;
    }

    public static Application getCurrentApplication() {
        Application app = application;
        if (app == null) {
            throw new IllegalStateException(
                    "AppConstants.getCurrentApplication() before Application init");
        }
        return app;
    }

    public static int getSdkLevel(Context context, String packageName) {
        try {
            PackageInfo info = context.getPackageManager()
                    .getPackageInfo(packageName, 0);
            return info.applicationInfo.targetSdkVersion;
        } catch (PackageManager.NameNotFoundException e) {
            return 0;
        }
    }

    public static long getTotalMemory() {
        ActivityManager am = getCurrentApplication()
                .getSystemService(ActivityManager.class);
        ActivityManager.MemoryInfo info = new ActivityManager.MemoryInfo();
        am.getMemoryInfo(info);
        return info.totalMem;
    }
}
