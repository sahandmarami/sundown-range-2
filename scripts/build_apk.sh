#!/bin/bash
export ANDROID_HOME=/home/z/android-sdk
export ANDROID_SDK_ROOT=/home/z/android-sdk
export PATH="$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools:$PATH"
export GRADLE_OPTS="-Dorg.gradle.daemon=false -Dorg.gradle.jvmargs=-Xmx1536m -Dorg.gradle.parallel=false -Dorg.gradle.caching=true"
cd /home/z/my-project/apk-project/android
echo "[$(date)] Starting build..." > /tmp/build.log
./gradlew assembleDebug --no-daemon --no-build-cache --configure-on-demand >> /tmp/build.log 2>&1
EXIT=$?
echo "[$(date)] Build finished with exit code $EXIT" >> /tmp/build.log
if [ $EXIT -eq 0 ]; then
  cp app/build/outputs/apk/debug/app-debug.apk /home/z/my-project/download/sundown-range-2.apk
  echo "[$(date)] APK copied to download dir" >> /tmp/build.log
fi
