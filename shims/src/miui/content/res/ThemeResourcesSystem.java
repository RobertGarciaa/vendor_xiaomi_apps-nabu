/* SPDX-License-Identifier: Apache-2.0 */
package miui.content.res;

import java.io.InputStream;

/**
 * App-local stand-in for MIUI's miui.content.res.ThemeResourcesSystem.
 *
 * An empty MIUI system theme. Every lookup misses, which is the correct answer
 * when no MIUI theme provider is installed. Never reports an icon it does not
 * have.
 */
public final class ThemeResourcesSystem {
    public ThemeResourcesSystem() {
    }

    public boolean hasIcon(String name) {
        return false;
    }

    public InputStream getIconStream(String name, long[] size) {
        return null;
    }
}
