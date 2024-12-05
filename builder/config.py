import os

INCLUDE_DIRS = ["include", "modules", "src"]  # , "third_party"]
DEFAULT_OUTPUT_DIR = os.path.join(os.getcwd(), "output")


bin_extensions_by_platform = {
    "Windows": ("lib", "dat"),
    "Linux": ("a", "dat"),
    # "Darwin": ("a", "dat"),
    "Android": ("a", "dat"),
    # "iOS": ("a", "dat"),
}


common_flags = {
    "extra_cflags": ["-g0"],  # Removes debug symbols from the binary to reduce its size (required for linux/darwin) - Fixed here: Stop forcing debug symbol generation with skia_enable_optimize_size | https://skia-review.googlesource.com/c/skia/+/892217
    "is_debug": False,
    "is_official_build": True,
    "is_component_build": False,
    "is_trivial_abi": False,
    "skia_compile_sksl_tests": False,
    # "skia_compile_modules": False,

    "skia_enable_tools": False,
    "skia_enable_precompile": True,
    "skia_enable_optimize_size": True,
    "skia_enable_svg": True,
    # "skia_enable_fontmgr_custom_directory": False,
    # "skia_enable_skshaper": True,
    # "skia_enable_ganesh": True,
    # "skia_enable_gpu": True,
    # "skia_enable_skottie": True,

    "skia_use_system_expat": False,
    "skia_use_system_libjpeg_turbo": False,
    "skia_use_system_libpng": False,
    "skia_use_system_libwebp": False,
    "skia_use_system_zlib": False,
    "skia_use_system_icu": False,
    "skia_use_system_harfbuzz": False,
    # "skia_use_system_freetype2": False,
}


platform_specific_flags = {
    "windows-x64": {
        # graphics backends
        "skia_use_gl": True,
        "skia_use_vulkan": True,
        "skia_use_direct3d": True,
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
        # graphics backends
        "skia_use_gl": True,
        "skia_use_vulkan": True,
        "skia_use_direct3d": False,
        "skia_use_angle": False,
        "skia_use_dawn": False,
        "skia_use_metal": False,

        # build env configs
        "target_os": "linux",
        "target_cpu": "x86_64",
        "cc": "clang",
        "cxx": "clang++",
        "extra_cflags_cc": ["-std=c++17"]
    },
    "android-arm": {
        # graphics backends
        "skia_use_gl": True,
        "skia_use_vulkan": True,
        "skia_use_direct3d": False,
        "skia_use_angle": False,
        "skia_use_dawn": False,
        "skia_use_metal": False,

        # build env configs
        "target_os": "android",
        "target_cpu": "arm",
        "ndk": "C:/Program Files/NDK",
        "cc": "clang",
        "cxx": "clang++",
        "extra_cflags_cc": ["-std=c++17"]
    },
    "android-arm64": {
        "skia_use_gl": True,
        "skia_use_vulkan": True,
        "skia_use_direct3d": False,
        "skia_use_angle": False,
        "skia_use_dawn": False,
        "skia_use_metal": False,
    },
    "ios": {
        "skia_use_gl": True,
        "skia_use_vulkan": False,
        "skia_use_direct3d": False,
        "skia_use_angle": True,
        "skia_use_dawn": False,
        "skia_use_metal": True,
    },
    "macos": {
        "skia_use_gl": True,
        "skia_use_vulkan": False,
        "skia_use_direct3d": False,
        "skia_use_angle": True,
        "skia_use_dawn": False,
        "skia_use_metal": True,
    },
}


def get_build_args(target_platform):
    platform_flags = platform_specific_flags.get(target_platform, {})
    flags = {**common_flags, **platform_flags}

    args_list = []
    for key, value in flags.items():
        if isinstance(value, str):
            # Handle string values with escaped quotes
            args_list.append(f'{key}="{value}"')
        elif isinstance(value, list):
            # Handle list values with brackets and quotes
            formatted_list = (
                "[" + ",".join([f'"{item}"' for item in value]) + "]"
            )
            args_list.append(f"{key}={formatted_list}")
        elif isinstance(value, bool):
            args_list.append(f"{key}={str(value).lower()}")

    return " ".join(args_list)


def parse_custom_build_args(custom_args_str):
    custom_args = {}
    for arg in custom_args_str.split(" "):
        key, value = arg.split("=")
        custom_args[key] = value.strip('"')
    return custom_args

