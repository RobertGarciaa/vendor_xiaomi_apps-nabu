# Translation table format

Each line is `<key><TAB><value>`. Because the file is line-based, these escapes
are used inside values and are expanded when the table is applied:

| Escape | Meaning |
| --- | --- |
| `\n` | newline |
| `\t` | tab |
| `\\` | literal backslash |

Values otherwise follow Android string escaping. A value must not contain a raw
newline; use `\n`. Leading and trailing spaces are preserved as written.

Format arguments (`%1$s`, `%d`, `%%`) must match the source string one-for-one;
`tools/check-translations.py` enforces that.
