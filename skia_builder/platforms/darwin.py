from skia_builder.platforms import execute_build, setup_env_common

SUPPORTED_ARCHITECTURES = ("arm64", "x64")


def setup_env(skip_llvm_instalation):
    setup_env_common()


def build(target_cpu, custom_build_args=None, override_build_args=None, archive_output=False):
    execute_build(target_cpu, "darwin", custom_build_args, override_build_args, archive_output)
