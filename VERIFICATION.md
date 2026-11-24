# Verification log — v3.1 English build

Everything below was executed against the signed artifact in `apk/`:

```
sha256  39114ecf8e7bbcc3e1d66b63e8e79169959f253e18e63b9f582e62a49d362e7b
size    814,027 bytes
```

## 1. Install and launch

Emulator: AVD `en34`, `system-images;android-34;default;x86_64`, 1080×2340 @440 dpi, KVM.

```
$ adb install -r LenovoMotorolovichY70_v3.1_EN.apk
Install command complete in 302 ms
$ adb shell dumpsys package com.moto.resolutionmaster | grep versionName
    versionName=3.1
$ adb shell am start -W -n com.moto.resolutionmaster/.MainMenuActivity
Status: ok / LaunchState: COLD / TotalTime: 1615
```

`WRITE_SECURE_SETTINGS` was granted so the display screen could be exercised:

```
$ adb shell pm grant com.moto.resolutionmaster android.permission.WRITE_SECURE_SETTINGS
```

## 2. Every activity, every string

`tools/verify_screens.py` launches each activity, dumps the accessibility tree, scrolls three
times, and flags any Cyrillic text node or crash line.

| Activity | Text nodes | Cyrillic |
|---|---|---|
| MainMenuActivity | 124 | 0 |
| MainActivity (display) | 94 | 0 |
| EyeCareActivity | 36 | 0 |
| AodActivity | 24 | 0 |
| PowerActivity | 36 | 0 |
| NetworkSpeedActivity | 56 | 0 |
| AudioActivity | 44 | 0 |
| DebloatActivity | 113 | 0 |
| NfcFixActivity | 40 | 0 |
| **total** | **567** | **0** |

`CRASH/EXCEPTION LINES: 0`

`TouchActivity` from v3.0 is not in this list because upstream v3.1 removed it — it is absent from
the manifest of the *untranslated* APK as well (`am start` returns
`Activity class ... does not exist`). Re-verified independently:

```
$ grep -oP 'android:name="\.[A-Za-z]+Activity"' AndroidManifest.xml | sort -u     # 9 entries, no TouchActivity
$ # Cyrillic audit of the whole v3.1 string corpus:
touch-related RU strings in v3.1: 0
has Турбо-режим: False
has тач: False
```

## 3. Structural parity with the untranslated APK

Resource table, both builds:

```
RU: {'color': 13, 'drawable': 23, 'id': 167, 'layout': 11, 'string': 82, 'style': 1}
EN: {'color': 13, 'drawable': 23, 'id': 167, 'layout': 11, 'string': 82, 'style': 1}
strings still Cyrillic in EN table: 0
```

Manifest, `aapt2 dump xmltree` with line numbers stripped:

```
$ diff m31_orig.txt m31_en.txt   →   identical
```

Dex round-trip: the rebuilt `classes.dex` was decoded back to smali and diffed against the
translated tree — only `'` → `\'` re-encoding differences, no changed bytecode.

## 4. Behaviour parity control

The untranslated v3.1 was installed on the same emulator and driven through the same actions as the
English build (apply FHD+, observe the confirmation dialog and countdown, let it expire):

| | untranslated | English |
|---|---|---|
| dialog title | Подтверждение экрана | Display confirmation |
| body | Установлен режим FHD+ (390 DPI)… | Mode FHD+ (390 DPI) enabled… |
| buttons | ОТКАТИТЬ СЕЙЧАС / ОСТАВИТЬ | ROLL BACK NOW / KEEP |
| countdown rollback | returned to display screen | returned to display screen |
| exceptions | none | none |

Same dialog, same countdown, same rollback, no exceptions on either side.

## 5. Screens

`shots/` captures from the v3.1 run are kept outside the repository; the release notes carry the
main menu render.

## Known limitations

- All measurement was done on an x86_64 emulator. Emulator panels do not implement the Moto
  display manager, so resolution/refresh-rate writes cannot actually take effect there — that path
  was verified for *behaviour parity* (identical dialog/countdown/rollback and identical absence of
  exceptions), not for a real 1440p→1080p panel change. On a real Legion Y70 the same code runs
  against the hardware it was written for.
- Shizuku- and root-gated features (refresh-rate switching, AppOps freezing, bypass charging, NFC
  routing) were not exercised end-to-end; their strings and dialogs render correctly and the code
  paths run, but a stock emulator cannot grant those privileges.
