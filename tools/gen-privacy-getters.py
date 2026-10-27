#!/usr/bin/env python3
"""Generate the Xiaomi account privacy-data getter shims.

The stock com.xiaomi.account.privacy_data getters collect device identifiers for
the Xiaomi account SDK. That SDK is not shipped on PixelOS and this port never
uploads anything, so every getter returns null (unavailable) instead of reading
or fabricating an identifier. Callers already handle a null value.

Generated sources are committed; rerunning must reproduce them byte for byte.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'shims/src/com/xiaomi/account/privacy_data'

# (sub-package, class name)
GETTERS = [
    ('android_id', 'AndroidIdGetter'),
    ('bluetooth_address', 'BluetoothAddressGetter'),
    ('bluetooth_name', 'BluetoothNameGetter'),
    ('bssid', 'BSSIDGetter'),
    ('configured_ssids', 'ConfiguredSSIDsGetter'),
    ('device_id', 'DeviceIdGetter'),
    ('iccid', 'ICCIDGetter'),
    ('imsi', 'IMSIGetter'),
    ('line_1_number', 'Line1NumberGetter'),
    ('mac_address', 'MacAddressGetter'),
    ('mccmnc', 'MCCMNCGetter'),
    ('miui_device_id', 'MiuiDeviceIdGetter'),
    ('mobile_data_enable', 'MobileDataEnableGetter'),
    ('network_mccmnc', 'NetworkMCCMNCGetter'),
    ('oaid', 'OAIDGetter'),
    ('sim_in_service', 'SimInServiceGetter'),
    ('ssid', 'SSIDGetter'),
    ('sub_id', 'SubIdGetter'),
]

TEMPLATE = '''/* SPDX-License-Identifier: Apache-2.0 */
package com.xiaomi.account.privacy_data.{pkg};

/**
 * App-local stand-in for Xiaomi's privacy_data {cls}.
 *
 * Returns null because the Xiaomi account SDK is absent and this port uploads
 * nothing. No device identifier is read, stored or invented.
 */
public class {cls} {{
    public {cls}() {{
    }}

    public String get() {{
        return null;
    }}
}}
'''


def main():
    for pkg, cls in GETTERS:
        target = OUT / pkg
        target.mkdir(parents=True, exist_ok=True)
        path = target / f'{cls}.java'
        text = TEMPLATE.format(pkg=pkg, cls=cls)
        if not path.exists() or path.read_text() != text:
            path.write_text(text)
            print(f'wrote {pkg}/{cls}.java')
    print(f'{len(GETTERS)} privacy getter shims in {OUT}')


if __name__ == '__main__':
    main()
