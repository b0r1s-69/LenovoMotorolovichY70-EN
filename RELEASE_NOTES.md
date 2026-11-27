## Full English build of LenovoMotorolovichY70 3.2 (unofficial) — with an added charge limit

The app ships Russian-only. This build keeps the original code and replaces every user-visible
string with English, then adds one feature the original does not have: a **battery charge limit** in
the Power and Bypass Charging screen.

**Asset:** `LenovoMotorolovichY70_v3.2_EN.apk`

```
size      830,493 bytes
sha256    8bf07b581d2843056b1c0a0f4d99256ef25041041b3644b589930cf438f9e283
package   com.moto.resolutionmaster
version   3.2 (versionCode 32)
dex       classes.dex + classes2.dex (the feature)
cert      SHA-256 49f8ec5349ea1098be287ba9470c90bca702af7987b8017a474da1a8e35c5844
```

### Install

```bash
adb install -r LenovoMotorolovichY70_v3.2_EN.apk
adb shell pm grant com.moto.resolutionmaster android.permission.WRITE_SECURE_SETTINGS
```

- From the official Russian build: `adb uninstall com.moto.resolutionmaster` first (different key).
- From the earlier English build: normal update, no uninstall.
- Resolution / refresh-rate switching on Android 14+ still needs Shizuku or root, as upstream.

### Battery charge limit (added, not upstream)

New card in **Power and Bypass Charging**: Off / 80% / 85% / 90% / 95%, a status line that reports
what is really happening (`hardware node active`, `enforcing`, `root required to enforce`,
`armed, no writable node`), and the selection is remembered.

How it works: vendor level nodes first (`charge_stop_level`, `charge_control_limit`,
`battery_charge_limit`) — if one accepts the percentage it is read back and the charge stops in
hardware. Otherwise a foreground service toggles a boolean node
(`battery_charging_enabled` and friends) at the threshold and resumes 3% below it. Unplugging always
re-enables charging.

**Needs root** — those sysfs nodes are system-owned, so Shizuku alone cannot write them. Without
root the card says so instead of pretending, and points at Moto Battery Care (which caps at 80% via
Motorola's own service).

The feature lives in `classes2.dex` and one added call in `PowerActivity`, so the translated
original dex is never rewritten. Sources, mechanism and limits: `feature/README.md`.

### What was translated

841-entry ru → en map; for 3.2 specifically, 2 new strings, 74 resources, 146 layout attributes
(160 occurrences) and 616 smali literals (668 occurrences). Format specifiers preserved exactly,
concatenated message fragments reflowed, emoji kept as UTF-16 surrogate pairs.

### Verification

- 8 menu screens opened and scrolled on Android 14 x86_64: 523 UI text nodes, **0 Cyrillic**,
  **0 crashes**.
- Charge-limit card: taps produce 80% / 90% / Off states, selection persists, no crashes.
- Resource table: nothing removed, +10 strings and +7 ids for the card; manifest: +1 service.
- Full evidence: [VERIFICATION.md](https://github.com/b0r1s-69/LenovoMotorolovichY70-EN/blob/main/VERIFICATION.md).

**Known limitation:** real charge enforcement was not exercised — the emulator has no writable
charging node and no root for the app. First real run has to happen on the phone.

### Upstream changes carried in 3.2

Bypass charging became root-gated (`moto_extend_service` is signature-protected) and every
sub-activity is `exported="false"` now, so screens are menu-only.

### Credits

Original app: **nik.reneyj** (4PDA). NFC routing fix: **stepchansky**.
Unofficial fan localization plus a locally added feature; not affiliated with the original author,
Motorola or Lenovo. Re-signed with a local key.
