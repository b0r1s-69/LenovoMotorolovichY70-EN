# LenovoMotorolovichY70 — English translation (v3.1)

Unofficial full English localization of **LenovoMotorolovichY70** (`com.moto.resolutionmaster`),
a display / power / debloat toolkit for the **Lenovo Legion Y70** and **Moto Edge 70 Max**.
The original app is Russian-only; this build ships the same code with every user-visible
string translated to English.

**Download:** see the [Releases](../../releases) page.

| | |
|---|---|
| Package | `com.moto.resolutionmaster` |
| Version | 3.1 (versionCode 31) |
| Size | 814,027 B |
| SHA-256 | `39114ecf8e7bbcc3e1d66b63e8e79169959f253e18e63b9f582e62a49d362e7b` |
| Min / target SDK | 26 / 34 |
| Signing cert SHA-256 | `49f8ec5349ea1098be287ba9470c90bca702af7987b8017a474da1a8e35c5844` |

## What was translated

839 unique Russian strings across the three places text actually lives in an Android app:

| Layer | Strings | Examples |
|---|---|---|
| `res/values/strings.xml` | 74 | dialogs, toasts, permission text, preset tables |
| `res/layout/*.xml` (`android:text` / `hint`) | 146 unique (160 occurrences) | screen titles, chips, warning blocks |
| `smali` string literals | 614 unique (661 occurrences) | runtime toasts, `String.format` fragments, 111 package descriptions, Magisk `module.prop` + `service.sh` |

Terminology was localized rather than transliterated:

| Russian | English |
|---|---|
| Герцовка | refresh rate |
| Сток | Stock |
| ШИМ / Анти-ШИМ | PWM / anti-PWM |
| Анти-шлейф | anti-black-smearing |
| Экстра-затемнение | Extra dim |
| Плотность | Density |
| СБПэй | SBPay |
| МЧС | civil defense |
| Шторка / тайлы | Quick Settings / tiles |

Details that matter for correctness:

- **Format specifiers preserved** — `%1$s`, `%2$d`, `%d`, `%.0f Гц` → `%.0f Hz`, `%d%%`. A parity
  check over all 839 pairs confirmed no specifier was added, dropped or reordered.
- **Runtime concatenation reflowed** — the app builds messages by gluing fragments
  (`"AOD turns off after "` + `" sec"`, `"Enabled "` + n + `" of "` + m + `" preset packages."`).
  Fragments were translated so the joined result is grammatical English, not translated in isolation.
- **Emoji kept** — including astral-plane emoji, which must be emitted as UTF-16 surrogate pairs
  (`\ud83d\ude80`) in smali. A plain `\u1f680` is parsed as `\u1f68` + `"0"` and silently corrupts the glyph.

## Install

```bash
adb install -r LenovoMotorolovichY70_v3.1_EN.apk
```

- If the **original Russian build** is installed, uninstall it first — the signature differs:
  `adb uninstall com.moto.resolutionmaster`
- This build **upgrades over the v3.0 English build** released earlier with the same key, so no
  uninstall is needed there.

Full functionality needs the same privileges the original requires:

```bash
adb shell pm grant com.moto.resolutionmaster android.permission.WRITE_SECURE_SETTINGS
```

Resolution and refresh-rate switching on Android 14+ additionally need Shizuku or root.

## Verification

See [VERIFICATION.md](VERIFICATION.md) for the full evidence trail. Summary:

- Installed and launched on an Android 14 (x86_64) emulator; all 9 activities opened and scrolled.
- 635 UI text nodes captured via `uiautomator`: **0 Cyrillic characters, 0 crashes/exceptions**.
- Resource table identical to the untranslated build in structure
  (13 colors / 23 drawables / 167 ids / 11 layouts / 82 strings / 1 style).
- `AndroidManifest.xml` content identical to the original (line numbers normalized).
- Behaviour parity control: the untranslated v3.1 was installed on the same emulator and driven
  through the same actions; both builds produced the same dialogs, countdown and rollback, with no
  exceptions on either side.

## Notes on v3.1

The upstream v3.1 removed the Touch / Turbo module: `TouchActivity` is gone from the manifest
(10 activities → 9) and there are no touch-related strings left in the APK. That is an upstream
change, not something removed by this translation.

## Repository layout

```
apk/                       signed, installable APK
translation/en.json        ru → en map (839 entries) — drop-in for future versions
tools/apply_translations.py  applies the map to an apktool-decoded tree
tools/verify_screens.py    launches every activity, dumps UI text, flags Cyrillic / crashes
```

To localize a future release:

```bash
apktool d -f LenovoMotorolovichY70_v3.2.apk -o dec
python3 tools/apply_translations.py dec     # reports any string not in the map
apktool b dec -o unsigned.apk
zipalign -p -f 4 unsigned.apk aligned.apk
apksigner sign --ks keystore.jks --out app_EN.apk aligned.apk
```

Only strings missing from `translation/en.json` need new work — v3.1 needed 3.

## Credits & disclaimer

- Original app: **nik.reneyj** (4PDA). NFC routing fix: **stepchansky**.
- This repository is an unofficial fan localization. Not affiliated with the original author,
  Motorola or Lenovo. No code was added or removed — only text literals were replaced.
- The APK is re-signed with a locally generated key, so it cannot be installed over a build signed
  by the original author.
- Use at your own risk. These tools change display resolution, refresh rate and system settings.
