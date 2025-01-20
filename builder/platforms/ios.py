from builder.platforms import execute_build

SUPPORTED_ARCHITECTURES = "arm64"


def setup_env():
    pass


def build(target_cpu, custom_build_args=None, override_build_args=None, archive_output=False):
    execute_build(target_cpu, "ios", custom_build_args, override_build_args, archive_output)
