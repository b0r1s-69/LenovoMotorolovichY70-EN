#!/usr/bin/env python3
"""Apply the English translation map to a decoded (apktool) APK tree.

Usage:
    apktool d -f app.apk -o dec
    python3 tools/apply_translations.py dec
    apktool b dec -o unsigned.apk

The map (translation/en.json) is keyed by the original Russian string and
applied to three places: res/values/strings.xml, res/layout/*.xml attributes,
and smali string literals. Format specifiers, surrounding spaces and the
apktool quoting convention are preserved.
"""
import json
import re
import sys
import glob
import os

CYR = re.compile('[\u0400-\u04FF]')


def xml_escape(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def esc_smali(s):
    """Encode a Python string as a smali string literal body."""
    out = []
    for ch in s:
        if ch == '\\':
            out.append('\\\\')
        elif ch == '"':
            out.append('\\"')
        elif ch == '\n':
            out.append('\\n')
        elif ch == '\t':
            out.append('\\t')
        elif ch == '\r':
            out.append('\\r')
        elif ord(ch) > 0x7e:
            o = ord(ch)
            if o > 0xFFFF:  # astral chars must be emitted as a UTF-16 surrogate pair
                o -= 0x10000
                out.append('\\u%04x\\u%04x' % (0xD800 + (o >> 10), 0xDC00 + (o & 0x3FF)))
            else:
                out.append('\\u%04x' % o)
        else:
            out.append(ch)
    return ''.join(out)


def unescape_smali(raw):
    out = []
    i = 0
    while i < len(raw):
        c = raw[i]
        if c == '\\' and i + 1 < len(raw):
            n = raw[i + 1]
            if n == 'u' and i + 5 < len(raw) and re.fullmatch(r'[0-9a-fA-F]{4}', raw[i + 2:i + 6]):
                out.append(chr(int(raw[i + 2:i + 6], 16)))
                i += 6
                continue
            out.append({'n': '\n', 't': '\t', 'r': '\r', '"': '"', '\\': '\\'}.get(n, n))
            i += 2
            continue
        out.append(c)
        i += 1
    s = ''.join(out)
    try:
        return s.encode('utf-16', 'surrogatepass').decode('utf-16')
    except Exception:
        return s


def unquote(s):
    if len(s) > 2 and s.startswith('"') and s.endswith('"'):
        return s[1:-1]
    return s


def main():
    dec = sys.argv[1] if len(sys.argv) > 1 else 'dec'
    here = os.path.dirname(os.path.abspath(__file__))
    MAP = json.load(open(os.path.join(here, '..', 'translation', 'en.json'), encoding='utf-8'))
    stats = {'res': 0, 'layout': 0, 'smali': 0, 'miss': []}

    # 1) strings.xml
    p = os.path.join(dec, 'res', 'values', 'strings.xml')
    if os.path.exists(p):
        txt = open(p, encoding='utf-8').read()

        def repl_string(m):
            name, attrs, val = m.group(1), m.group(2), m.group(3)
            if not CYR.search(val):
                return m.group(0)
            quoted = len(val) >= 2 and val.startswith('"') and val.endswith('"')
            core = val[1:-1] if quoted else val
            en = MAP.get(core) or MAP.get(val)
            if en is None:
                stats['miss'].append(('res', name, core[:60]))
                return m.group(0)
            out = xml_escape(en)
            if quoted or out.startswith(' ') or out.endswith(' ') or en.startswith('\n') or en.endswith('\n'):
                out = '"' + out + '"'
            stats['res'] += 1
            return '<string name="%s"%s>%s</string>' % (name, attrs, out)

        txt = re.sub(r'<string name="([^"]+)"([^>]*)>(.*?)</string>', repl_string, txt, flags=re.S)
        open(p, 'w', encoding='utf-8').write(txt)

    # 2) layouts — newlines are the two characters \n, quotes must be &quot;
    attr_re = re.compile(r'(android:(?:text|hint|title|contentDescription|summary)|tools:text)="([^"]*)"')
    for f in sorted(glob.glob(os.path.join(dec, 'res', 'layout', '*.xml'))):
        s = open(f, encoding='utf-8').read()

        def repl_attr(m):
            a, v = m.group(1), m.group(2)
            if not CYR.search(v):
                return m.group(0)
            en = MAP.get(v)
            if en is None:
                stats['miss'].append(('layout', os.path.basename(f), v[:60]))
                return m.group(0)
            esc = en.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            esc = esc.replace('\n', '\\n').replace('"', '&quot;')
            stats['layout'] += 1
            return '%s="%s"' % (a, esc)

        s2 = attr_re.sub(repl_attr, s)
        if s2 != s:
            open(f, 'w', encoding='utf-8').write(s2)

    # 3) smali
    lit = re.compile(r'"((?:[^"\\]|\\.)*)"')
    for f in sorted(glob.glob(os.path.join(dec, 'smali', '**', '*.smali'), recursive=True)):
        s = open(f, encoding='utf-8', errors='replace').read()
        if not CYR.search(s) and '\\u04' not in s:
            continue
        changed = [False]

        def repl_lit(m):
            dec_s = unescape_smali(m.group(1))
            if not CYR.search(dec_s):
                return m.group(0)
            en = MAP.get(dec_s)
            if en is None:
                stats['miss'].append(('smali', os.path.basename(f), dec_s[:60]))
                return m.group(0)
            changed[0] = True
            stats['smali'] += 1
            return '"' + esc_smali(en) + '"'

        s2 = lit.sub(repl_lit, s)
        if changed[0]:
            open(f, 'w', encoding='utf-8').write(s2)

    print('applied: %d res / %d layout / %d smali' % (stats['res'], stats['layout'], stats['smali']))
    if stats['miss']:
        print('untranslated (%d):' % len(stats['miss']))
        for m in stats['miss'][:40]:
            print('  ', m)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
