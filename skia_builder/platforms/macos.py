from skia_builder.platforms.common import CommonPlatformManager, HostPlatform


class MacOSPlatformManager(CommonPlatformManager):
    HOST_PLATFORM = TARGET_PLATFORM = HostPlatform.MACOS
    SUPPORTED_ARCHITECTURES = TARGET_PLATFORM.supported_architectures
