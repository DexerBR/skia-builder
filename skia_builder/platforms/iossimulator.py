from skia_builder.platforms.common import CommonSubPlatformManager, SubPlatform


class IOSSimulatorPlatformManager(CommonSubPlatformManager):
    HOST_PLATFORMS_ENV_SETUP = {
        "Linux": None,
        "Windows": None,
        "macOS": CommonSubPlatformManager.noop,
    }
    TARGET_PLATFORM = SubPlatform.IOS_SIMULATOR
    HOST_PLATFORM = TARGET_PLATFORM.host_platform
    SUPPORTED_ARCHITECTURES = TARGET_PLATFORM.supported_architectures
