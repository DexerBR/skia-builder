import os

ANDROID_NDK_VERSION = os.getenv("SKIA_ANDROID_NDK_VERSION", "r27d")
ANDROID_NDK = f"android-ndk-{ANDROID_NDK_VERSION}"
SKIA_VERSION = os.getenv("SKIA_VERSION", "m145")

# Minimum supported versions
MIN_ANDROID_NDK_VERSION = "r27d"
MIN_SKIA_VERSION = "m140"
