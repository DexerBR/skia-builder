import os

from builder.config import get_build_args, parse_override_build_args
from builder.utils import Logger, archive_build_output, run_command, store_includes


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

    gn_executable = os.path.join(
        os.getcwd(),
        "skia",
        "bin",
        f"gn{'.exe' if platform == 'windows' else ''}",
    )
    ninja_executable = os.path.join(
        os.getcwd(),
        "depot_tools",
        f"ninja{'.bat' if platform == 'windows' else ''}",
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
            platform=platform,
            output_dir=output_dir,
        )
