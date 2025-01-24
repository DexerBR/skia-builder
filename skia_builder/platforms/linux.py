from skia_builder.platforms import execute_build, setup_env_common
from skia_builder.utils import Logger, run_command

SUPPORTED_ARCHITECTURES = ("arm64", "x64")


def setup_env(skip_llvm_instalation):
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

    setup_env_common(install_skia_extra_dependencies=True)


def build(target_cpu, custom_build_args=None, override_build_args=None, archive_output=False):
    execute_build(target_cpu, "linux", custom_build_args, override_build_args, archive_output)
