/* SPDX-License-Identifier: Apache-2.0 */
package miui.cloud.sync.providers;

import miui.cloud.sync.SyncInfoProviderBase;

/**
 * App-local stand-in for MIUI's miui.cloud.sync.providers.SoundRecorderSyncInfoProvider.
 *
 * No Xiaomi cloud sync database exists on PixelOS. Inherited queryCount()
 * reports the unknown count rather than a fabricated zero.
 */
public final class SoundRecorderSyncInfoProvider extends SyncInfoProviderBase {
    public SoundRecorderSyncInfoProvider() {
        super();
    }
}
