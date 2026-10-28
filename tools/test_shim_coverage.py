import importlib.util
from pathlib import Path
import tempfile
import unittest
spec = importlib.util.spec_from_file_location('coverage', Path(__file__).with_name('check-shim-coverage.py'))
coverage = importlib.util.module_from_spec(spec)
spec.loader.exec_module(coverage)

class CoverageTests(unittest.TestCase):
    def test_same_name_on_another_class_or_overload_does_not_satisfy_reference(self):
        app = ({}, {('Lmiui/Required;', 'query(I)Z')}, {'Lmiui/Required;'})
        shims = ({'Lmiui/Required;': ({'query()Z'}, []),
                  'Lmiui/Other;': ({'query(I)Z'}, [])}, set(), set())
        self.assertEqual(len(coverage.unresolved(app, shims)), 1)

    def test_private_class_and_android_miui_field_reference_are_parsed(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'App.smali'
            path.write_text('.class Lexample/Private;\n.super Ljava/lang/Object;\n'
                            'sget v0, Landroid/util/MiuiDisplayMetrics;->DENSITY_DEVICE:I\n'
                            '.annotation build Lmiuix/StrippedAnnotation;\n.end annotation\n')
            classes, refs, types = coverage.parse_smali(Path(directory))
            self.assertIn('Lexample/Private;', classes)
            self.assertIn(('Landroid/util/MiuiDisplayMetrics;', 'DENSITY_DEVICE:I'), refs)
            self.assertEqual(types, {'Landroid/util/MiuiDisplayMetrics;'})

    def test_exact_inherited_shim_member_is_accepted(self):
        app = ({}, {('Lmiui/Child;', 'query(I)Z')}, {'Lmiui/Child;'})
        shims = ({'Lmiui/Child;': (set(), ['Lmiui/Parent;']),
                  'Lmiui/Parent;': ({'query(I)Z'}, [])}, set(), set())
        self.assertFalse(coverage.unresolved(app, shims))

    def test_constructor_on_parent_does_not_satisfy_child_constructor(self):
        app = ({}, {('Lmiui/Child;', '<init>(I)V')}, {'Lmiui/Child;'})
        shims = ({'Lmiui/Child;': (set(), ['Lmiui/Parent;']),
                  'Lmiui/Parent;': ({'<init>(I)V'}, [])}, set(), set())
        self.assertEqual(len(coverage.unresolved(app, shims)), 1)

if __name__ == '__main__': unittest.main()
