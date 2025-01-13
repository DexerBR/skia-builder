import platform
import argparse
import sys

from builder.config import parse_custom_build_args
from builder.platforms import (
    android,
    ios,
    iossimulator,
    linux,
    darwin,
    windows,
)


def get_supported_architectures(platform):
    arch_map = {
        "Android": android.SUPPORTED_ARCHITECTURES,
        "iOS": ios.SUPPORTED_ARCHITECTURES,
        "iOSSimulator": iossimulator.SUPPORTED_ARCHITECTURES,
        "Linux": linux.SUPPORTED_ARCHITECTURES,
        "Darwin": darwin.SUPPORTED_ARCHITECTURES,
        "Windows": windows.SUPPORTED_ARCHITECTURES,
    }

    archs = arch_map.get(platform)
    return archs


def setup_env(platform, sub_env=None):
    platform_actions = {
        "Android": android.setup_env,
        "iOS": ios.setup_env,
        "iOSSimulator": iossimulator.setup_env,
        "Linux": linux.setup_env,
        "Darwin": darwin.setup_env,
        "Windows": windows.setup_env,
    }

    # Retrieve the setup action for the given platform
    action = platform_actions.get(platform)

    if action:
        # Set up the main platform environment
        action()

        # If a sub-environment is provided, set it up after the platform setup
        if sub_env:
            sub_env_action = platform_actions.get(sub_env)
            if sub_env_action:
                sub_env_action()  # Set up the sub-environment
            else:
                print(f"Unknown sub-environment: {sub_env}")
                sys.exit(1)
    else:
        print(f"Unknown platform: {platform}")
        sys.exit(1)


def build(platform, target_cpu, custom_build_args, archive_build_output, sub_env=None):
    platform_actions = {
        "Android": android.build,
        "iOS": ios.build,
        "iOSSimulator": iossimulator.build,
        "Linux": linux.build,
        "Darwin": darwin.build,
        "Windows": windows.build,
    }

    # Use sub_env if provided, otherwise default to the detected platform
    target_platform = sub_env if sub_env else platform

    action = platform_actions.get(target_platform)
    if action:
        action(target_cpu, custom_build_args, archive_build_output)
    else:
        print(f"Unknown platform: {target_platform}")
        sys.exit(1)


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
        "--archive", action="store_true", help="Archive the build output after compilation"
    )
    build_parser.set_defaults(func=build)

    args = parser.parse_args()
    current_platform = platform.system()

    if args.command == "setup-env":
        setup_env(current_platform, args.sub_env)

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
        custom_build_args = (
            parse_custom_build_args(args.custom_build_args) if args.custom_build_args else {}
        )

        build(current_platform, args.target_cpu, custom_build_args, args.archive, args.sub_env)

    else:
        print(f"Unknown command: {args.command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
