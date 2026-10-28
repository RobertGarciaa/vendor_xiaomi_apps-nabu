#!/usr/bin/env python3
"""Manifest hardening shared by the ported Xiaomi apps.

This port deliberately severs every Xiaomi cloud tie:

  * automatic APK updates        — the app must not replace itself
  * Xiaomi Market links          — no market/deeplink hand-off for updates
  * Xiaomi cloud sync            — no account-backed sync components
  * Xiaomi account sign-in       — no login surfaces

This disables known manifest entry points and removes installation permissions.
It does not block direct network requests, outgoing intents, or code that later
re-enables its own component. Those require a separate DEX/runtime audit.

Two rules keep this honest:
  * only components whose class names match the families below are disabled,
  * a component is never removed, only marked android:enabled="false", so the
    package identity and any explicit introspection stay intact.
"""
from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

ANDROID_NS = 'http://schemas.android.com/apk/res/android'

# Component class-name fragments for each blocked family.
BLOCKED_FAMILIES = {
    # Xiaomi account sign-in and OAuth surfaces.
    'account': ('AccountTransparentActivity', 'AccountReceiver', 'XiaomiAccount',
                'PassportActivity', 'LoginActivity', 'OAuthActivity',
                'MiAuthenticatorService', 'AccountAuthenticator'),
    # Cloud sync / cloud backup / cloud settings.
    'cloud': ('CloudService', 'CloudSync', 'NotesSyncService', 'SyncService',
              'MiCloud', 'CloudBackup', 'CreationsSyncService', 'PushReceiver'),
    # Xiaomi Market update hand-off.
    'market': ('Market', 'UpdateAppsActivity', 'AppUpdate'),
}

# Permissions that only make sense with those services. They are not removed
# (removing a permission can change how the app behaves at runtime); instead the
# manifest declares them with a leading comment in build_* when reviewed. This
# set is only used to report what is present.
CLOUD_PERMISSIONS = (
    'com.xiaomi.permission.CLOUD_MANAGER',
    'com.xiaomi.permission.READ_WRITE_MICLOUD_SETTINGS',
    'com.xiaomi.permission.SYNC_TAG_DATA',
    'com.xiaomi.market.sdk.UPDATE',
    'com.miui.cloudserive.permission.USE_KEYCHAIN',
)


def _matches(name: str, fragment: str) -> bool:
    return fragment.lower() in name.lower()


def blocked_family(name: str, *, extra_components=(), extra_families=None):
    if name in extra_components:
        return 'explicit'
    # Do not disable an unrelated login/sync component just because its name is generic.
    if not name.startswith(('com.miui.', 'com.xiaomi.', 'miui.')):
        return None
    families = dict(BLOCKED_FAMILIES)
    if extra_families:
        families.update(extra_families)
    for family, fragments in families.items():
        if any(_matches(name, fragment) for fragment in fragments):
            return family
    return None


def block_xiaomi_services(manifest_path: Path, *, extra_components=(),
                          extra_families=None) -> list[tuple[str, str, str]]:
    """Disable every component that belongs to a blocked Xiaomi service family.

    Returns (tag, class name, family) for each component that was disabled.
    """
    ET.register_namespace('android', ANDROID_NS)
    tree = ET.parse(manifest_path)
    root = tree.getroot()
    app = root.find('application')
    if app is None:
        raise SystemExit('manifest has no <application>')

    families = dict(BLOCKED_FAMILIES)
    if extra_families:
        families.update(extra_families)

    disabled = []
    for tag in ('activity', 'activity-alias', 'service', 'receiver', 'provider'):
        for node in list(app.findall(tag)):
            name = node.get(f'{{{ANDROID_NS}}}name', '')
            if not name:
                continue
            package = root.get('package', '')
            qualified = package + name if name.startswith('.') else (
                package + '.' + name if '.' not in name else name)
            family = blocked_family(qualified, extra_components=extra_components,
                                    extra_families=extra_families)
            if family is None:
                continue
            node.set(f'{{{ANDROID_NS}}}enabled', 'false')
            disabled.append((tag, name, family))

    tree.write(manifest_path, encoding='utf-8', xml_declaration=True)
    return disabled


def drop_install_package_permission(manifest_path: Path) -> list[str]:
    """Remove both installer permission declarations; not a complete updater firewall."""
    ET.register_namespace('android', ANDROID_NS)
    tree = ET.parse(manifest_path)
    root = tree.getroot()

    removed = []
    for node in list(root.findall('uses-permission')):
        name = node.get(f'{{{ANDROID_NS}}}name', '')
        if name in ('android.permission.REQUEST_INSTALL_PACKAGES',
                    'android.permission.INSTALL_PACKAGES'):
            root.remove(node)
            removed.append(name)
    # uses-permission-sdk-23 / -sdk-m can also carry it.
    for tag in ('uses-permission-sdk-23', 'uses-permission-sdk-m'):
        for node in list(root.findall(tag)):
            name = node.get(f'{{{ANDROID_NS}}}name', '')
            if name in ('android.permission.REQUEST_INSTALL_PACKAGES',
                        'android.permission.INSTALL_PACKAGES'):
                root.remove(node)
                removed.append(name)

    tree.write(manifest_path, encoding='utf-8', xml_declaration=True)
    return removed


def report_cloud_permissions(manifest_path: Path) -> list[str]:
    """List Xiaomi cloud/market permissions still declared, for the build log."""
    tree = ET.parse(manifest_path)
    root = tree.getroot()
    found = []
    for tag in ('uses-permission', 'uses-permission-sdk-23', 'uses-permission-sdk-m'):
        for node in root.findall(tag):
            name = node.get(f'{{{ANDROID_NS}}}name', '')
            if name in CLOUD_PERMISSIONS:
                found.append(name)
    return sorted(set(found))


def drop_micloud_library(manifest_path: Path) -> list[str]:
    """Drop the absent cloud framework, whose supported APIs are app-local shims.

    An omitted android:required means true. Even a complete shim DEX cannot
    satisfy PackageManager's shared-library check during package scanning.
    Preserve every other uses-library declaration, including optional libraries.
    """
    ET.register_namespace('android', ANDROID_NS)
    tree = ET.parse(manifest_path)
    app = tree.getroot().find('application')
    if app is None:
        raise ValueError('manifest has no <application>')
    removed = []
    for node in list(app.findall('uses-library')):
        name = node.get(f'{{{ANDROID_NS}}}name', '')
        if name == 'micloud-sdk':
            app.remove(node)
            removed.append(name)
    tree.write(manifest_path, encoding='utf-8', xml_declaration=True)
    return removed
