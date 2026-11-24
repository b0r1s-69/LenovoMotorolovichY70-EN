#!/usr/bin/env python3
"""Per-activity verification: launch, capture text + shot, scroll, optional safe taps."""
import subprocess, re, time, os, json, sys

ADB = os.path.expanduser('~/android-sdk/platform-tools/adb')
PKG = 'com.moto.resolutionmaster'
TAG = sys.argv[1] if len(sys.argv) > 1 else 'en'
OUT = f'/home/admin1/apk-en/shots/{TAG}'
os.makedirs(OUT, exist_ok=True)

ACT = {'menu': '.MainMenuActivity', 'display': '.MainActivity', 'eyecare': '.EyeCareActivity',
       'aod': '.AodActivity', 'touch': '.TouchActivity', 'power': '.PowerActivity',
       'netspeed': '.NetworkSpeedActivity', 'audio': '.AudioActivity',
       'debloat': '.DebloatActivity', 'nfc': '.NfcFixActivity'}

def sh(*a):
    return subprocess.run([ADB, *a], capture_output=True, text=True, timeout=90).stdout

def dump(name):
    for _ in range(3):
        o = sh('shell', 'uiautomator', 'dump', '/sdcard/v.xml')
        if 'dumped' in o:
            break
        time.sleep(1)
    sh('pull', '/sdcard/v.xml', f'/tmp/v_{name}.xml')
    s = open(f'/tmp/v_{name}.xml', encoding='utf-8', errors='replace').read()
    png = subprocess.run([ADB, 'exec-out', 'screencap', '-p'], capture_output=True).stdout
    open(f'{OUT}/{name}.png', 'wb').write(png)
    return [t for t in re.findall(r'text="([^"]*)"', s) if t.strip()], s

res = {}
for name, act in ACT.items():
    sh('shell', 'am', 'force-stop', PKG)
    sh('shell', 'am', 'start', '-n', f'{PKG}/{act}')
    time.sleep(2.5)
    texts, xml = dump(name)
    allt = list(texts)
    for i in range(3):
        sh('shell', 'input', 'swipe', '540', '1700', '540', '900', '280')
        time.sleep(0.9)
        t2, x2 = dump(f'{name}_s{i}')
        allt += ['SCROLL'] + t2
        xml += x2
    res[name] = allt
    cyr = [t for t in allt if re.search('[\u0400-\u04FF]', t)]
    print(f'{name:10s} nodes={len(allt):3d} cyrillic={len(cyr)} first={texts[0][:40] if texts else "-"}')

json.dump(res, open(f'{OUT}/texts.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
total = sum(len(v) for v in res.values())
cyr_all = [(k, t) for k, v in res.items() for t in v if re.search('[\u0400-\u04FF]', t)]
print(f'\nTOTAL text nodes: {total}; CYRILLIC: {len(cyr_all)}')
for k, t in cyr_all[:10]:
    print('  ', k, t[:60])

log = subprocess.run([ADB, 'logcat', '-d', '-v', 'brief'], capture_output=True, text=True).stdout
bad = [l for l in log.splitlines() if re.search(r'FATAL|AndroidRuntime: .*com\.moto|com\.moto.*(Exception|NotFoundException|InflateException)', l)]
print('CRASH/EXCEPTION LINES:', len(bad))
for l in bad[:10]:
    print('  ', l[:170])
