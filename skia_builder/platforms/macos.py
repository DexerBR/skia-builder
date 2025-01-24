from skia_builder.platforms.common import CommonPlatformManager, HostPlatform
from skia_builder.utils import Logger, run_command


class MacOSPlatformManager(CommonPlatformManager):
    HOST_PLATFORM = TARGET_PLATFORM = HostPlatform.MACOS
    SUPPORTED_ARCHITECTURES = TARGET_PLATFORM.supported_architectures
