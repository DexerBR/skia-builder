from skia_builder.platforms.common import CommonSubPlatformManager, SubPlatform
from skia_builder.platforms.macos import MacOSPlatformManager


class IOSPlatformManager(CommonSubPlatformManager):
    @staticmethod
    def _setup_env_host_macos(skip_llvm_instalation):
        MacOSPlatformManager.setup_env(skip_llvm_instalation)

    HOST_PLATFORMS_ENV_SETUP = {
        "Linux": None,
        "Windows": None,
        "macOS": _setup_env_host_macos,
    }
    TARGET_PLATFORM = SubPlatform.IOS
    HOST_PLATFORM = TARGET_PLATFORM.host_platform
    SUPPORTED_ARCHITECTURES = TARGET_PLATFORM.supported_architectures
