# LenovoMotorolovichY70 — English translation (v3.1)

Unofficial full English localization of **LenovoMotorolovichY70** (`com.moto.resolutionmaster`),
a display / power / debloat toolkit for the **Lenovo Legion Y70** and **Moto Edge 70 Max**.
The original app is Russian-only; this build ships the same code with every user-visible
string translated to English.

**Download:** see the [Releases](https://github.com/b0r1s-69/LenovoMotorolovichY70-EN/releases) page.

| | |
|---|---|
| Package | `com.moto.resolutionmaster` |
| Version | 3.2 (versionCode 32) |
| Size | 830,493 B |
| SHA-256 | `8bf07b581d2843056b1c0a0f4d99256ef25041041b3644b589930cf438f9e283` |
| Min / target SDK | 26 / 34 |
| Signing cert SHA-256 | `49f8ec5349ea1098be287ba9470c90bca702af7987b8017a474da1a8e35c5844` |

## What was translated

839 unique Russian strings across the three places text actually lives in an Android app:

| Layer | Strings | Examples |
|---|---|---|
| `res/values/strings.xml` | 74 | dialogs, toasts, permission text, preset tables |
| `res/layout/*.xml` (`android:text` / `hint`) | 146 unique (160 occurrences) | screen titles, chips, warning blocks |
| `smali` string literals | 616 unique (668 occurrences) | runtime toasts, `String.format` fragments, 111 package descriptions, Magisk `module.prop` + `service.sh` |

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

## Battery charge limit — added here, not upstream

Version 3.2 has no charge limit. This build adds one to the **Power and Bypass Charging** screen:
presets Off / 80% / 85% / 90% / 95%, a status line that reports what is actually happening, and
remembered state. It drives the charging circuit through vendor sysfs nodes, so it needs root.

It ships as a second dex (`classes2.dex`) and one added `invoke-static` in `PowerActivity`, so the
translated original code is never rewritten. Details, mechanism and limitations:
[feature/README.md](feature/README.md).

Unplugged or unrooted, the card degrades honestly — it shows `root required to enforce` and the
footer points at Moto Battery Care, which caps charging at 80% without root.

## Install

```bash
adb install -r LenovoMotorolovichY70_v3.2_EN.apk
```

- If the **original Russian build** is installed, uninstall it first — the signature differs:
  `adb uninstall com.moto.resolutionmaster`
- Every English build here shares one key, so 3.1 → 3.2 is a normal update with no uninstall.

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

## Upstream changes carried in 3.2

- Bypass charging moved to a root-gated path: `moto_extend_service` is signature-protected, so the
  app now says so instead of failing silently.
- All sub-activities became `exported="false"` (they were exported in 3.1) — the screens are only
  reachable through the menu cards now.
- Two strings reworded; everything else was already covered by the existing map.

## Notes on v3.1

The upstream v3.1 removed the Touch / Turbo module: `TouchActivity` is gone from the manifest
(10 activities → 9) and there are no touch-related strings left in the APK. That is an upstream
change, not something removed by this translation.

## Repository layout

```
apk/                       signed, installable APKs
translation/en.json        ru → en map (841 entries) — drop-in for future versions
tools/apply_translations.py  applies the map to an apktool-decoded tree
tools/verify_screens.py    launches every activity, dumps UI text, flags Cyrillic / crashes
feature/                   the added charge-limit card: Java sources, injection script, build
```

To localize a future release:

```bash
apktool d -f LenovoMotorolovichY70_v3.2.apk -o dec
python3 tools/apply_translations.py dec     # reports any string not in the map
apktool b dec -o unsigned.apk
zipalign -p -f 4 unsigned.apk aligned.apk
apksigner sign --ks keystore.jks --out app_EN.apk aligned.apk
```

Only strings missing from `translation/en.json` need new work — v3.2 needed 2, v3.1 needed 3.

## Credits & disclaimer

- Original app: **nik.reneyj** (4PDA). NFC routing fix: **stepchansky**.
- This repository is an unofficial fan localization. Not affiliated with the original author,
  Motorola or Lenovo. No code was added or removed — only text literals were replaced.
- The APK is re-signed with a locally generated key, so it cannot be installed over a build signed
  by the original author.
- Use at your own risk. These tools change display resolution, refresh rate and system settings.
