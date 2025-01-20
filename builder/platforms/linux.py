import os

from builder.platforms import execute_build
from builder.utils import run_command
from builder.versions import SKIA_VERSION

SUPPORTED_ARCHITECTURES = ("arm64", "x64")


def setup_env():
    # Update package lists
    run_command(
        ["sudo", "apt-get", "update"],
        "Updating package lists",
    )

    # FIXME: update to make it install the lastest release
    # Install Bazelisk
    run_command(
        [
            "sudo",
            "wget",
            "https://github.com/bazelbuild/bazelisk/releases/download/v1.25.0/bazelisk-linux-amd64",
            "-O",
            "/usr/local/bin/bazelisk",
        ],
        "Downloading Bazelisk",
    )
    # run_command(
    #     ["sudo", "chmod", "+x", "/usr/local/bin/bazelisk"],
    #     "Making Bazelisk executable"
    # )  # TODO: Investigate why this is required on the local machine but not in GitHub Actions
    run_command(["bazelisk", "version"], "Testing Bazelisk installation")

    # Install LLVM
    run_command(
        ["wget", "https://apt.llvm.org/llvm.sh", "-O", "/tmp/llvm.sh"],
        "Downloading LLVM installation script",
    )
    run_command(
        ["sudo", "chmod", "+x", "/tmp/llvm.sh"], "Making LLVM installation script executable"
    )
    run_command(["sudo", "bash", "/tmp/llvm.sh"], "Running LLVM installation script")
    # run_command(
    #     ["echo", 'export PATH=/usr/lib/llvm-18/bin:$PATH', ">>", "~/.bashrc"],
    #     "Adding LLVM to PATH"
    # )
    # run_command(
    #     ["bash", "-c", "source ~/.bashrc"],
    #     "Reloading bashrc to apply changes"
    # )
    # run_command(
    #     ["which", "clang"],
    #     "Check clang version"
    # )
    # run_command(
    #     ["clang", "--version"],
    #     "Check clang version"
    # )

    # Clone depot_tools
    run_command(
        [
            "git",
            "clone",
            "https://chromium.googlesource.com/chromium/tools/depot_tools.git",
        ],
        "Cloning depot_tools",
    )

    # Verify Depot Tools Installation
    run_command(
        [os.path.join(os.getcwd(), "depot_tools", "gclient")],
        "Verifying Depot Tools Installation",
    )

    # Clone Skia Repository and Fetch Dependencies
    run_command(
        ["git", "clone", "https://skia.googlesource.com/skia.git"],
        "Cloning Skia Repository",
    )

    skia_path = os.path.join(os.getcwd(), "skia")

    # Fetch and checkout to the specific branch (Chrome/SKIA_VERSION)
    run_command(
        ["git", "fetch", "-v"],
        "Fetching Skia Repository",
        cwd=skia_path,
    )
    run_command(
        ["git", "checkout", f"origin/chrome/{SKIA_VERSION}"],
        f"Checking out Chrome/{SKIA_VERSION} branch",
        cwd=skia_path,
    )

    # Install Skia extra dependencies
    run_command(
        [os.path.join(os.getcwd(), "skia", "tools", "install_dependencies.sh"), "-y"],
        "Install Skia Extra Dependencies",
        cwd=skia_path,
    )

    # Sync Skia dependencies using git-sync-deps script
    run_command(
        ["python3", "tools/git-sync-deps"],
        "Syncing Skia Dependencies",
        cwd=skia_path,
    )

    # Fetch Ninja binary for Skia
    run_command(
        ["python3", "bin/fetch-ninja"],
        "Fetching Ninja for Skia",
        cwd=skia_path,
    )


def build(target_cpu, custom_build_args=None, override_build_args=None, archive_output=False):
    execute_build(target_cpu, "linux", custom_build_args, override_build_args, archive_output)
