import os

from builder.config import get_build_args
from builder.utils import Logger, archive_build_output, run_command, store_includes
from builder.versions import ANDROID_NDK

SUPPORTED_ARCHITECTURES = ("arm", "arm64", "x64", "x86")


def setup_env():
    os.makedirs("Android_NDK", exist_ok=True)

    # Download Android NDK
    run_command(
        [
            "curl",
            "-o",
            f"Android_NDK/{ANDROID_NDK}-windows.zip",
            f"https://dl.google.com/android/repository/{ANDROID_NDK}-windows.zip",
        ],
        "Downloading Android NDK",
    )

    # Unzip Android NDK
    run_command(
        [
            "powershell",
            "-Command",
            f"Expand-Archive -Path 'Android_NDK/{ANDROID_NDK}-windows.zip' -DestinationPath 'Android_NDK'",
        ],
        "Extracting Android NDK",
    )


def build(target_cpu, custom_build_args=None, archive_output=False):
    Logger.info(f"Building with {'custom' if custom_build_args else 'default'} " "arguments.")
    Logger.info(
        "Archiving build output." if archive_output else "Build output will not be archived."
    )

    skia_path = os.path.join(os.getcwd(), "skia")
    build_target = f"android-{target_cpu}"
    output_dir = os.path.join("output", build_target)

    if archive_output:
        store_includes(skia_path, output_dir=output_dir)

    build_args = custom_build_args or get_build_args(build_target)
    run_command(
        [
            "skia/bin/gn.exe",
            "gen",
            f"out/{build_target}",
            f"--args={build_args}",
        ],
        "Generating Build Files",
        cwd=skia_path,
    )

    run_command(
        [
            os.path.join(os.getcwd(), "depot_tools", "ninja.bat"),
            "-C",
            f"out/{build_target}",
        ],
        f"Building Skia for {build_target}",
        cwd=skia_path,
    )

    if archive_output:
        archive_build_output(
            os.path.join(skia_path, "out", f"{build_target}"),
            platform="Android",
            output_dir=output_dir,
        )
