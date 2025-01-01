# skia-builder


## Usage

```
skia-builder build --target-cpu=x64 --archive
skia-builder build --sub-env=Android --target-cpu=x64 --archive


skia-builder setup-env
skia-builder setup-env --sub-env=Android


skia-builder build --sub-env=Android --target-cpu=arm --custom-build-args="extra_cflags=['-g0'] is_debug=false is_component_build=false cc='clang' cxx='clang++' extra_cflags_cc=['-std=c++17'] ..."
```

For macOS, we assume the built library will be used in an application that uses ANGLE as a GL provider. As a result, we force the `skia_gl_standard` setting to `"gles"`, since Skia cannot accurately detect the OpenGL version when running with ANGLE on macOS.

If you intend to use Skia in an environment that does not rely on GLES (e.g., standard macOS OpenGL), you can override this default by setting the `SKIABUILDER_SKIA_GL_STANDARD` environment variable. This lets you specify a different value for the `skia_gl_standard` argument, such as `"gl"` (for default macOS OpenGL).