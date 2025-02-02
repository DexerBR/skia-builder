import os
import platform
import sys
from enum import Enum

from skia_builder.config import get_build_args, parse_override_build_args
from skia_builder.utils import (
    Logger,
    archive_build_output,
    run_command,
    store_includes,
    store_skia_license,
)
from skia_builder.versions import SKIA_VERSION


PLATFORM_NAME_MAP = {
    "Darwin": "macOS",
}


class Architecture(Enum):
    ARM = "arm"
    ARM64 = "arm64"
    X64 = "x64"
    X86 = "x86"


class BasePlatform:
    @property
    def lowercase(self):
        """Returns the platform name in lowercase."""
        return self.value.lower()


class HostPlatform(BasePlatform, Enum):
    WINDOWS = "Windows"
    LINUX = "Linux"
    MACOS = "macOS"

    @classmethod
    def get_current(cls):
        """Returns the current platform based on platform.system()."""
        current_system = platform.system()
        system_name = PLATFORM_NAME_MAP.get(current_system, current_system)
        try:
            return cls(system_name)
        except ValueError:
            raise ValueError(f"Unsupported platform: {current_system}")

    @property
    def supported_architectures(self):
        """Supported architectures for the host platform."""
        if self == HostPlatform.WINDOWS:
            return [Architecture.X64.value]
        elif self in (HostPlatform.LINUX, HostPlatform.MACOS):
            return [Architecture.X64.value, Architecture.ARM64.value]
        else:
            raise ValueError(f"Unknown platform: {self}")


class SubPlatform(BasePlatform, Enum):
    ANDROID = "Android"
    IOS = "iOS"
    IOS_SIMULATOR = "iOSSimulator"

    @property
    def supported_architectures(self):
        """Supported architectures for the target platform."""
        if self == SubPlatform.ANDROID:
            return [
                Architecture.ARM.value,
                Architecture.ARM64.value,
                Architecture.X64.value,
                Architecture.X86.value,
            ]
        elif self == SubPlatform.IOS:
            return [Architecture.ARM64.value]
        elif self == SubPlatform.IOS_SIMULATOR:
            return [Architecture.ARM64.value, Architecture.X64.value]
        else:
            raise ValueError(f"Unsupported platform: {self}")

    @property
    def host_platform(self):
        """Returns the compatible host platform or None."""
        try:
            current_host = HostPlatform.get_current()
        except ValueError:
            return None

        if self in (SubPlatform.IOS, SubPlatform.IOS_SIMULATOR):
            return current_host if current_host == HostPlatform.MACOS else None
        elif self == SubPlatform.ANDROID:
            return current_host if current_host == HostPlatform.WINDOWS else None
            # return (
            #     current_platform
            #     if current_platform in (HostPlatform.WINDOWS, HostPlatform.MACOS)
            #     else None
            # )  TODO: implement MACOS later
        else:
            raise ValueError(f"Unknown target platform: {self}")


class CommonPlatformManager:
    HOST_PLATFORM = None
    """
    The primary platform where the code will be generated. Possible values are:
    - Platform.WINDOWS
    - Platform.LINUX
    - Platform.MACOS

    Defines the base environment for building the project.
    """

    TARGET_PLATFORM = None
    """
    The target platform for building Skia. Typically, it matches `HOST_PLATFORM` for Linux, Windows,
    and macOS, but it can also take the following values depending on the availability of the
    host-to-sub-environment implementation:
    - Platform.ANDROID
    - Platform.IOS
    - Platform.IOS_SIMULATOR

    This variable defines the final platform where the code will be executed.
    """

    SUPPORTED_ARCHITECTURES = None
    """
    A set of architectures supported for building Skia, determined based on the `TARGET_PLATFORM`
    (i.e., `TARGET_PLATFORM.supported_architectures`).

    This defines which CPU architectures are compatible with the current target platform.
    Examples include `x86`, `x64`, `arm`, and `arm64`.
    """

    @classmethod
    def _setup_env(cls):
        """
        Configures the Skia environment by cloning repositories, syncing dependencies,
        and optionally installing additional dependencies (specific to Linux).
        """
        if not cls.HOST_PLATFORM:
            Logger.error("Unsupported platform")
            sys.exit(1)

        run_command(
            [
                "git",
                "clone",
                "https://chromium.googlesource.com/chromium/tools/depot_tools.git",
            ],
            "Cloning depot_tools",
        )

        gclient_executable = cls._get_executable_path(
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

        if cls.HOST_PLATFORM == HostPlatform.LINUX:
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

    @classmethod
    def _build(
        cls,
        target_cpu,
        custom_build_args=None,
        override_build_args=None,
        archive_output=False,
    ):
        """
        Build Skia for a specified platform and CPU target.

        Args:
            target_cpu (str): The target CPU architecture (e.g., "arm64", "x64").
            custom_build_args (str): Optional custom build flags.
            override_build_args (str): Optional build flags that override the default or custom
                build flags.
            archive_output (bool): Whether to archive the build output.
        """
        if not cls.TARGET_PLATFORM:
            Logger.error("Unsupported target platform")
            sys.exit(1)

        flags_mode = "custom" if custom_build_args else "default"
        Logger.info(f"Building with {flags_mode} flags.")
        if override_build_args:
            Logger.info(f"Overriding {flags_mode} build flags with: {override_build_args}.")

        Logger.info(
            "Archiving build output." if archive_output else "Build output will not be archived."
        )

        platform = cls.TARGET_PLATFORM.lowercase
        skia_path = os.path.join(os.getcwd(), "skia")
        build_target = f"{platform}-{target_cpu}"
        output_dir = os.path.join("output", build_target)

        if archive_output:
            store_skia_license(skia_path, output_dir=output_dir)
            store_includes(skia_path, output_dir=output_dir)

        build_args = custom_build_args or get_build_args(build_target)
        if override_build_args:
            build_args = parse_override_build_args(build_args, override_build_args)

        gn_executable = cls._get_executable_path(
            "skia",
            "bin",
            executable_name="gn",
            windows_extension=".exe",
        )
        ninja_executable = cls._get_executable_path(
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

    @classmethod
    def _get_executable_path(cls, *path_parts, executable_name, windows_extension=None):
        """
        Builds a complete path for an executable, using the current working directory as the base.
        Adds the specified extension only on Windows.

        Args:
            *path_parts: Variable-length list of path components (relative to the current
                directory).
            executable_name: The name of the executable (without the extension).
            windows_extension: Optional extension to add (e.g., '.exe', '.bat') on Windows.
                No extension is added for non-Windows platforms.

        Returns:
            str: The complete path to the executable, starting from the current working directory.
        """
        if cls.HOST_PLATFORM == HostPlatform.WINDOWS and windows_extension:
            executable_name += windows_extension

        return os.path.join(os.getcwd(), *path_parts, executable_name)

    @classmethod
    def setup_env(cls, skip_llvm_instalation=False):
        """Sets up the environment. When overriding, call _setup_env() at the end."""
        cls._setup_env()

    @classmethod
    def build(
        cls,
        target_cpu,
        custom_build_args=None,
        override_build_args=None,
        archive_output=False,
    ):
        """Builds Skia. When overriding, call _build() at the end."""
        cls._build(
            target_cpu,
            custom_build_args,
            override_build_args,
            archive_output,
        )


class CommonSubPlatformManager(CommonPlatformManager):
    HOST_PLATFORMS_ENV_SETUP = {}

    @staticmethod
    def noop(*args, **kwargs):
        """No-op method that performs no operation.

        This method is used as a placeholder for cases where a function is
        expected but no action is required.
        """
        pass

    @classmethod
    def _validate_host_platform(cls):
        if not cls.HOST_PLATFORM:
            Logger.error("Unsupported host platform")
            sys.exit(1)

    @classmethod
    def _get_host_setup_env(cls):
        supported_host_platforms = cls.HOST_PLATFORMS_ENV_SETUP
        system_name = platform.system()

        current_platform = PLATFORM_NAME_MAP.get(system_name, system_name)

        if not (setup_env_host := supported_host_platforms.get(current_platform)):
            available_platforms = [
                name for name, config in supported_host_platforms.items() if config
            ]

            Logger.error(
                f"Unsupported host platform: {current_platform}. "
                f"Available host platforms: {', '.join(available_platforms) or 'none'}"
            )
            sys.exit(1)

        return setup_env_host

    @classmethod
    def setup_env(cls, skip_llvm_instalation=False):
        cls._validate_host_platform()
        setup_env_host = cls._get_host_setup_env()
        setup_env_host(skip_llvm_instalation)
        cls._setup_env()

    @classmethod
    def build(
        cls,
        target_cpu,
        custom_build_args=None,
        override_build_args=None,
        archive_output=False,
    ):
        cls._validate_host_platform()
        cls._build(
            target_cpu,
            custom_build_args,
            override_build_args,
            archive_output,
        )
