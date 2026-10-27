/* SPDX-License-Identifier: Apache-2.0 */
package miui.app;

import android.os.IBinder;

/**
 * App-local stand-in for MIUI's miui.app.IMiuiFreeFormManager and its Stub.
 *
 * The ported Notes app ships its own MiuiFreeFormManager, IFreeformCallback and
 * MiuiFreeFormStackInfo, but not this AIDL interface. MIUI free-form windows are
 * a MIUI framework feature PixelOS does not implement, so every query reports
 * "nothing here" and every mutation is ignored. No floating window is ever
 * reported as running or pinned.
 *
 * The nested MiuiFreeFormStackInfo reference resolves to the app's own class at
 * runtime; nothing is shipped twice.
 */
public interface IMiuiFreeFormManager extends android.os.IInterface {

    java.util.List<MiuiFreeFormManager.MiuiFreeFormStackInfo>
            getAllFreeFormStackInfosOnDisplay(int displayId);

    java.util.List<MiuiFreeFormManager.MiuiFreeFormStackInfo>
            getAllPinedFreeFormStackInfosOnDisplay(int displayId);

    MiuiFreeFormManager.MiuiFreeFormStackInfo getFreeFormStackInfoByActivity(IBinder token);

    MiuiFreeFormManager.MiuiFreeFormStackInfo getFreeFormStackInfoByStackId(int stackId);

    MiuiFreeFormManager.MiuiFreeFormStackInfo getFreeFormStackInfoByWindow(IBinder token);

    int getMaxMiuiFreeFormStackCountForFlashBack(String packageName, boolean check);

    void hidePinFloatingWindow(int stackId);

    boolean isSupportPin();

    void registerFreeformCallback(IFreeformCallback callback);

    boolean unPinFloatingWindow(android.graphics.Rect rect, int stackId, float x, float y,
            boolean animate);

    void unregisterFreeformCallback(IFreeformCallback callback);

    void updatePinFloatingWindowPos(android.graphics.Rect rect, int stackId);

    /** Minimal Stub so MiuiFreeFormManager$1 can call asInterface(). */
    abstract class Stub extends android.os.Binder implements IMiuiFreeFormManager {
        private static final Stub NO_OP = new Stub() {
        };

        public static IMiuiFreeFormManager asInterface(IBinder binder) {
            // There is no MIUI free-form service on PixelOS.
            return NO_OP;
        }

        @Override
        public IBinder asBinder() {
            return this;
        }

        @Override
        public java.util.List<MiuiFreeFormManager.MiuiFreeFormStackInfo>
                getAllFreeFormStackInfosOnDisplay(int displayId) {
            return java.util.Collections.emptyList();
        }

        @Override
        public java.util.List<MiuiFreeFormManager.MiuiFreeFormStackInfo>
                getAllPinedFreeFormStackInfosOnDisplay(int displayId) {
            return java.util.Collections.emptyList();
        }

        @Override
        public MiuiFreeFormManager.MiuiFreeFormStackInfo getFreeFormStackInfoByActivity(
                IBinder token) {
            return null;
        }

        @Override
        public MiuiFreeFormManager.MiuiFreeFormStackInfo getFreeFormStackInfoByStackId(
                int stackId) {
            return null;
        }

        @Override
        public MiuiFreeFormManager.MiuiFreeFormStackInfo getFreeFormStackInfoByWindow(
                IBinder token) {
            return null;
        }

        @Override
        public int getMaxMiuiFreeFormStackCountForFlashBack(String packageName, boolean check) {
            return 0;
        }

        @Override
        public void hidePinFloatingWindow(int stackId) {
        }

        @Override
        public boolean isSupportPin() {
            return false;
        }

        @Override
        public void registerFreeformCallback(IFreeformCallback callback) {
        }

        @Override
        public boolean unPinFloatingWindow(android.graphics.Rect rect, int stackId, float x,
                float y, boolean animate) {
            return false;
        }

        @Override
        public void unregisterFreeformCallback(IFreeformCallback callback) {
        }

        @Override
        public void updatePinFloatingWindowPos(android.graphics.Rect rect, int stackId) {
        }
    }
}
