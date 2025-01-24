import os
import platform

from skia_builder.config import get_build_args, parse_override_build_args
from skia_builder.utils import Logger, archive_build_output, run_command, store_includes
from skia_builder.versions import SKIA_VERSION


def get_executable_path(*path_parts, executable_name, windows_extension=None):
    """
    Builds a complete path for an executable, using the current working directory as the base.
    Adds the specified extension only on Windows.

    Args:
        *path_parts: Variable-length list of path components (relative to the current directory).
        executable_name: The name of the executable (without the extension).
        windows_extension: Optional extension to add (e.g., '.exe', '.bat') on Windows.
                           No extension is added for non-Windows platforms.

    Returns:
        str: The complete path to the executable, starting from the current working directory.
    """
    if platform.system() == "Windows" and windows_extension:
        executable_name += windows_extension

    return os.path.join(os.getcwd(), *path_parts, executable_name)


def execute_build(
    target_cpu,
    platform,
    custom_build_args=None,
    override_build_args=None,
    archive_output=False,
):
    """
    Build Skia for a specified platform and CPU target.

    Args:
        target_cpu (str): The target CPU architecture (e.g., "arm64", "x64").
        platform (str): The target platform (e.g., "macos", "ios", "iossimulator", "linux", "windows", "android").
        custom_build_args (str): Optional custom build flags.
        archive_output (bool): Whether to archive the build output.
    """
    flags_mode = "custom" if custom_build_args else "default"
    Logger.info(f"Building with {flags_mode} flags.")
    if override_build_args:
        Logger.info(f"Overriding {flags_mode} build flags with: {override_build_args}.")

    Logger.info(
        "Archiving build output." if archive_output else "Build output will not be archived."
    )

    skia_path = os.path.join(os.getcwd(), "skia")
    build_target = f"{platform}-{target_cpu}"
    output_dir = os.path.join("output", build_target)

    if archive_output:
        store_includes(skia_path, output_dir=output_dir)

    build_args = custom_build_args or get_build_args(build_target)
    if override_build_args:
        build_args = parse_override_build_args(build_args, override_build_args)

    gn_executable = get_executable_path(
        "skia",
        "bin",
        executable_name="gn",
        windows_extension=".exe",
    )
    ninja_executable = get_executable_path(
        "depot_tools",
        executable_name="ninja",
        windows_extension=".bat",
    )

    run_command(
        [
            gn_executable,
            "gen",
            f"out/{build_target}",
            f"--args={build_args}",
        ],
        "Generating Build Files",
        cwd=skia_path,
    )

    run_command(
        [
            ninja_executable,
            "-C",
            f"out/{build_target}",
        ],
        f"Building Skia for {build_target}",
        cwd=skia_path,
    )

    if archive_output:
        archive_build_output(
            os.path.join(skia_path, "out", f"{build_target}"),
            platform,
            output_dir=output_dir,
        )


def setup_env_common(install_skia_extra_dependencies=False):
    """
    Configures the Skia environment by cloning repositories, syncing dependencies,
    and optionally installing additional dependencies (specific to Linux/Unix).

    Args:
        install_skia_extra_dependencies (bool): If True, installs extra dependencies
        required for Skia, applicable primarily to Linux/Unix systems.
    """
    run_command(
        [
            "git",
            "clone",
            "https://chromium.googlesource.com/chromium/tools/depot_tools.git",
        ],
        "Cloning depot_tools",
    )

    gclient_executable = get_executable_path(
        "depot_tools",
        executable_name="gclient",
        windows_extension=".bat",
    )
    run_command(
        [gclient_executable],
        "Verifying Depot Tools Installation",
    )

    run_command(
        ["git", "clone", "https://skia.googlesource.com/skia.git"],
        "Cloning Skia Repository",
    )

    skia_path = os.path.join(os.getcwd(), "skia")

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

    if install_skia_extra_dependencies:
        run_command(
            [os.path.join(os.getcwd(), "skia", "tools", "install_dependencies.sh"), "-y"],
            "Install Skia Extra Dependencies",
            cwd=skia_path,
        )

    run_command(
        ["python3", "tools/git-sync-deps"],
        "Syncing Skia Dependencies",
        cwd=skia_path,
    )

    run_command(
        ["python3", "bin/fetch-ninja"],
        "Fetching Ninja binary for Skia",
        cwd=skia_path,
    )
