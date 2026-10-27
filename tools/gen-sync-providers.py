#!/usr/bin/env python3
"""Generate the empty MIUI cloud sync provider shims.

Each provider is a named subclass with no data source on PixelOS. They report
unknown counts (-1) through SyncInfoProviderBase.queryCount, never a fake zero.
Generated sources are committed; rerunning must reproduce them byte for byte.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'shims/src/miui/cloud/sync/providers'

PROVIDERS = [
    'AntispamSyncInfoProvider',
    'BrowserSyncInfoProvider',
    'CalendarSyncInfoProvider',
    'CalllogSyncInfoProvider',
    'ContactsSyncInfoProvider',
    'GallerySyncInfoProvider',
    'NotesSyncInfoProvider',
    'PersonalAssistantSyncInfoProvider',
    'QuickSearchBoxProvider',
    'SmsSyncInfoProvider',
    'SoundRecorderSyncInfoProvider',
    'WifiSyncInfoProvider',
]

TEMPLATE = '''/* SPDX-License-Identifier: Apache-2.0 */
package miui.cloud.sync.providers;

import miui.cloud.sync.SyncInfoProviderBase;

/**
 * App-local stand-in for MIUI's miui.cloud.sync.providers.{name}.
 *
 * No Xiaomi cloud sync database exists on PixelOS. Inherited queryCount()
 * reports the unknown count rather than a fabricated zero.
 */
public final class {name} extends SyncInfoProviderBase {{
    public {name}() {{
        super();
    }}
}}
'''


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name in PROVIDERS:
        path = OUT / f'{name}.java'
        text = TEMPLATE.format(name=name)
        if path.exists() and path.read_text() != text:
            path.write_text(text)
            print(f'updated {path.name}')
        elif not path.exists():
            path.write_text(text)
            print(f'created {path.name}')
    print(f'{len(PROVIDERS)} sync provider shims in {OUT}')


if __name__ == '__main__':
    main()
