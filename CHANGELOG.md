# Changelog

## v3.2-en — 2026-11-27

English localization of LenovoMotorolovichY70 **3.2** (versionCode 32), plus one added feature.

Translation:
- 2 new strings (`Требуется Root или системный режим`, the root-gated bypass explanation); the other
  616 smali / 146 layout / 74 resource strings were already covered by the map.
- Map grown to 841 entries.

Added feature (not upstream): **battery charge limit** in Power and Bypass Charging —
Off / 80% / 85% / 90% / 95%, vendor sysfs level-node first, toggle-node service with 3% hysteresis
as fallback, status line that reports the real state, selection persisted. Ships as
`classes2.dex`; the original dex is untouched. Requires root; see `feature/README.md`.

Upstream changes carried in 3.2:
- Bypass charging is now root-gated (`moto_extend_service` is signature-protected).
- Every sub-activity is `exported="false"` now, so screens are menu-only.

## v3.1-en — 2026-11-24

English localization of LenovoMotorolovichY70 **3.1** (versionCode 31).

- 839 Russian strings translated: 74 resources, 146 layout attributes (160 occurrences),
  614 smali literals (661 occurrences).
- Only 3 strings were new relative to v3.0; the rest of the map carried over unchanged:
  `fps_144_desc`, `fps_auto_desc`, `section_fps_desc` (reworded upstream).
- Format specifiers, run-time concatenation fragments and emoji (as UTF-16 surrogate pairs)
  preserved.
- Signed so it upgrades over the v3.0 English build without an uninstall.

### Upstream changes carried in 3.1

- Touch / Turbo module removed: `TouchActivity` deleted (10 activities → 9), all touch-related
  strings gone.
- Refresh-rate and resolution descriptions reworded.

## v3.0-en — earlier

Initial English localization of LenovoMotorolovichY70 3.0. Not published in this repository.
