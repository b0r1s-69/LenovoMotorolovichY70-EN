## Full English build of LenovoMotorolovichY70 3.2 (unofficial)

The app ships Russian-only. This build is a **translation only**: every user-visible string is
English, nothing else was touched.

**Asset:** `LenovoMotorolovichY70_v3.2_EN.apk`

```
size      822,219 bytes
sha256    57d95678544f8f8375488ef603e9175106a2c2dd27ee6bd807ad168b12576909
package   com.moto.resolutionmaster
version   3.2 (versionCode 32)
dex       classes.dex only — same class set as upstream
cert      SHA-256 49f8ec5349ea1098be287ba9470c90bca702af7987b8017a474da1a8e35c5844
```

### Install

```bash
adb install -r LenovoMotorolovichY70_v3.2_EN.apk
adb shell pm grant com.moto.resolutionmaster android.permission.WRITE_SECURE_SETTINGS
```

- From the official Russian build: `adb uninstall com.moto.resolutionmaster` first (different key).
- From an earlier English build on this repo: normal update, no uninstall.

### What was translated

841-entry ru → en map. For 3.2 specifically: 2 new strings, plus 74 resources, 146 layout
attributes (160 occurrences) and 616 smali literals (668 occurrences) carried over from the map.
Format specifiers preserved exactly, concatenated message fragments reflowed, emoji kept as
UTF-16 surrogate pairs.

### Nothing else changed

- Resource table structurally identical to upstream: 13 colours / 23 drawables / 167 ids /
  11 layouts / 82 strings / 1 style — **no added resources, none removed**.
- `AndroidManifest.xml` content identical to the original (line numbers normalised, diff empty).
- Single `classes.dex`, exactly like the upstream APK — no extra dex, no injected code.

### Verification

- 8 menu screens opened and scrolled on Android 14 x86_64: 0 Cyrillic text nodes, 0 crashes.
- Full evidence: [VERIFICATION.md](https://github.com/b0r1s-69/LenovoMotorolovichY70-EN/blob/main/VERIFICATION.md).

### Upstream changes carried in 3.2

Bypass charging became root-gated (`moto_extend_service` is signature-protected) and every
sub-activity is `exported="false"` now, so the screens are reachable only through the menu cards.

### Credits

Original app: **nik.reneyj** (4PDA). NFC routing fix: **stepchansky**.
Unofficial fan localization; not affiliated with the original author, Motorola or Lenovo.
Only text literals were replaced. Re-signed with a local key, so it will not install over an
author-signed build.
