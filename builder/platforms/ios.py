import os

from builder.config import get_build_args
from builder.utils import (
    Logger,
    archive_build_output,
    run_command,
    store_includes,
)
from builder.versions import SKIA_VERSION


SUPPORTED_ARCHITECTURES = ("arm64")


def setup_env():
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


def build(target_cpu, custom_build_args=None, archive_output=False):
    Logger.info(f"Building with {'custom' if custom_build_args else 'default'} " "arguments.")
    Logger.info(
        "Archiving build output." if archive_output else "Build output will not be archived."
    )

    skia_path = os.path.join(os.getcwd(), "skia")
    build_target = f"ios-{target_cpu}"
    output_dir = os.path.join("output", build_target)

    if archive_output:
        store_includes(skia_path, output_dir=output_dir)

    build_args = custom_build_args or get_build_args(build_target)
    run_command(
        [
            os.path.join(os.getcwd(), "skia", "bin", "gn"),
            "gen",
            f"out/{build_target}",
            f"--args={build_args}",
        ],
        "Generating Build Files",
        cwd=skia_path,
    )

    run_command(
        [
            os.path.join(os.getcwd(), "depot_tools", "ninja"),
            "-C",
            f"out/{build_target}",
        ],
        f"Building Skia for {build_target}",
        cwd=skia_path,
    )

    if archive_output:
        archive_build_output(
            os.path.join(skia_path, "out", f"{build_target}"),
            output_dir=output_dir,
        )
