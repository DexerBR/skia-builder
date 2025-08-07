import os
from skia_builder.versions import ANDROID_NDK

INCLUDE_DIRS = ["include", "modules", "src"]  # , "third_party"]
DEFAULT_OUTPUT_DIR = os.path.join(os.getcwd(), "output")


bin_extensions_by_platform = {
    "windows": ("lib", "dat"),
    "linux": ("a", "dat"),
    "macos": ("a", "dat"),
    "android": ("a", "dat"),
    "ios": ("a", "dat"),
    "iossimulator": ("a", "dat"),
}


common_flags = {
    # Removes debug symbols from the binary to reduce its size (required for linux/macos)
    # - Fixed here: Stop forcing debug symbol generation with skia_enable_optimize_size
    # | https://skia-review.googlesource.com/c/skia/+/892217
    "extra_cflags": ["-g0"],
    "is_debug": False,
    "is_official_build": True,
    "is_component_build": False,
    "is_trivial_abi": False,
    "skia_compile_sksl_tests": False,
    # "skia_compile_modules": True,
    "skia_enable_tools": False,
    "skia_enable_pdf": False,
    "skia_enable_precompile": True,
    "skia_enable_optimize_size": True,
    "skia_enable_sksl": True,
    "skia_enable_svg": True,
    "skia_enable_skottie": True,
    "skia_enable_skshaper": True,
    "skia_enable_skparagraph": True,
    "skia_enable_gpu": True,
    "skia_enable_ganesh": True,
    # "skia_enable_skresources": True,
    # "skia_enable_sksg": True,
    # "skia_enable_fontmgr_custom_directory": False,
    # "skia_enable_skjson": True,
    # "skia_use_icu": True,
    # "skia_use_freetype": True,
    "skia_use_system_expat": False,
    "skia_use_system_libjpeg_turbo": False,
    "skia_use_system_libpng": False,
    "skia_use_system_libwebp": False,
    "skia_use_system_zlib": False,
    "skia_use_system_icu": False,
    "skia_use_system_harfbuzz": False,
    # "skia_use_system_freetype2": False,
}


android_base_flags = {
    **common_flags,
    # graphics backends
    "skia_use_gl": True,
    "skia_use_vulkan": False,
    "skia_use_direct3d": False,
    "skia_use_angle": False,
    "skia_use_dawn": False,
    "skia_use_metal": False,
    # build env configs
    "target_os": "android",
    "ndk": os.path.join(os.getcwd(), "Android_NDK", ANDROID_NDK),
    "cc": "clang",
    "cxx": "clang++",
    "extra_cflags_cc": ["-std=c++17"],
    # extra (temporary?) arguments
    "skia_use_system_freetype2": False,
}


linux_base_flags = {
    **common_flags,
    # graphics backends
    "skia_use_gl": True,
    "skia_use_vulkan": False,
    "skia_use_direct3d": False,
    "skia_use_angle": False,
    "skia_use_dawn": False,
    "skia_use_metal": False,
    # build env configs
    "target_os": "linux",
    "cc": "clang",
    "cxx": "clang++",
    "extra_cflags_cc": ["-std=c++17"],
}

macos_base_flags = {
    **common_flags,
    # graphics backends
    "skia_use_gl": True,
    "skia_use_vulkan": False,
    "skia_use_direct3d": False,
    "skia_use_angle": False,
    "skia_use_dawn": False,
    "skia_use_metal": True,
    # build env configs
    "target_os": "mac",
    "skia_gl_standard": "gles",
}

ios_base_flags = {
    **common_flags,
    # graphics backends
    "skia_use_gl": True,
    "skia_use_vulkan": False,
    "skia_use_direct3d": False,
    "skia_use_angle": False,
    "skia_use_dawn": False,
    "skia_use_metal": True,
    # build env config
    "target_os": "ios",
    "ios_min_target": "13.0",
    "skia_enable_pdf": False,
    "skia_use_expat": False,
}

platform_specific_flags = {
    "windows-x64": {
        **common_flags,
        # graphics backends
        "skia_use_gl": True,
        "skia_use_vulkan": False,
        "skia_use_direct3d": False,
        "skia_use_angle": True,
        "skia_use_dawn": False,
        "skia_use_metal": False,
        # build env configs
        "target_os": "win",
        "target_cpu": "x86_64",
        "cc": "clang-cl",
        "cxx": "clang-cl++",
        "clang_win": "C:/Program Files/LLVM",
        "extra_cflags_cc": ["/std:c++17"],
    },
    "linux-x64": {
        **linux_base_flags,
        "target_cpu": "x86_64",
        "extra_cflags": [
            *linux_base_flags["extra_cflags"],
            "-fPIC",
        ],
        "extra_cflags_cc": [
            *linux_base_flags["extra_cflags_cc"],
            "-fPIC",
        ],
    },
    "linux-arm64": {
        **linux_base_flags,
        "target_cpu": "arm64",
        "skia_use_system_freetype2": False,
        "skia_use_egl": True,
        "skia_gl_standard": "gles",
        "extra_cflags": [
            *linux_base_flags["extra_cflags"],
            "-fPIC",
        ],
        "extra_cflags_cc": [
            *linux_base_flags["extra_cflags_cc"],
            "-fPIC",
        ],
    },
    # "linux-arm": {
    #     **linux_base_flags,
    #     "target_cpu": "arm",
    # },
    "android-arm": {
        **android_base_flags,
        "target_cpu": "arm",
    },
    "android-arm64": {
        **android_base_flags,
        "target_cpu": "arm64",
    },
    "android-x64": {
        **android_base_flags,
        "target_cpu": "x64",
    },
    "android-x86": {
        **android_base_flags,
        "target_cpu": "x86",
    },
    "ios-arm64": {
        **ios_base_flags,
        "target_cpu": "arm64",
    },
    "iossimulator-arm64": {
        **ios_base_flags,
        "target_cpu": "arm64",
        "ios_use_simulator": True,
    },
    "iossimulator-x64": {
        **ios_base_flags,
        "target_cpu": "x64",
        "ios_use_simulator": True,
    },
    "macos-x64": {
        **macos_base_flags,
        "target_cpu": "x64",
    },
    "macos-arm64": {
        **macos_base_flags,
        "target_cpu": "arm64",
    },
}


def parse_override_build_args(base_args_str, override_args_str):
    base_args = base_args_str.replace("'", '"').split()
    override_args = override_args_str.replace("'", '"').split()

    for override_arg in override_args:
        flag_b, value_b = override_arg.split("=", 1)

        # Loop through base_args and update the matching flag-value pairs
        for i, custom_arg in enumerate(base_args):
            flag_a, _ = custom_arg.split("=", 1)
            if flag_a == flag_b:
                base_args[i] = f"{flag_a}={value_b}"
                break

    return " ".join(base_args)


def get_build_args(target_platform):
    flags = platform_specific_flags.get(target_platform, {})

    args_list = []
    for key, value in flags.items():
        if isinstance(value, str):
            # Handle string values with escaped quotes
            args_list.append(f'{key}="{value}"')
        elif isinstance(value, list):
            # Handle list values with brackets and quotes
            formatted_list = "[" + ",".join([f'"{item}"' for item in value]) + "]"
            args_list.append(f"{key}={formatted_list}")
        elif isinstance(value, bool):
            args_list.append(f"{key}={str(value).lower()}")

    return " ".join(args_list)


def parse_custom_build_args(custom_args_str):
    return custom_args_str.replace("'", '"')
