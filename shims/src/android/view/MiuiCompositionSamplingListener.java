/* SPDX-License-Identifier: Apache-2.0 */
package android.view;
import android.graphics.GraphicBuffer;
import android.util.Log;
import java.util.concurrent.Executor;
/**
 * Type compatibility for the bundled MIUI blur SDK. PixelOS has no MIUI
 * GraphicBuffer sampler. Never call MIUI native entry points or fabricate a
 * sampling callback. The application's existing non-sampled rendering remains.
 */
public abstract class MiuiCompositionSamplingListener {
    protected MiuiCompositionSamplingListener(Executor executor) {}
    public abstract void onSampleCollected(GraphicBuffer buffer);
    public static void register(MiuiCompositionSamplingListener listener, int display,
            SurfaceControl surface, float scale, int flags) {
        Log.d("NabuApps", "MIUI composition sampling is unavailable on AOSP");
    }
    public static void unregister(MiuiCompositionSamplingListener listener) {}
}
