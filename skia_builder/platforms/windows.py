import sys

from skia_builder.platforms import execute_build, setup_env_common
from skia_builder.utils import Logger, run_command

SUPPORTED_ARCHITECTURES = "x64"


def setup_env(skip_llvm_instalation):
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

    setup_env_common()


def build(target_cpu, custom_build_args=None, override_build_args=None, archive_output=False):
    execute_build(target_cpu, "windows", custom_build_args, override_build_args, archive_output)
