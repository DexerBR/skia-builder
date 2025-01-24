import platform
import argparse
import sys

from skia_builder.config import parse_custom_build_args
from skia_builder.platforms import (
    android,
    ios,
    iossimulator,
    linux,
    macos,
    windows,
)


PLATFORM_MANAGERS = {
    "Android": android.AndroidPlatformManager,
    "iOS": ios.IOSPlatformManager,
    "iOSSimulator": iossimulator.IOSSimulatorPlatformManager,
    "Linux": linux.LinuxPlatformManager,
    "macOS": macos.MacOSPlatformManager,
    "Windows": windows.WindowsPlatformManager,
}


def get_supported_architectures(target_platform):
    manager = PLATFORM_MANAGERS.get(target_platform)
    if manager is None:
        raise ValueError(f"Unsupported platform: {target_platform}")
    return manager.SUPPORTED_ARCHITECTURES


def setup_env(host_platform, sub_env=None, skip_llvm_instalation=False):
    # Use sub_env if provided, otherwise default to the detected platform
    target_platform = sub_env if sub_env else host_platform

    manager = PLATFORM_MANAGERS.get(target_platform)
    if manager is None:
        print(f"Unsupported target platform: {target_platform}")
        sys.exit(1)

    manager.setup_env(skip_llvm_instalation)


def build(
    host_platform,
    target_cpu,
    custom_build_args,
    override_build_args,
    archive_build_output,
    sub_env=None,
):
    # Use sub_env if provided, otherwise default to the detected platform
    target_platform = sub_env if sub_env else host_platform

    manager = PLATFORM_MANAGERS.get(target_platform)
    if manager is None:
        print(f"Unsupported target platform: {target_platform}")
        sys.exit(1)

    manager.build(target_cpu, custom_build_args, override_build_args, archive_build_output)


def main():
    parser = argparse.ArgumentParser(prog="skia-builder", description="Skia Builder Script")
    subparsers = parser.add_subparsers(dest="command")

    # setup-env subcommand
    setup_env_parser = subparsers.add_parser("setup-env", help="Set up the environment")
    setup_env_parser.add_argument(
        "--sub-env",
        type=str,
        choices=["Android", "iOS", "iOSSimulator"],
        help="Sub-environment to configure (e.g., Android, iOS)",
    )
    setup_env_parser.add_argument(
        "--skip-llvm-instalation",
        action="store_true",
        help="Skip the installation of LLVM during environment setup",
    )
    setup_env_parser.set_defaults(func=setup_env)

    # build subcommand
    build_parser = subparsers.add_parser("build", help="Builds the skia binaries")
    build_parser.add_argument(
        "--sub-env",
        type=str,
        choices=["Android", "iOS", "iOSSimulator"],
        help="Sub-environment to build (e.g., Android, iOS)",
    )
    build_parser.add_argument(
        "--target-cpu", type=str, help="Target CPU architecture (e.g., arm, arm64, x86, x64)"
    )
    build_parser.add_argument(
        "--custom-build-args", type=str, help="Custom arguments for the build configuration"
    )
    build_parser.add_argument(
        "--override-build-args",
        type=str,
        help=(
            "Arguments to selectively override specific values in the default or custom build configuration"
        ),
    )
    build_parser.add_argument(
        "--archive", action="store_true", help="Archive the build output after compilation"
    )
    build_parser.set_defaults(func=build)

    args = parser.parse_args()
    current_platform = "macOS" if platform.system() == "Darwin" else platform.system()

    if args.command == "setup-env":
        setup_env(current_platform, args.sub_env, args.skip_llvm_instalation)

    elif args.command == "build":
        if not args.target_cpu:
            print("Error: --target-cpu must be specified for the build command.")
            sys.exit(1)

        # Validate if target CPU is supported
        supported_architectures = get_supported_architectures(
            args.sub_env if args.sub_env else current_platform
        )
        if args.target_cpu not in supported_architectures:
            print(
                f"Unsupported CPU architecture for {args.sub_env or current_platform}: {args.target_cpu}. "
                f"Supported architectures are: {', '.join(supported_architectures)}"
            )
            sys.exit(1)

        # Parse custom build arguments if provided
        custom_build_args, override_build_args = (
            (parse_custom_build_args(arg) if arg else {})
            for arg in [args.custom_build_args, args.override_build_args]
        )

        build(
            current_platform,
            args.target_cpu,
            custom_build_args,
            override_build_args,
            args.archive,
            args.sub_env,
        )

    else:
        print(f"Unsupported command: {args.command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
