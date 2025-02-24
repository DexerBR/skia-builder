import json
import os
import re
import shutil
import signal
import subprocess
import sys
import tarfile
import threading
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

from skia_builder.config import DEFAULT_OUTPUT_DIR, INCLUDE_DIRS, bin_extensions_by_platform


class Logger:
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    LIGHT_GRAY = "\033[37m"
    DARK_GRAY = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    WHITE = "\033[97m"

    BOLD = "\033[1m"

    RESET = "\033[0m"

    @staticmethod
    def info(message):
        print(f"{Logger.GREEN}[INFO]{Logger.RESET} {message}", flush=True)

    @staticmethod
    def warning(message):
        print(f"{Logger.YELLOW}[WARNING]{Logger.RESET} {message}", flush=True)

    @staticmethod
    def error(message):
        print(f"{Logger.RED}[ERROR]{Logger.RESET} {message}", flush=True)

    @staticmethod
    def debug(message):
        print(f"{Logger.BLUE}[DEBUG]{Logger.RESET} {message}", flush=True)

    @staticmethod
    def custom(message, color, bold=False):
        if bold:
            color = f"{Logger.BOLD}{color}"

        formatted_message = "\n".join(
            f"{color}{line}{Logger.RESET}" for line in message.splitlines()
        )
        if message.endswith("\n"):
            formatted_message += "\n"

        print(formatted_message, flush=True)


def run_command(command_list, step_description, cwd=None, exit_on_error=True):
    Logger.custom(f"\n--- Running step: {step_description} ---", Logger.BRIGHT_YELLOW)

    process = None
    returncode = 0
    stop_event = threading.Event()

    def handle_sigterm(*args):
        stop_event.set()
        if process:
            process.terminate()

    signal.signal(signal.SIGTERM, handle_sigterm)

    try:
        process = subprocess.Popen(
            command_list,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

        def print_output(pipe, log_function):
            for line in iter(pipe.readline, ""):
                if stop_event.is_set():
                    break
                log_function(line.strip())

        stdout_thread = threading.Thread(target=print_output, args=(process.stdout, print))
        stderr_thread = threading.Thread(
            target=print_output,
            args=(process.stderr, lambda line: print(line, file=sys.stderr)),
        )

        stdout_thread.start()
        stderr_thread.start()

        while stdout_thread.is_alive() or stderr_thread.is_alive():
            stdout_thread.join(timeout=0.1)
            stderr_thread.join(timeout=0.1)
            if stop_event.is_set():
                break

        process.stdout.close()
        process.stderr.close()

        if not stop_event.is_set():
            returncode = process.wait()
    except Exception as e:
        Logger.error(f"Failed to start process: {e}")
        returncode = 1
    finally:
        if process and process.poll() is None:
            process.kill()
            process.wait()

    if returncode == 0:
        message = f"Command succeeded: {' '.join(command_list)}\n"
        color = Logger.GREEN
    else:
        message = f"Error executing command: {' '.join(command_list)}\n"
        color = Logger.RED
    Logger.custom(message, color, bold=True)

    if returncode != 0 and exit_on_error:
        Logger.error(f"Exit code: {returncode}\n")
        sys.exit(returncode)

    return returncode


def get_files_with_extensions(directory, extensions):
    matching_files = []
    for item in os.listdir(directory):
        full_path = os.path.join(directory, item)
        if os.path.isfile(full_path):
            name_parts = item.split(".")
            if len(name_parts) == 2 and name_parts[-1] in extensions:
                matching_files.append(full_path)

    return matching_files


def _ensure_output_dir(output_dir):
    if output_dir is None:
        output_dir = DEFAULT_OUTPUT_DIR
    os.makedirs(output_dir, exist_ok=True)
    return output_dir


def store_skia_license(skia_dir, output_dir=None):
    output_dir = _ensure_output_dir(output_dir)

    src_license = os.path.join(skia_dir, "LICENSE")
    dest_license = os.path.join(output_dir, "SKIA_LICENSE")

    if os.path.exists(src_license):
        shutil.copy(src_license, dest_license)
        Logger.info(f"Copied LICENSE to {dest_license}")
    else:
        Logger.error(f"LICENSE file not found at {src_license}")


def store_includes(skia_dir, output_dir=None):
    output_dir = _ensure_output_dir(output_dir)

    for folder in INCLUDE_DIRS:
        src_folder = os.path.join(skia_dir, folder)
        dest_folder = os.path.join(output_dir, folder)

        if os.path.exists(src_folder):
            shutil.copytree(src_folder, dest_folder)
            Logger.info(f"Copied {src_folder} to {dest_folder}")
        else:
            Logger.error(f"{src_folder} does not exist.")


def archive_build_output(build_input_src, target_platform, output_dir=None):
    output_dir = _ensure_output_dir(output_dir)

    if not os.path.exists(build_input_src):
        Logger.error(
            f"Build input src {build_input_src} does not exist. "
            "There was an error during the build process?"
        )
        return

    # Ensure output/bin dir exists
    output_bin_dir = os.path.join(output_dir, "bin")
    os.makedirs(output_bin_dir, exist_ok=True)

    # Get the list of files with the specified extensions
    matching_files = get_files_with_extensions(
        build_input_src, bin_extensions_by_platform[target_platform]
    )

    # Copy each matching file to the output_bin_dir
    for file_path in matching_files:
        shutil.copy(file_path, output_bin_dir)
        Logger.info(f"Copied {file_path} to {output_bin_dir}")

    tar_path = os.path.join(output_dir, f"{os.path.basename(build_input_src)}.tar.gz")
    with tarfile.open(tar_path, "w:gz") as tar:
        for name in os.listdir(output_dir):
            full_path = os.path.join(output_dir, name)
            tar.add(full_path, arcname=name)

    Logger.info(f"Build output archived to {tar_path}")


def check_update_skia_version():
    chromium_url = (
        "https://chromiumdash.appspot.com/fetch_releases?channel=Stable&platform=Windows&num=1"
    )
    release_notes_url = "https://raw.githubusercontent.com/google/skia/main/RELEASE_NOTES.md"
    versions_file = "versions.py"
    readme_file = "README.md"

    # Fetch Chromium dash data and extract the milestone
    try:
        with urlopen(chromium_url) as response:
            if response.status != 200:
                raise URLError(f"HTTP Status {response.status}")
            data = json.load(response)
    except URLError as e:
        Logger.error(f"Failed to fetch Chromium release data from {chromium_url}. Error: {e}")
        sys.exit(1)

    try:
        milestone = data[0]["milestone"]
    except (IndexError, KeyError):
        Logger.error("Unexpected format when extracting the milestone from the fetched data.")
        sys.exit(1)

    # Fetch Skia release notes
    try:
        with urlopen(release_notes_url) as response:
            if response.status != 200:
                raise URLError(f"HTTP Status {response.status}")
            release_notes = response.read().decode("utf-8")
    except URLError as e:
        Logger.error(f"Failed to fetch Skia release notes from {release_notes_url}. Error: {e}")
        sys.exit(1)

    milestone_pattern = f"Milestone {milestone}"
    if milestone_pattern not in release_notes:
        Logger.info(
            f"No new stable Skia milestone found (expected {milestone}). "
            "Skia update is not required."
        )
        sys.exit(0)

    Logger.info(
        f"Found new Skia stable milestone {milestone}. "
        f"Proceeding with updates to {versions_file} and {readme_file}."
    )

    versions_file_path = Path(__file__).parent / versions_file
    readme_file_path = Path(__file__).parent.parent / readme_file

    if not versions_file_path.exists():
        Logger.error(f"{versions_file} not found in the expected location. Update cannot proceed.")
        sys.exit(1)

    try:
        versions_content = versions_file_path.read_text(encoding="utf-8")
    except Exception as e:
        Logger.error(f"Error reading {versions_file}: {e}. Unable to proceed with version update.")
        sys.exit(1)

    # Updating version in versions.py
    new_versions_content, _ = re.subn(
        r'SKIA_VERSION = "m\d+"', f'SKIA_VERSION = "m{milestone}"', versions_content
    )

    if versions_content == new_versions_content:
        Logger.warning(f"No SKIA_VERSION entry found in {versions_file} to update.")
    else:
        try:
            versions_file_path.write_text(new_versions_content, encoding="utf-8")
            Logger.info(
                f"Successfully updated {versions_file}: Set SKIA_VERSION to 'm{milestone}'."
            )
        except Exception as e:
            Logger.error(
                f"Error writing to {versions_file}: {e}. Update of {versions_file} failed."
            )
            sys.exit(1)

    # Updating README.md
    try:
        readme_content = readme_file_path.read_text(encoding="utf-8")
    except Exception as e:
        Logger.error(f"Error reading {readme_file}: {e}. Unable to proceed with README update.")
        sys.exit(1)

    # Replacing version in the badge
    new_readme_content, _ = re.subn(
        r"!\[SKIA_VERSION\]\(https://img.shields.io/badge/Skia_version-m\d+-blue\?style=flat-square\)",
        f"![SKIA_VERSION](https://img.shields.io/badge/Skia_version-m{milestone}-blue?style=flat-square)",
        readme_content,
    )

    if readme_content == new_readme_content:
        Logger.warning(f"No SKIA_VERSION badge found in {readme_file} to update.")
    else:
        try:
            readme_file_path.write_text(new_readme_content, encoding="utf-8")
            Logger.info(
                f"Successfully updated {readme_file}: Updated SKIA_VERSION badge to 'm{milestone}'."
            )
        except Exception as e:
            Logger.error(f"Error writing to {readme_file}: {e}. Update of {readme_file} failed.")
            sys.exit(1)

    # NOTE: In GitHub Actions, this code appends NEW_SKIA_VERSION to the env file for later steps.
    github_env_file = os.getenv("GITHUB_ENV")
    if github_env_file:
        with open(github_env_file, "a") as env_file:
            if versions_content != new_versions_content and readme_content != new_readme_content:
                env_file.write(f"NEW_SKIA_VERSION=m{milestone}\n")
            else:
                env_file.write("NEW_SKIA_VERSION=''\n")
