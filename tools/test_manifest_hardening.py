import tempfile
import unittest
from pathlib import Path
import xml.etree.ElementTree as ET
import harden_manifest as harden
import manifest_checks as checks
import appbuild
import zipfile

class ManifestTests(unittest.TestCase):
    def test_micloud_is_removed_without_losing_real_libraries(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'manifest.xml'
            path.write_text('''<manifest xmlns:android="http://schemas.android.com/apk/res/android">
              <application><uses-library android:name="micloud-sdk"/>
              <uses-library android:name="org.apache.http.legacy" android:required="true"/>
              <uses-library android:name="androidx.window.extensions" android:required="false"/>
              </application></manifest>''')
            self.assertEqual(harden.drop_micloud_library(path), ['micloud-sdk'])
            nodes = ET.parse(path).getroot().find('application').findall('uses-library')
            self.assertEqual([n.get('{'+harden.ANDROID_NS+'}name') for n in nodes],
                             ['org.apache.http.legacy', 'androidx.window.extensions'])
            self.assertEqual(harden.drop_micloud_library(path), [])

    def test_privapp_audit_honors_expired_max_sdk(self):
        root = {'children': [
            {'tag': 'uses-permission', 'attrs': {'name': 'expired', 'maxSdkVersion': '(type 0x10)0x1c'}},
            {'tag': 'uses-permission', 'attrs': {'name': 'current', 'maxSdkVersion': '37'}},
            {'tag': 'uses-permission-sdk-23', 'attrs': {'name': 'unlimited'}},
        ]}
        self.assertEqual(checks.active_permissions(root, 37), {'current', 'unlimited'})

    def test_rebuilt_table_includes_its_resource_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); stock = root/'stock.apk'; rebuilt = root/'rebuilt.apk'
            with zipfile.ZipFile(stock, 'w') as z:
                z.writestr('res/x.xml', b'original'); z.writestr('resources.arsc', b'old')
                z.writestr('assets/data', b'keep'); z.writestr('AndroidManifest.xml', b'old')
            with zipfile.ZipFile(rebuilt, 'w') as z:
                z.writestr('res/anim/expanded.xml', b'compiled')
            out = root/'out.apk'
            appbuild.build_apk(stock, b'manifest', {}, {}, out,
                               resources_arsc=b'new', rebuilt_resources=rebuilt)
            with zipfile.ZipFile(out) as z:
                self.assertEqual(z.read('res/anim/expanded.xml'), b'compiled')
                self.assertEqual(z.read('res/x.xml'), b'original')
                self.assertEqual(z.read('assets/data'), b'keep')
            with self.assertRaises(ValueError):
                appbuild.build_apk(stock, b'manifest', {}, {}, out, resources_arsc=b'new')
    def test_shims_preserve_app_owned_class(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); app = root / 'app'; shims = root / 'shims'
            app.mkdir(); shims.mkdir()
            declaration = '.class public Lcom/xiaomi/common/Optional;\n.super Ljava/lang/Object;\n'
            (app / 'Owned.smali').write_text(declaration)
            (shims / 'Owned.smali').write_text(declaration)
            (shims / 'Needed.smali').write_text('.class public Lmiui/os/Build;\n.super Ljava/lang/Object;\n')
            output = appbuild.filtered_shims(shims, app, root / 'output')
            self.assertFalse((output / 'Owned.smali').exists())
            self.assertTrue((output / 'Needed.smali').exists())
    def test_scoped_block_and_installer_declarations(self):
        original = '''<manifest xmlns:android="http://schemas.android.com/apk/res/android" package="com.miui.notes">
        <uses-permission android:name="android.permission.REQUEST_INSTALL_PACKAGES"/>
        <uses-permission-sdk-23 android:name="android.permission.INSTALL_PACKAGES"/>
        <uses-permission android:name="android.permission.INTERNET"/>
        <application><activity android:name=".AccountTransparentActivity"/>
        <service android:name="com.miui.notes.cloudservice.NotesSyncService"/>
        <activity android:name="org.example.LoginActivity"/>
        <activity android:name=".EditorActivity"/></application></manifest>'''
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'manifest.xml'; path.write_text(original)
            blocked = harden.block_xiaomi_services(path)
            self.assertEqual(len(blocked), 2)
            self.assertEqual(len(harden.drop_install_package_permission(path)), 2)
            root = ET.parse(path).getroot(); nodes = list(root.find('application'))
            enabled = '{'+harden.ANDROID_NS+'}enabled'
            self.assertTrue(all(n.get(enabled) == 'false' for n in nodes[:2]))
            self.assertTrue(all(n.get(enabled) is None for n in nodes[2:]))
            self.assertEqual(len(root.findall('uses-permission')), 1)
            self.assertEqual(harden.block_xiaomi_services(path), blocked)
            self.assertFalse(harden.drop_install_package_permission(path))

    def test_xmltree_does_not_borrow_sibling_disabled_flag(self):
        tree = checks.parse_xmltree('''N: android=http://schemas.android.com/apk/res/android
  E: manifest (line=1)
    A: package="com.miui.notes"
    E: uses-permission (line=2)
      A: http://schemas.android.com/apk/res/android:name(0x01010003)="android.permission.INSTALL_PACKAGES"
    E: application (line=3)
      E: service (line=4)
        A: http://schemas.android.com/apk/res/android:name(0x01010003)=".NotesSyncService"
      E: service (line=5)
        A: http://schemas.android.com/apk/res/android:name(0x01010003)=".OtherService"
        A: http://schemas.android.com/apk/res/android:enabled(0x0101000e)=false
''')
        components = checks.components(tree)
        self.assertFalse(checks.disabled(components['com.miui.notes.NotesSyncService']))
        self.assertTrue(checks.disabled(components['com.miui.notes.OtherService']))
        self.assertIn('android.permission.INSTALL_PACKAGES', checks.permissions(tree))
        self.assertTrue(checks.disabled({'attrs': {'enabled': '(type 0x12)0x0'}}))
        self.assertFalse(checks.disabled({'attrs': {'enabled': '0xffffffff'}}))
        with self.assertRaises(ValueError): checks.parse_xmltree('error: manifest dump failed')

if __name__ == '__main__': unittest.main()
