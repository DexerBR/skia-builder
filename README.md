# skia-builder
#### Cross-platform tool for Skia environment setup and binary generation

<br>

## Supported platforms, architectures, and environments in `skia-builder`

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




#### Examples:

Automatically detects the OS and architecture and configures the main environment (Linux, Windows, macOS):

```
skia-builder setup-env
```

Does the same as the command above, and additionally configures the Android environment (only available on Windows):

```
skia-builder setup-env --sub-env=Android
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


***Important:*** The usage logic of `"` and `'` must be implemented exactly as shown in the example below.

```
skia-builder build --sub-env=Android --target-cpu=arm64 --custom-build-args="extra_cflags=['-g0'] is_debug=false is_component_build=false cc='clang' cxx='clang++' extra_cflags_cc=['-std=c++17'] ..." --archive
```

<br>

### General Notes
For macOS, we assume the built library will be used in an application that uses ANGLE as a GL provider. As a result, we force the `skia_gl_standard` setting to `"gles"`, since Skia cannot accurately detect the OpenGL version when running with ANGLE on macOS.

If you intend to use Skia in an environment that does not rely on GLES (e.g., standard macOS OpenGL), you can override this default by setting the `SKIABUILDER_SKIA_GL_STANDARD` environment variable. This lets you specify a different value for the `skia_gl_standard` argument, such as `"gl"` (for default macOS OpenGL).