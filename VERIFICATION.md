# Verification log

Latest run: **v3.2**. The v3.1 log is kept at the bottom for comparison.

## v3.2 (versionCode 32)

Artifact:

```
sha256  8bf07b581d2843056b1c0a0f4d99256ef25041041b3644b589930cf438f9e283
size    830,493 bytes
dex     classes.dex (translated original) + classes2.dex (charge-limit feature)
```

### Screens

v3.2 made every sub-activity `exported="false"`, so screens are reached through the menu cards
instead of `am start`. 8 cards, all opened, scrolled three times each:

| Card | Activity | Text nodes | Cyrillic |
|---|---|---|---|
| Display and resolution | MainActivity | 98 | 0 |
| Eye protection | EyeCareActivity | 36 | 0 |
| Smart Always On Display | AodActivity | 24 | 0 |
| Power and Bypass Charging | PowerActivity | 76 | 0 |
| Audio and Bluetooth | AudioActivity | 44 | 0 |
| Network speed | NetworkSpeedActivity | 56 | 0 |
| App cleanup | DebloatActivity | 117 | 0 |
| NFC fix | NfcFixActivity | 40 | 0 |
| **total** | | **523** | **0** |

`CRASH/EXCEPTION LINES: 0`

### Charge-limit feature

| Check | Observed |
|---|---|
| card renders | Off / 80% / 85% / 90% / 95%, Root badge, footer note |
| tap 80% | `Limit: 80% • root required to enforce • battery 100%` |
| tap 90% | `Limit: 90% • root required to enforce • battery 100%` |
| tap Off | `Limit: Off • charging to 100%` |
| persistence | selection survives re-render (read back from `SharedPreferences`) |
| crashes | none |
| shell semantics | `test -w`, `echo 0 > node`, `cat` read-back validated on a local POSIX shell |

Emulator battery node inventory (`/sys/class/power_supply/battery/`): `capacity`, `status`, `temp`,
`voltage_now`, … — **no** `*charging_enabled*` and no `charge_*limit*` node, and an app on a stock
emulator image cannot obtain root. So enforcement itself is unverified on hardware; everything up
to the sysfs write is verified.

### Structural parity

```
RU resources: color 13, drawable 23, id 167, layout 11, string 82, style 1
EN resources: color 13, drawable 23, id 174, layout 11, string 92, style 1
  added ids:     btn_cl_80, btn_cl_85, btn_cl_90, btn_cl_95, btn_cl_off, card_charge_limit, tv_cl_status
  added strings: cl_80, cl_85, cl_90, cl_95, cl_badge, cl_desc, cl_footer, cl_off, cl_status_off, cl_title
  removed:       nothing
Cyrillic in EN resource table: 0
Manifest diff vs original: exactly one added service (.ChargeLimitService, specialUse)
```

---

# v3.1 (versionCode 31)

Everything below was executed against the v3.1 artifact:

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
