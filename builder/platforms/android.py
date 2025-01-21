import os

from builder.platforms import execute_build
from builder.utils import run_command
from builder.versions import ANDROID_NDK

SUPPORTED_ARCHITECTURES = ("arm", "arm64", "x64", "x86")


def setup_env():
    os.makedirs("Android_NDK", exist_ok=True)

    run_command(
        [
            "curl",
            "-o",
            f"Android_NDK/{ANDROID_NDK}-windows.zip",
            f"https://dl.google.com/android/repository/{ANDROID_NDK}-windows.zip",
        ],
        "Downloading Android NDK",
    )

    run_command(
        [
            "powershell",
            "-Command",
            f"Expand-Archive -Path 'Android_NDK/{ANDROID_NDK}-windows.zip' -DestinationPath 'Android_NDK'",
        ],
        "Extracting Android NDK",
    )


def build(target_cpu, custom_build_args=None, override_build_args=None, archive_output=False):
    execute_build(target_cpu, "android", custom_build_args, override_build_args, archive_output)
