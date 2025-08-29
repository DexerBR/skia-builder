# skia-builder
#### Cross-platform tool for Skia environment setup and binary generation

<br>

## Supported platforms, architectures, and environments in `skia-builder`

[![PyPI - Version](https://img.shields.io/pypi/v/skia-builder?style=flat-square&color=blue)](https://pypi.org/project/skia-builder/)

![SKIA_VERSION](https://img.shields.io/badge/Skia_version-m139-blue?style=flat-square)

![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/DexerBR/skia-builder/build_skia_linux.yml?event=push&style=flat-square&label=Linux%20build)
![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/DexerBR/skia-builder/build_skia_macos.yml?event=push&style=flat-square&label=macOS%20build)
![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/DexerBR/skia-builder/build_skia_windows.yml?event=push&style=flat-square&label=Windows%20build)
<br>
![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/DexerBR/skia-builder/build_skia_android.yml?event=push&style=flat-square&label=Android%20build)
![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/DexerBR/skia-builder/build_skia_ios.yml?event=push&style=flat-square&label=iOS%20build)


Platforms and architectures currently supported:


| OS | Supported Architectures |
| :-:        | :-:            |
| `Linux`  | `x64`<br>`arm64`        |
| `macOS`  | `x64`<br>`arm64`        |
| `Windows`  | `x64`        |
| `Android`  | `arm`<br>`arm64`<br>`x64`<br>`x86`        |
| `iOS`  | `arm64`        |
| `iOS Simulator`  | `x64`<br>`arm64`        |

<br>

Main environments and their supported sub-environments:

| Main Environment | Available sub-environments (`sub-env`) |
| :-:        | :-:            |
| `Linux`    | `-`        |
| `macOS`  | `iOS`<br>`iOSSimulator`        |
| `Windows`  | `Android`        |


<br>

## Usage
### Setting up the Skia environment


The `setup-env` command of `skia-builder` can be used to configure two types of environments: the main environment for Linux, macOS, and Windows, and the sub-environment (`sub-env`) for Android, iOS, and iOS Simulator.

***Note:*** The sub-environment configuration automatically sets up the main (host) environment.

#### LLVM Installation

LLVM is automatically installed on Linux and Windows platforms. However, the installation process varies between operating systems. Below are the detailed instructions for each platform:

- **Linux**: LLVM is automatically installed via the *"Automatic installation script"*, available at [https://apt.llvm.org/](https://apt.llvm.org/).

- **Windows**: On Windows, LLVM is installed via the Chocolatey package manager. Chocolatey is a requirement for LLVM installation. If the user does not have Chocolatey installed, it must be installed first, or the user can manually install LLVM from [https://github.com/llvm/llvm-project/releases](https://github.com/llvm/llvm-project/releases).

- **macOS**: LLVM comes with Xcode on macOS, which can be installed via the App Store or from the Apple Developer website. The *Command Line Tools* may be insufficient for some advanced tasks.

To disable the automatic installation of LLVM, see the example below.

#### Examples:

Automatically detects the OS and architecture and configures the main environment (Linux, Windows, macOS):

```
skia-builder setup-env
```

If the user wants to manually manage the LLVM installation (or use a different compiler), they can pass the following argument when setting up the environment, which will skip the automatic LLVM installation:

```
skia-builder setup-env --skip-llvm-instalation
```

Does the same as the command above, and additionally configures the Android environment (only available on Windows):

```
skia-builder setup-env --sub-env=Android
```


<br>

### Listing available build arguments

The `list-args` command displays all available build configuration arguments supported by the Skia version. These flags can be overridden using `--custom-build-args` or `--override-build-args`.

```
skia-builder list-args
```


<br>

### Generating Skia binaries

To generate the binaries, **it is necessary to specify the target architecture**. Optionally, the `--archive` command can be used to archive the output binaries to `output/<OS>-<architecture>/*` and to generate a compressed file in `output/<OS><architecture>/<OS>-<architecture>.tar.gz`.

#### Examples:

On Windows, to generate the binaries for Windows x64 and archive the output to `output/windows-x64/*` and `output/windows-x64/windows-x64.tar.gz`:
```
skia-builder build --target-cpu=x64 --archive
```

Still in the Windows environment (host environment), to generate the binaries for Android `arm64` and archive the output to `output/android-arm64/*` and `output/android-arm64/android-arm64.tar.gz`:

```
skia-builder build --sub-env=Android --target-cpu=arm64 --archive
```

The `skia-builder` also allows passing custom arguments for the Skia build flags through `--custom-build-args=<args>`. When these arguments are defined, **`skia-builder` will prioritize them and automatically ignore all default arguments**. The command below will generate the binaries for Android within the host environment (Windows) for the `arm64` architecture, using the custom build args, and archive the output as mentioned above.


***Important:*** The usage logic of `"` and `'` must be implemented exactly as shown in the example below. Each flag definition should be separated by a space, and there should be no spaces within each flag definition.


- 🟢 **Do:** `--custom-build-args="extra_cflags=['-g0']"`

- 🔴 **Don't:** `--custom-build-args="extra_cflags =[ '-g0']"`

- 🟢 **Do:** `--custom-build-args="extra_cflags=['-g0'] is_debug=false extra_cflags_cc=['-std=c++17'] ..."`

- 🔴 **Don't:** `--custom-build-args="extra_cflags=[ '-g0'] is_debug =false  extra_cflags_cc=['-std=c++17' ] ..."`

```
skia-builder build --sub-env=Android --target-cpu=arm64 --custom-build-args="extra_cflags=['-g0'] is_debug=false is_component_build=false cc='clang' cxx='clang++' extra_cflags_cc=['-std=c++17'] ..." --archive
```

<br>

### Build workflows and binary generation

This repository uses GitHub Actions to automatically build Skia binaries for **Windows**, **macOS**, **Linux**, **iOS**/**iOS Simulator**, and **Android** under the following conditions:  

#### Triggers:  
- **Tags**: Pushing a tag (e.g., `v1.0.0`) triggers builds for all platforms.  
- **Pull Requests**:  
  - Opened or updated PRs trigger builds **only if labeled** with:  
    - `ci/build-binaries-windows` for Windows binaries.  
    - `ci/build-binaries-macos` for macOS binaries.  
    - `ci/build-binaries-linux` for Linux binaries.  
    - `ci/build-binaries-ios` for iOS/iOS Simulator binaries.  
    - `ci/build-binaries-android` for Android binaries.  

#### Concurrency Control:  
- Only the **latest** build for a specific PR or tag will run.  
- Previous queued or in-progress builds for the same PR or tag are automatically **canceled** to prioritize the most recent changes.  

<br>

### General Notes
For macOS, we assume the built library will be used in an application that uses ANGLE as a GL provider. As a result, we force the `skia_gl_standard` setting to `"gles"`, since Skia cannot accurately detect the OpenGL version when running with ANGLE on macOS.

If you intend to use Skia in an environment that does not rely on GLES (e.g., standard macOS OpenGL), you can override this default by passing
`skia_gl_standard` to `--override-build-args` with the desired value, for example, `--override-build-args="skia_gl_standard='gl'"` (for the default macOS OpenGL).

<br>

## License

This project is licensed under the terms of the [GNU Lesser General Public License v3.0](https://www.gnu.org/licenses/lgpl-3.0.html).

> **Note:**  
> This repository includes the full texts of both the GNU GPL v3.0 and the GNU LGPL v3.0. The GPL v3.0 serves as the base for the LGPL v3.0, but the applicable license for this project is **LGPL v3.0**. For more details, see the `COPYING` and `COPYING.LESSER` files.