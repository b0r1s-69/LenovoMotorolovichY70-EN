#!/usr/bin/env bash
# Builds classes2.dex for the charge-limit feature.
#
# The feature ships as a SECOND dex (classes2.dex) instead of being merged into classes.dex:
#   - the original, translated dex is never rewritten, so a mistake here cannot corrupt the app
#   - Android 5.0+ (minSdk 26 here) loads every classesN.dex in the APK automatically
#   - PowerActivity reaches the bridge with one added invoke-static; both classes live on the
#     same PathClassLoader, so no reflection is needed at the call site
#
# Usage: feature/build.sh <decoded-apk-dir> <output-apk>
#   apktool d -f app.apk -o dec && feature/build.sh dec out.apk
set -euo pipefail

SDK="${ANDROID_SDK_ROOT:-$HOME/android-sdk}"
AJ="$SDK/platforms/android-34/android.jar"
BT="$(ls -d "$SDK"/build-tools/* | sort -V | tail -1)"
JAVAC="${JAVA_HOME:-$(dirname "$(dirname "$(readlink -f "$(command -v java)")")")}/bin/javac"
HERE="$(cd "$(dirname "$0")" && pwd)"
DEC="${1:-dec}"
OUT="${2:-out.apk}"
WORK="$(mktemp -d)"

# 24 or 34 both work; d8 from build-tools 34 crashes on anonymous inner classes compiled by
# javac 21 ("NullPointerException: String.length()"), build-tools 36 or newer is required.
echo "== javac"
"$JAVAC" --release 8 -g:none -classpath "$AJ" -d "$WORK/classes" "$HERE"/src/com/moto/resolutionmaster/*.java 2>&1 | grep -v '^Note:' || true

echo "== d8"
"$BT/d8" --min-api 26 --lib "$AJ" --output "$WORK/classes2.zip" \
    "$WORK"/classes/com/moto/resolutionmaster/*.class
unzip -o -q "$WORK/classes2.zip" -d "$WORK/dex"

echo "== apktool build"
apktool b "$DEC" -o "$WORK/staged.apk"

echo "== add classes2.dex"
cp "$WORK/dex/classes.dex" "$WORK/classes2.dex"
(cd "$WORK" && zip -q -j staged.apk classes2.dex)

echo "== align + sign"
zipalign -p -f 4 "$WORK/staged.apk" "$WORK/aligned.apk"
: "${KS:?set KS to your keystore path}"
apksigner sign --ks "$KS" --ks-pass "pass:${KS_PASS:-android}" --key-pass "pass:${KEY_PASS:-android}" \
    --ks-key-alias "${KS_ALIAS:-appkey}" --v1-signing-enabled true --v2-signing-enabled true \
    --v3-signing-enabled true --out "$OUT" "$WORK/aligned.apk"
apksigner verify "$OUT"
echo "OK -> $OUT"
