import os
import shutil
import signal
import subprocess
import sys
import tarfile
import threading
import platform

from builder.config import DEFAULT_OUTPUT_DIR, INCLUDE_DIRS, bin_extensions_by_platform


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
    def warn(message):
        print(f"{Logger.YELLOW}[WARN]{Logger.RESET} {message}", flush=True)

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


def run_command(command_list, step_description, cwd=None):
    Logger.custom(
        f"\n--- Running step: {step_description} ---", Logger.BRIGHT_YELLOW
    )

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

        stdout_thread = threading.Thread(
            target=print_output, args=(process.stdout, print)
        )
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

    if returncode != 0:
        Logger.error(f"Exit code: {returncode}\n")
        sys.exit(returncode)


def get_files_with_extensions(directory, extensions):
    matching_files = []
    for item in os.listdir(directory):
        full_path = os.path.join(directory, item)
        if os.path.isfile(full_path):
            name_parts = item.split(".")
            if len(name_parts) == 2 and name_parts[-1] in extensions:
                matching_files.append(full_path)

    return matching_files


def store_includes(skia_dir, output_dir=None):
    if output_dir is None:
        output_dir = DEFAULT_OUTPUT_DIR

    os.makedirs(output_dir, exist_ok=True)

    for folder in INCLUDE_DIRS:
        src_folder = os.path.join(skia_dir, folder)
        dest_folder = os.path.join(output_dir, folder)

        if os.path.exists(src_folder):
            shutil.copytree(src_folder, dest_folder)
            Logger.info(f"Copied {src_folder} to {dest_folder}")
        else:
            Logger.error(f"{src_folder} does not exist.")


def archive_build_output(build_input_src, platform=platform.system(), output_dir=None):
    if output_dir is None:
        output_dir = DEFAULT_OUTPUT_DIR

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
    matching_files = get_files_with_extensions(build_input_src, bin_extensions_by_platform[platform])

    # Copy each matching file to the output_bin_dir
    for file_path in matching_files:
        shutil.copy(file_path, output_bin_dir)
        Logger.info(f"Copied {file_path} to {output_bin_dir}")

    tar_path = os.path.join(
        output_dir, f"{os.path.basename(build_input_src)}.tar.gz"
    )
    with tarfile.open(tar_path, "w:gz") as tar:
        for name in os.listdir(output_dir):
            full_path = os.path.join(output_dir, name)
            if os.path.isdir(full_path):
                tar.add(full_path, arcname=name)

    Logger.info(f"Build output archived to {tar_path}")
