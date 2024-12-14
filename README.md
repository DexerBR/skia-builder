# skia-builder


## Usage

```
skia-builder build --target-cpu=x64 --archive
skia-builder build --sub-env=Android --target-cpu=x64 --archive


skia-builder setup-env
skia-builder setup-env --sub-env=Android


skia-builder build --sub-env=Android --target-cpu=arm --custom-build-args="extra_cflags=['-g0'] is_debug=false is_component_build=false cc='clang' cxx='clang++' extra_cflags_cc=['-std=c++17'] ..."
```