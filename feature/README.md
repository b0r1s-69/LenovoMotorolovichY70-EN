# Battery charge limit — an added feature, not upstream

> **This does not exist in the original app.** v3.1 and earlier had no charge limit; the upstream
> author did not ship this. It was requested for this English build and lives entirely in
> `classes2.dex`, so the translated original code is untouched.

## What it does

The **Power and Bypass Charging** screen gains a *Battery charge limit* card:

- presets **Off / 80% / 85% / 90% / 95%**
- a status line that reports what is actually happening, not what was requested:
  `Limit: 80% • hardware node active • battery 74%`,
  `Limit: 80% • enforcing • battery 74%`,
  `Limit: 80% • root required to enforce`,
  `Limit: 80% • armed, no writable node`,
  `Limit: Off • charging to 100%`
- the selection is remembered in `SharedPreferences` even when it cannot be enforced yet

## How it controls charging

Two mechanisms, tried in order:

1. **Level node** — vendor nodes that take a percentage and stop the charge in hardware:
   `charge_stop_level`, `charge_control_limit`, `battery_charge_limit` under
   `/sys/class/power_supply/battery/`. If one accepts the value, it is read back to confirm and
   no background work is needed.
2. **Toggle node** — boolean nodes (`battery_charging_enabled`, `charging_enabled`,
   `charge_disable`, `input_suspend`, `batt_slate_mode`). `ChargeLimitService` then runs a
   foreground service that stops the charge at the limit and resumes it 3% below
   (`HYSTERESIS`), so the charger is not toggled on every percentage point. Unplugging always
   re-enables charging so the next session starts clean.

Every shell command goes through the app's own `ShellHelper.runCommand` / `runCommandWithOutput`,
which already implements the root → Shizuku chain and its logging. This feature adds no second
privileged channel and no new permission.

Node detection uses `test -w <node> && echo y`; writes are `echo <value> > <node>` and are verified
by reading the node back. The winning node is cached in preferences so the probe cost is paid once.

## Why root

`/sys/class/power_supply/*` nodes are owned by `system`/`root`. The shell uid that Shizuku provides
cannot write them on a stock ROM, so the card reports *root required* instead of pretending to work.
On a rooted Legion Y70 / Moto Edge 70 Max the enforcement path runs.

Without root the card is still useful: the footer points at **Moto Battery Care**, which caps
charging at 80% through Motorola's own system service (the app already had a button for it).

## Files

```
feature/src/com/moto/resolutionmaster/ChargeLimit.java         prefs, node probing, command building
feature/src/com/moto/resolutionmaster/ChargeLimitService.java  foreground service, hysteresis, notification
feature/src/com/moto/resolutionmaster/ChargeLimitBridge.java   view binding by name, status rendering
feature/inject_card.py                                         adds the card, strings, manifest entry and the one-line wiring
feature/build.sh                                               javac → d8 → classes2.dex → align → sign
```

## Build

```bash
apktool d -f LenovoMotorolovichY70_v3.2.apk -o dec
python3 tools/apply_translations.py dec      # English strings
python3 feature/inject_card.py               # card + strings + manifest + PowerActivity wiring
KS=~/keystore.jks feature/build.sh dec app_EN.apk
```

`inject_card.py` is idempotent: every block is guarded, so re-running it on an already-patched tree
does nothing.

## Verification performed

| Check | Result |
|---|---|
| card renders in the Power screen | yes — Off / 80 / 85 / 90 / 95 buttons, Root badge, footer |
| taps wired | 80% → `Limit: 80% • root required to enforce • battery 100%`, 90% → same with 90, Off → `Limit: Off` |
| selection persists across re-render | yes (read back from preferences) |
| crashes while tapping | none in logcat |
| shell semantics | `test -w`, `echo 0 > node`, `cat` read-back validated on a local POSIX shell |
| resource table | original 82 strings / 167 ids + 10 strings / 7 ids added, nothing removed |
| manifest | original plus exactly one `specialUse` foreground service |

**Not verified:** actual enforcement on hardware. The emulator exposes no writable charging node
(`/sys/class/power_supply/battery/` there has `capacity`, `status`, `temp`, … and no
`*charging_enabled*` or `charge_*limit*`), and an app on a stock emulator image cannot obtain root.
The enforcement loop, hysteresis and notification were therefore exercised only as far as the UI
state machine; the first real run has to happen on the phone.
