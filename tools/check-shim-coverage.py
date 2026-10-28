#!/usr/bin/env python3
"""Check exact external MIUI descriptors against app-local DEX definitions.

Includes MIUI additions under android.*, not just miui.* packages. This is a
linkage check for the supplied classes, not a test of runtime behavior, hidden
Android APIs, reflection, JNI or optional service availability.
"""
import re
import sys
from pathlib import Path

STR = re.compile(r'"(?:\\.|[^"\\])*"')
CLASS = re.compile(r'^\.class[ \t]+(?:\S+[ \t]+)*(L[^;\s]+;)[ \t]*$', re.M)
METHOD = re.compile(r'^\.method[ \t]+(?:\S+[ \t]+)*([^\s(]+\([^\n]+)$', re.M)
FIELD = re.compile(r'^\.field[ \t]+(?:\S+[ \t]+)*([^\s:]+:[^\s=]+)', re.M)
REF = re.compile(r'(L[^;\s]+;)->([^\s,]+)')
TYPE = re.compile(r'L[^;\s()]+;')


def is_miui(owner):
    return owner.startswith(('Lmiui/', 'Lcom/miui/', 'Lcom/xiaomi/', 'Lmiuix/')) or (
        owner.startswith('Landroid/') and 'miui' in owner.lower())


def parse_smali(root):
    classes, references, types = {}, set(), set()
    for path in Path(root).rglob('*.smali'):
        text = path.read_text(errors='replace')
        declaration = CLASS.search(text)
        if not declaration:
            raise ValueError('Missing class declaration: ' + str(path))
        owner = declaration[1]
        if owner in classes:
            raise ValueError('Duplicate DEX class: ' + owner)
        parents = re.findall(r'^\.(?:super|implements)\s+(L[^;]+;)', text, re.M)
        classes[owner] = (set(METHOD.findall(text)) | set(FIELD.findall(text)), parents)
        body = STR.sub('""', text)
        # Build-retained annotation classes may be deliberately stripped from stock DEX.
        body = re.sub(r'(?ms)^[ \t]*\.annotation build [^\n]*\n.*?^[ \t]*\.end annotation[ \t]*$', '', body)
        references.update((owner, member) for owner, member in REF.findall(body) if is_miui(owner))
        types.update(owner for owner in TYPE.findall(body) if is_miui(owner))
    return classes, references, types


def unresolved(app, shims):
    app_classes, references, types = app
    shim_classes, _, _ = shims
    provided = dict(shim_classes)
    provided.update(app_classes)
    missing = [owner + ' [class missing]' for owner in sorted(types - provided.keys())]

    def resolves(owner, member, visited):
        if owner in visited or owner not in provided:
            return False
        members, parents = provided[owner]
        if member in members:
            return True
        # Constructors must exist on the requested class; they are not inherited.
        if member.startswith('<init>('):
            return False
        return any(resolves(parent, member, visited | {owner}) for parent in parents)

    for owner, member in sorted(references):
        # Internal app classes are not compatibility shims. Their own inherited
        # Android methods are outside this deliberately scoped check.
        if owner in app_classes or owner not in provided:
            continue
        if not resolves(owner, member, set()):
            missing.append(owner + '->' + member + ' [exact shim member missing]')
    return missing


def main(app_smali, shim_smali, _framework_jar=None, verbose=False):
    app = parse_smali(app_smali)
    shims = parse_smali(shim_smali)
    missing = unresolved(app, shims)
    print(f'app classes: {len(app[0])}; shim classes: {len(shims[0])}; unresolved: {len(missing)}')
    for failure in missing:
        print('  ' + failure)
    if verbose and not missing:
        print('PASS: exact external MIUI class/member descriptors, including android.* additions')
    return bool(missing)


if __name__ == '__main__':
    sys.exit(main(*sys.argv[1:4], verbose='-v' in sys.argv))
