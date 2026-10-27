#!/usr/bin/env python3
"""Extract the pinned stock inputs from a shuntian dump and verify every SHA-1.

Nothing is written until every file has been read and hashed successfully, so a
wrong or damaged dump cannot leave a half-populated proprietary/ tree.
"""
import argparse
import hashlib
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIST = ROOT / 'proprietary-files.txt'


def read_pins():
    pins = []
    for line in LIST.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        src, sha1 = line.split('|', 1)
        pins.append((src.strip(), sha1.strip()))
    if not pins:
        raise SystemExit('No pins in ' + str(LIST))
    return pins


def sha1_file(path):
    h = hashlib.sha1()
    with path.open('rb') as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--dump', required=True, type=Path,
                   help='root of the extracted shuntian dump')
    p.add_argument('--verify-only', action='store_true',
                   help='only verify the already extracted proprietary/ tree')
    a = p.parse_args()

    pins = read_pins()

    if a.verify_only:
        bad = []
        for src, want in pins:
            dst = ROOT / 'proprietary' / src
            if not dst.is_file():
                bad.append((src, 'missing'))
            elif sha1_file(dst) != want:
                bad.append((src, 'hash mismatch'))
        if bad:
            for src, why in bad:
                print(f'FAIL {src}: {why}', file=sys.stderr)
            raise SystemExit(1)
        print(f'PASS: {len(pins)} pinned stock inputs verified')
        return

    dump = a.dump.resolve()
    if not dump.is_dir():
        raise SystemExit(f'Dump directory not found: {dump}')

    if (ROOT / 'proprietary').exists():
        residual = [x for x in (ROOT / 'proprietary').rglob('*') if x.is_file()]
        if residual:
            print(f'NOTE: replacing {len(residual)} existing file(s) under proprietary/',
                  file=sys.stderr)

    with tempfile.TemporaryDirectory(prefix='apps-nabu-extract-') as tmp:
        stage = Path(tmp)
        for src, want in pins:
            source = dump / src
            if not source.is_file():
                raise SystemExit(f'Missing pinned input in dump: {src}')
            got = sha1_file(source)
            if got != want:
                raise SystemExit(
                    f'Wrong firmware or damaged file: {src}\n'
                    f'  expected {want}\n  actual   {got}')
            target = stage / src
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
            print(f'verified {src}')

        # Only replace the tree once every pin has matched.
        if (ROOT / 'proprietary').exists():
            shutil.rmtree(ROOT / 'proprietary')
        shutil.copytree(stage, ROOT / 'proprietary')

    print(f'PASS: extracted and verified {len(pins)} pinned stock inputs')


if __name__ == '__main__':
    main()
