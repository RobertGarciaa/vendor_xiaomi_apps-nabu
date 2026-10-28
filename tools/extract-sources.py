#!/usr/bin/env python3
"""Extract the pinned stock inputs from a shuntian dump and verify every SHA-1.

Nothing is written until every file has been read and hashed successfully, so a
wrong or damaged dump cannot leave a half-populated proprietary/ tree.
"""
import argparse
import hashlib
import os
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
    p.add_argument('--dump', type=Path,
                   help='root of the extracted shuntian dump')
    p.add_argument('--nabu-dump', type=Path,
                   help='Pad 5 OS1.0.6.0 dump for pins under the nabu/ staging prefix')
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

    for label, dump in (('--dump', a.dump), ('--nabu-dump', a.nabu_dump)):
        if dump is None or not dump.is_dir():
            raise SystemExit(f'{label} must name an existing source dump')

    with tempfile.TemporaryDirectory(prefix='apps-nabu-extract-') as tmp:
        stage = Path(tmp)
        for src, want in pins:
            source = (a.nabu_dump / src.removeprefix('nabu/')
                      if src.startswith('nabu/') else a.dump / src)
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

        # Replace only verified input files. Never delete ignored ported APKs or
        # unrelated staging files when refreshing an extraction. Each replace is
        # atomic even when TMPDIR and the repository use different filesystems.
        for src, _ in pins:
            target = ROOT / 'proprietary' / src
            target.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(dir=target.parent, prefix='.extract-', delete=False) as temporary:
                replacement = Path(temporary.name)
            try:
                shutil.copy2(stage / src, replacement)
                os.replace(replacement, target)
            finally:
                replacement.unlink(missing_ok=True)

    print(f'PASS: extracted and verified {len(pins)} pinned stock inputs')


if __name__ == '__main__':
    main()
