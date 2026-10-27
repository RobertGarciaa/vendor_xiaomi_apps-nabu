/* SPDX-License-Identifier: Apache-2.0 */
package miui.cloud.sync.providers;

import miui.cloud.sync.SyncInfoProviderBase;

/**
 * App-local stand-in for MIUI's miui.cloud.sync.providers.ContactsSyncInfoProvider.
 *
 * No Xiaomi cloud sync database exists on PixelOS. Inherited queryCount()
 * reports the unknown count rather than a fabricated zero.
 */
public final class ContactsSyncInfoProvider extends SyncInfoProviderBase {
    public ContactsSyncInfoProvider() {
        super();
    }
}
