import sys

from skia_builder.platforms.common import CommonPlatformManager, HostPlatform
from skia_builder.utils import Logger, run_command


class WindowsPlatformManager(CommonPlatformManager):
    HOST_PLATFORM = TARGET_PLATFORM = HostPlatform.WINDOWS
    SUPPORTED_ARCHITECTURES = TARGET_PLATFORM.supported_architectures

    @classmethod
    def setup_env(cls, skip_llvm_instalation=False):
        if skip_llvm_instalation:
            Logger.info("Skipping LLVM installation")
        else:
            returncode = run_command(
                ["choco", "--version"], "Verifying Chocolatey Installation", exit_on_error=False
            )
            if returncode == 0:
                run_command(
                    ["choco", "install", "llvm", "-y"],
                    "Installing LLVM",
                )
            else:
                Logger.error(
                    "Chocolatey is not installed, and the installation of LLVM cannot proceed. "
                    "Please install Chocolatey or manually install LLVM from "
                    "'https://github.com/llvm/llvm-project/releases'"
                )
                sys.exit(1)

        cls._setup_env()
