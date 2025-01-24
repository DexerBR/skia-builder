from skia_builder.platforms.common import CommonPlatformManager, HostPlatform
from skia_builder.utils import Logger, run_command


class LinuxPlatformManager(CommonPlatformManager):
    HOST_PLATFORM = TARGET_PLATFORM = HostPlatform.LINUX
    SUPPORTED_ARCHITECTURES = TARGET_PLATFORM.supported_architectures

    @classmethod
    def setup_env(cls, skip_llvm_instalation=False):
        if skip_llvm_instalation:
            Logger.info("Skipping LLVM installation")
        else:
            run_command(
                ["sudo", "apt-get", "update"],
                "Updating package lists",
            )
            run_command(
                ["wget", "https://apt.llvm.org/llvm.sh", "-O", "/tmp/llvm.sh"],
                "Downloading LLVM installation script",
            )
            run_command(
                ["sudo", "chmod", "+x", "/tmp/llvm.sh"],
                "Making LLVM installation script executable",
            )
            run_command(
                ["sudo", "bash", "/tmp/llvm.sh"],
                "Running LLVM installation script",
            )
            run_command(
                ["echo", "export PATH=/usr/lib/llvm-18/bin:$PATH", ">>", "~/.bashrc"],
                "Adding LLVM to PATH",
            )
            run_command(
                ["bash", "-i", "-c", "source ~/.bashrc"],
                "Reloading .bashrc to apply PATH changes",
            )
            run_command(
                ["clang", "--version"],
                "Verifying clang installation",
            )

        cls._setup_env()
