## Full English build of LenovoMotorolovichY70 3.1 (unofficial)

The original app ships Russian-only. This build keeps the application untouched and replaces every
user-visible string with English.

**Asset:** `LenovoMotorolovichY70_v3.1_EN.apk`

```
size      814,027 bytes
sha256    39114ecf8e7bbcc3e1d66b63e8e79169959f253e18e63b9f582e62a49d362e7b
package   com.moto.resolutionmaster
version   3.1 (versionCode 31)
cert      SHA-256 49f8ec5349ea1098be287ba9470c90bca702af7987b8017a474da1a8e35c5844
```

### Install

```bash
adb install -r LenovoMotorolovichY70_v3.1_EN.apk
adb shell pm grant com.moto.resolutionmaster android.permission.WRITE_SECURE_SETTINGS
```

- Coming from the official Russian build: `adb uninstall com.moto.resolutionmaster` first (different
  signing key).
- Coming from the v3.0 English build: installs as a normal update, no uninstall needed.
- Resolution / refresh-rate switching on Android 14+ still needs Shizuku or root, exactly as upstream.

### What was translated

839 strings — 74 resources, 146 layout attributes (160 occurrences), 614 smali literals
(661 occurrences), covering dialog text, toasts, screen copy, all 111 debloat package descriptions,
and the Magisk `module.prop` / `service.sh` payloads.

- Format specifiers preserved exactly (`%1$s`, `%2$d`, `%.0f Hz`, `%d%%`) — checked with a parity
  pass over all pairs.
- Run-time concatenated fragments reflowed so the joined message reads as English word order, e.g.
  `"Enabled "` + n + `" of "` + m + `" preset packages."`
- Emoji preserved, including astral-plane ones emitted as UTF-16 surrogate pairs in smali.

### Verification

- Installed and launched on Android 14 (x86_64) emulator — COLD start OK, no crashes.
- All 9 activities opened and scrolled: 567 UI text nodes captured, **0 Cyrillic characters**,
  **0 exceptions**.
- Resource table structurally identical to the untranslated build
  (13 colors / 23 drawables / 167 ids / 11 layouts / 82 strings / 1 style); manifest content identical.
- Behaviour parity control against the untranslated v3.1: same confirmation dialog, same 15 s
  countdown, same rollback, no exceptions in either build.

Full evidence: [VERIFICATION.md](../blob/main/VERIFICATION.md).

### Upstream changes in 3.1

The Touch / Turbo module was removed by the original author — `TouchActivity` no longer exists
(10 activities → 9) and there are no touch-related strings left in the APK. Nothing was removed by
this translation.

### Credits

Original app: **nik.reneyj** (4PDA). NFC routing fix: **stepchansky**.
Unofficial fan localization, not affiliated with the original author, Motorola or Lenovo.
Only text literals were replaced; no code was added or removed. Re-signed with a locally generated
key, so it will not install over an author-signed build.
