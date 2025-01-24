import os

from skia_builder.platforms.common import CommonSubPlatformManager, SubPlatform
from skia_builder.platforms.windows import WindowsPlatformManager
from skia_builder.utils import run_command
from skia_builder.versions import ANDROID_NDK


class AndroidPlatformManager(CommonSubPlatformManager):
    @staticmethod
    def _setup_env_host_windows(skip_llvm_instalation):
        WindowsPlatformManager.setup_env(skip_llvm_instalation)

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

    HOST_PLATFORMS_ENV_SETUP = {
        "Linux": None,
        "macOS": None,
        "Windows": _setup_env_host_windows,
    }
    TARGET_PLATFORM = SubPlatform.ANDROID
    HOST_PLATFORM = TARGET_PLATFORM.host_platform
    SUPPORTED_ARCHITECTURES = TARGET_PLATFORM.supported_architectures
