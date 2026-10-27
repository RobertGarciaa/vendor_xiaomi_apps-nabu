#!/usr/bin/env python3
"""Expand or collapse the escape sequences used by the translation tables.

Table values are single-line, so a newline is written as \\n. This helper keeps
the encoding in one place instead of repeating it in every tool.

  encode: real text  -> table value
  decode: table value -> real text
"""
import sys


def encode(text):
    return (text.replace('\\', '\\\\')
                .replace('\n', '\\n')
                .replace('\t', '\\t'))


def decode(text):
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
    if len(sys.argv) != 3 or sys.argv[1] not in ('encode', 'decode'):
        raise SystemExit(__doc__)
    fn = encode if sys.argv[1] == 'encode' else decode
    data = sys.stdin.read()
    if data.endswith('\n'):
        data = data[:-1]
    sys.stdout.write(fn(data))
    sys.stdout.write('\n')


if __name__ == '__main__':
    main()
