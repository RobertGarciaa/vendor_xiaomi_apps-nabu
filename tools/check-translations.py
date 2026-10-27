#!/usr/bin/env python3
"""Check a TSV translation table against the app's default strings.

Rules enforced here:
  * every key in the table exists in the app's default strings.xml
  * no translated value still contains CJK ideographs (lunar/sexagenary data is
    excluded upstream, not here)
  * printf-style format argument lists match the source string exactly
  * optional --complete requires the table to cover a given key list

This is the guard rail for the Korean translations; it never edits the table.
"""
import argparse
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

CJK = re.compile(r'[\u4e00-\u9fff\u3400-\u4dbf]')
FMT = re.compile(r'%\d+\$[-#+ 0(]*\d*(?:\.\d+)?[a-zA-Z]|%[-#+ 0(]*\d*(?:\.\d+)?[a-zA-Z]')


def load_xml_strings(path):
    root = ET.parse(path).getroot()
    out = {}
    for node in root.iter('string'):
        name = node.get('name')
        if name:
            out[name] = ''.join(node.itertext())
    return out


def load_tsv(path):
    out = {}
    for raw in Path(path).read_text().splitlines():
        if not raw.strip() or raw.startswith('#'):
            continue
        if '\t' not in raw:
            raise SystemExit(f'Malformed TSV line (no tab): {raw!r}')
        key, value = raw.split('\t', 1)
        if key in out:
            raise SystemExit(f'Duplicate key in TSV: {key}')
        out[key] = value
    return out


def decode_escapes(text):
    """Expand the table's single-line escapes into real characters."""
    out = []
    i = 0
    while i < len(text):
        ch = text[i]
        if ch == '\\' and i + 1 < len(text):
            nxt = text[i + 1]
            if nxt == 'n':
                out.append('\n')
                i += 2
                continue
            if nxt == 't':
                out.append('\t')
                i += 2
                continue
            if nxt == '\\':
                out.append('\\')
                i += 2
                continue
        out.append(ch)
        i += 1
    return ''.join(out)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--strings', required=True, type=Path,
                   help='decoded res/values/strings.xml of the stock app')
    p.add_argument('--tsv', required=True, type=Path)
    p.add_argument('--complete-from', type=Path,
                   help='file with one required key per line')
    p.add_argument('--allow-cjk-keys', type=Path,
                   help='file with keys allowed to keep CJK (regulatory numbers)')
    a = p.parse_args()

    source = load_xml_strings(a.strings)
    table = {k: decode_escapes(v) for k, v in load_tsv(a.tsv).items()}
    raw_table = load_tsv(a.tsv)
    allow_cjk = set()
    if a.allow_cjk_keys and a.allow_cjk_keys.is_file():
        allow_cjk = {x.strip() for x in a.allow_cjk_keys.read_text().splitlines()
                     if x.strip()}

    errors = []

    for key, value in table.items():
        if key not in source:
            errors.append(f'unknown key: {key}')
            continue
        if CJK.search(value) and key not in allow_cjk:
            errors.append(f'CJK left in {key}: {value!r}')
        src_fmt = FMT.findall(source[key])
        dst_fmt = FMT.findall(value)
        if sorted(src_fmt) != sorted(dst_fmt):
            errors.append(
                f'format args differ in {key}: source={src_fmt} translation={dst_fmt}')

    if a.complete_from:
        required = {x.strip() for x in a.complete_from.read_text().splitlines()
                    if x.strip()}
        missing = sorted(required - set(table))
        for key in missing:
            errors.append(f'missing translation: {key}')

    print(f'source keys : {len(source)}')
    print(f'table keys  : {len(table)}')
    print(f'errors      : {len(errors)}')
    for e in errors[:80]:
        print('  ' + e)
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())
