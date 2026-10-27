#!/usr/bin/env python3
"""Verify that the compiled shim DEX provides every member the ported app needs.

The app's DEX files reference MIUI/Xiaomi classes that PixelOS does not provide.
This script compares those references against the classes and members actually
present in the built shim DEX, plus the classes the app already defines itself.
A remaining gap would be NoClassDefFoundError / NoSuchMethodError at runtime.
"""
import re
import sys
from pathlib import Path

STR = re.compile(r'"(?:\\.|[^"\\])*"')
CLASS_LINE = re.compile(r'^\.class\s+.*?(L[^;]+;)\s*$', re.M)
METHOD_DECL = re.compile(r'^\.method\s+(?:[^\n]*?\s)?([^\s(]+)\(', re.M)
FIELD_DECL = re.compile(r'^\.field\s+[^\n]*?\s([^\s:]+):', re.M)
INVOKE = re.compile(r'invoke-\w+(?:/\w+)?\s+\{[^}]*\},\s*L([A-Za-z0-9_$/]+);->([^\s(]+)')
SFIELD = re.compile(r's(?:get|put)(?:-object|-boolean|-byte|-char|-short|-wide)?\s+\w+,\s*'
                    r'L([A-Za-z0-9_$/]+);->([^\s:]+):')
NEWINST = re.compile(r'new-instance\s+\w+,\s*L([A-Za-z0-9_$/]+);')
SUPER = re.compile(r'^\.super\s+L([A-Za-z0-9_$/]+);', re.M)
IMPL = re.compile(r'^\.implements\s+L([A-Za-z0-9_$/]+);', re.M)
TYPED_FIELD = re.compile(r'^\.field [^\n]*?:L([A-Za-z0-9_$/]+);', re.M)


def norm_method(name):
    """baksmali prints constructors as 'constructor <init>'."""
    return '<init>' if name in ('constructor', '<init>') else name


def parse_smali(root):
    root = Path(root)
    defined = set()
    methods = set()
    fields = set()
    refs = set()
    for f in root.rglob('*.smali'):
        text = f.read_text(errors='replace')
        m = CLASS_LINE.search(text)
        if m:
            defined.add(m.group(1)[1:-1])
        for name in METHOD_DECL.findall(text):
            methods.add(norm_method(name))
        for name in FIELD_DECL.findall(text):
            fields.add(name)
        body = STR.sub('""', text)
        for line in body.splitlines():
            s = line.strip()
            if not s or s.startswith('#'):
                continue
            for cls, member in INVOKE.findall(s):
                refs.add((cls, norm_method(member)))
            for cls, member in SFIELD.findall(s):
                refs.add((cls, member))
            for cls in NEWINST.findall(s):
                refs.add((cls, '<init>'))
        for cls in SUPER.findall(text):
            refs.add((cls, '<init>'))
        for cls in IMPL.findall(text):
            refs.add((cls, '<implements>'))
        for cls in TYPED_FIELD.findall(text):
            refs.add((cls, '<type>'))
    return defined, methods, fields, refs


def main(app_smali, shim_smali, framework_jar, verbose=False):
    app_defined, app_methods, app_fields, app_refs = parse_smali(app_smali)
    shim_defined, shim_methods, shim_fields, _shim_refs = parse_smali(shim_smali)

    provided = app_defined | shim_defined
    unresolved = []

    for cls, member in sorted(app_refs):
        if not cls.startswith(('miui/', 'com/miui/', 'com/xiaomi/', 'miuix/')):
            continue
        if cls in app_defined:
            continue
        if cls not in provided:
            unresolved.append((cls, member, 'class missing'))
            continue
        if member in ('<type>', '<implements>'):
            continue
        if cls in shim_defined and cls not in app_defined:
            if member == '<init>':
                if '<init>' not in shim_methods:
                    unresolved.append((cls, member, 'constructor missing'))
            elif member not in shim_methods and member not in shim_fields:
                unresolved.append((cls, member, 'member missing in shim'))

    print(f'app classes     : {len(app_defined)}')
    print(f'shim classes    : {len(shim_defined)}')
    print(f'shim methods    : {len(shim_methods)}')
    print(f'shim fields     : {len(shim_fields)}')
    print(f'unresolved      : {len(unresolved)}')
    for cls, member, why in unresolved:
        print(f'  {cls}->{member}  [{why}]')
    if verbose and not unresolved:
        print('all MIUI/Xiaomi references resolved by app classes or shims')
    return 1 if unresolved else 0


if __name__ == '__main__':
    sys.exit(main(*sys.argv[1:4], verbose='-v' in sys.argv))
