package(default_visibility = ["//visibility:public"])

# Main entry point
py_binary(
    name = "main",
    srcs = ["main.py"],
    main = "main.py",
    deps = [
        "//src/core:core",
    ],
)

# Configuration files
filegroup(
    name = "config_files",
    srcs = glob([
        "config/**/*",
        "data/**/*",
    ]),
    visibility = ["//visibility:public"],
)